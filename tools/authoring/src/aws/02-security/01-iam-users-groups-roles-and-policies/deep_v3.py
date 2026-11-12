from cloudkit import *

LADDER = ladder([
 ('IAM is like the security guard of a big office. Every person gets their own ID card, and a rule book says which rooms each card opens. If the rule book does not say “yes”, the door stays locked.',
  'Write down three “people” in a small shop (owner, cashier, helper) and what each should be able to do with the cash box (open, count, take out).',
  'If the rule book says nothing about a door, is it open or locked?', 'Locked. In AWS the default answer is always “no” (implicit deny).'),
 ('A <b>user</b> is a login for one person; a <b>group</b> is a team; a <b>policy</b> lists allowed actions; a <b>role</b> is a temporary badge for programs.',
  'Do Step 1 of the hands-on (read AmazonS3ReadOnlyAccess) and point to Effect, Action and Resource.',
  'Should you give each person their own user or share one?', 'Their own — so every action can be traced to a person and removed without affecting others.'),
 ('Write a customer managed policy scoped to one bucket folder; attach it to a group; prove allowed and denied actions with the Policy Simulator.',
  'Do Step 2 of the hands-on and change the folder to <code>finance/</code> — check the results flip.',
  'Which ARN does s3:ListBucket need — bucket or object?', 'The bucket ARN (arn:aws:s3:::name). Get/Put/DeleteObject need object ARNs (arn:aws:s3:::name/key).'),
 ('Combine identity and resource policies; use conditions (aws:SecureTransport, aws:MultiFactorAuthPresent, aws:SourceIp, tags); design roles for apps and cross-account access.',
  'Add a Deny statement to S3ReadMenu that blocks requests without MFA; test with the simulator’s context keys.',
  'Cross-account: Account B’s user has an Allow, but Account A’s bucket policy says nothing. Result?', 'Denied. Cross-account access needs an Allow on both sides (identity policy in B and resource policy in A).'),
 ('Design guard-rails at scale: permissions boundaries for delegated admins, SCPs and RCPs in Organizations, ABAC with tags, Access Analyzer unused-access findings, and Identity Center permission sets.',
  'Write an SCP that denies all actions outside ap-south-1 and ap-south-2 except global services, and explain the exceptions you needed.',
  'An SCP allows s3:*, the identity policy allows s3:GetObject, a boundary allows only ec2:*. Can the user read S3?', 'No. The effective permission is the intersection of SCP, boundary and identity policy; the boundary has no S3, so S3 is denied.')])

HOOD = under_hood('How IAM really evaluates a request — the full logic professionals use to debug AccessDenied.', [
 ('1 · The complete evaluation order (single account)',
  '<ol><li><b>Explicit Deny</b> in any applicable policy → denied. Stop.</li><li><b>Organizations SCPs / RCPs</b> (if the account is in an organisation): the action must be allowed by every SCP level and RCP; otherwise denied.</li><li><b>Resource-based policy</b> that allows the principal → can allow (same account).</li><li><b>Identity-based policy</b> must allow the action…</li><li>…and, if set, the <b>permissions boundary</b> must allow it too…</li><li>…and, for assumed-role sessions, any <b>session policy</b> must allow it.</li><li>Nothing allowed it → <b>implicit deny</b>.</li></ol><p>Effective permissions are therefore an <i>intersection</i> of guard-rails (SCP, boundary, session) with the <i>union</i> of grants (identity + resource policies).</p>'),
 ('2 · Guard-rails that only limit, never grant',
  table(['Guard-rail', 'Set on', 'Purpose'], [['Permissions boundary', 'a user or role', 'maximum permissions — lets a team lead create roles without escalating privilege'], ['Service control policy (SCP)', 'OU or account in Organizations', 'maximum for every principal in member accounts (not the management account)'], ['Resource control policy (RCP)', 'OU or account', 'maximum permissions on resources (e.g. S3, KMS) whoever calls'], ['Session policy', 'passed at AssumeRole', 'narrow a role for one session']], minw=560)),
 ('3 · What STS does when a role is assumed',
  '<p><code>sts:AssumeRole</code> checks the role’s <b>trust policy</b> (is this caller allowed?) and the caller’s own permission to call AssumeRole, then returns an <b>AccessKeyId (ASIA…)</b>, <b>SecretAccessKey</b>, <b>SessionToken</b> and <b>Expiration</b>. Default duration is 1 hour; a role can allow up to 12 hours. Role chaining (a role assuming another role) is limited to 1 hour. EC2 and Lambda call STS for you and refresh credentials before they expire.</p>'),
 ('4 · How the policy language matches',
  '<ul><li>Actions are case-insensitive, <code>service:Operation</code>; wildcards <code>*</code> and <code>?</code> allowed (<code>s3:Get*</code>).</li><li>Resources are ARNs; wildcards in the resource part.</li><li><code>NotAction</code> / <code>NotResource</code> invert the match — powerful and easy to misuse.</li><li>Policy variables: <code>${aws:username}</code> lets one policy give each user their own folder: <code>arn:aws:s3:::home/${aws:username}/*</code>.</li><li>Global condition keys: <code>aws:SourceIp</code>, <code>aws:MultiFactorAuthPresent</code>, <code>aws:SecureTransport</code>, <code>aws:PrincipalTag</code>, <code>aws:RequestedRegion</code>, <code>aws:PrincipalOrgID</code>.</li></ul>'),
 ('5 · Limits you will hit',
  table(['Item', 'Default limit'], [['Managed policies attached per user/group/role', '10 (can be raised to 20)'], ['Groups a user can belong to', '10'], ['Users per account', '5,000'], ['Managed policy size', '6,144 characters'], ['Inline policy size (user / group / role)', '2,048 / 5,120 / 10,240 characters'], ['Role session duration', '15 min – 12 h (default 1 h)']], minw=420) +
  '<p>IAM is <b>eventually consistent</b>: a new policy usually works within seconds — scripts should wait or retry (that is why the lab uses <code>sleep 10</code>).</p>'),
])

ROLES = by_role('IAM touches every role; here is what each one actually does with it.', [
 ('Software developer (backend)', 'Never handles keys; asks for precise permissions for the app.', 'Lambda execution roles, ECS task roles, EC2 instance profiles, SDK credential chain.', 'The order service needs sqs:SendMessage on one queue — request exactly that, scoped to the queue ARN.', 'Reading AccessDenied messages and asking for the exact action/ARN.'),
 ('App / mobile developer', 'End users never get IAM users.', 'Amazon Cognito identity pools → temporary IAM roles for app users; pre-signed URLs.', 'Each app user may upload only to <code>uploads/${cognito-identity.amazonaws.com:sub}/*</code>.', 'Policy variables, Cognito, pre-signed URLs.'),
 ('Data analyst', 'Gets read access to curated data only.', 'Group/permission set with Athena + read on curated S3 prefixes or Lake Formation grants.', 'Can query sales_curated, cannot see raw customer PII.', 'Understanding why a query fails with AccessDenied on S3 vs Glue catalog.'),
 ('Data engineer', 'Builds pipelines that run as roles.', 'Glue job roles, EMR roles, Lake Formation permissions, cross-account data sharing roles.', 'Glue job role: read raw/, write curated/, decrypt with one KMS key — nothing else.', 'Prefix-scoped S3 policies, KMS key policies, cross-account roles.'),
 ('ML / AI engineer', 'Notebooks and endpoints run as execution roles.', 'SageMaker execution roles, Bedrock model access, S3 dataset prefixes.', 'Notebook role may read training-data/ and invoke one Bedrock model; cannot read HR data.', 'Scoping data access; separating training vs inference roles.'),
 ('DevOps / cloud engineer', 'Owns identity design.', 'Identity Center permission sets, CI/CD roles via OIDC (no keys in GitHub), boundaries, SCPs.', 'GitHub Actions deploys with a role trusted through OIDC; no long-term key exists anywhere.', 'Trust policies, OIDC federation, guard-rails.'),
 ('Security engineer', 'Audits and tightens.', 'IAM Access Analyzer (external + unused access), credential reports, CloudTrail, policy validation.', 'Monthly: remove permissions unused for 90 days; flag any role trusted by an unknown account.', 'Evaluation logic, Access Analyzer, least-privilege reviews.')])

DOMAINS = by_domain('IAM rules are where regulators look first.', [
 ('Banking / fintech', 'payment systems, core banking add-ons', 'Identity Center + MFA, maker-checker via separate roles, break-glass role with alerts, SCPs', 'RBI: access reviews, segregation of duties, audit trails'),
 ('Healthcare', 'patient records', 'roles per function (doctor app, billing), ABAC on department tags, strict S3/KMS policies', 'DPDP/ABDM: access only on need-to-know; log every access'),
 ('Retail / e-commerce', 'orders, catalogue, payments', 'app roles per microservice, Cognito for customers, no human access to card data', 'PCI DSS: least privilege, quarterly access reviews'),
 ('Education', 'students, faculty, labs', 'groups: Faculty (upload notes), Students (read), Accountants; sandbox accounts per batch', 'student data under DPDP; one action to add a faculty member'),
 ('Manufacturing / IoT', 'devices and plants', 'IoT certificates + policies per device, roles for edge gateways', 'compromised device must not reach other plants'),
 ('Government', 'citizen services', 'federation with government identity providers, strict SCPs', 'MeitY/CERT-In logging and access control')])

PRO = (
 '  <h3>IAM commands professionals use</h3>\n' + cheatsheet([
   ('aws iam simulate-principal-policy --policy-source-arn USER_OR_ROLE_ARN --action-names s3:GetObject --resource-arns ARN', 'would it be allowed? (and why not)'),
   ('aws iam get-account-authorization-details --filter User Role Group > iam.json', 'export every identity and policy for review'),
   ('aws iam generate-service-last-accessed-details --arn ROLE_ARN', 'which services a role really used (to trim permissions)'),
   ('aws accessanalyzer validate-policy --policy-type IDENTITY_POLICY --policy-document file://p.json', 'lint a policy before deploying'),
   ('aws iam list-attached-group-policies --group-name Interns', 'what a group gets'),
   ('aws sts decode-authorization-message --encoded-message MSG', 'decode an EC2 “Encoded authorization failure” message'),
   ('aws iam get-credential-report --query Content --output text | base64 -d', 'all users, MFA status, key ages')]) +
 '  <h3>AccessDenied messages, decoded</h3>\n' + errors_table([
   ('User: arn:aws:iam::111122223333:user/intern-kabir is not authorized to perform: s3:DeleteObject on resource: … because no identity-based policy allows the s3:DeleteObject action', 'any denied call', 'no Allow (implicit deny); the message now names the policy type that is missing', 'add the action to the right policy — or accept that it should be denied'),
   ('… with an explicit deny in a service control policy', 'org accounts', 'an SCP denies it (e.g. Region or service restriction)', 'ask the organisation admin; the identity policy cannot override it'),
   ('… with an explicit deny in an identity-based policy / resource-based policy', 'policies with Deny statements', 'a Deny (often a Condition like no MFA / not HTTPS)', 'meet the condition (MFA, HTTPS) or fix the Deny'),
   ('An error occurred (AccessDenied) when calling the AssumeRole operation: User … is not authorized to perform: sts:AssumeRole on resource: …', 'assuming a role', 'trust policy does not include the caller, or caller lacks sts:AssumeRole', 'fix the role trust policy Principal; grant sts:AssumeRole'),
   ('MalformedPolicyDocument: Policy document should not specify a principal.', 'creating an identity policy', 'Principal is only for resource-based/trust policies', 'remove Principal from identity policies'),
   ('LimitExceeded: Cannot exceed quota for PoliciesPerGroup: 10', 'attaching many policies', 'managed policy attachment limit', 'merge policies or request an increase')]) +
 checklist('IAM production checklist', ['No IAM users with access keys older than 90 days (or none at all).', 'People via Identity Center or users-in-groups with MFA.', 'Apps use roles; no keys in code, images or CI variables (use OIDC).', 'Customer managed policies scoped to exact ARNs; validated with Access Analyzer.', 'Explicit Deny for dangerous patterns (non-HTTPS, Regions, disabling CloudTrail).', 'Quarterly review with last-accessed data; unused permissions removed.']) +
 refs([('IAM user guide', 'https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html'), ('Policy evaluation logic', 'https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html'), ('IAM JSON policy elements', 'https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements.html'), ('IAM quotas', 'https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_iam-quotas.html')])
)

PROJ = projects([
 ('Basic', 'Access plan for a coaching institute', 'An institute has an owner, 4 faculty, 2 accountants and 1 auditor sharing one AWS login.',
  ['List each person and what they must do (upload notes, read invoices, view everything).', 'Design groups (Owners, Faculty, Accountants, Auditors) and which AWS managed or custom policy each gets.', 'Explain how a new faculty member is added in one action.', 'Explain what changes for the shared login.'],
  'A table of groups → policies → members, and five sentences on why.', 'Add MFA enforcement with a Deny-without-MFA statement.'),
 ('Intermediate', 'Folder-level permissions with proof', 'Faculty may upload to <code>notes/</code>; students’ <code>submissions/</code> must be invisible to them.',
  ['Create a bucket with notes/ and submissions/.', 'Write a customer managed policy for Faculty (ListBucket with s3:prefix notes/*, PutObject/GetObject on notes/*).', 'Create the Faculty group and two users.', 'Prove with the Policy Simulator: PutObject notes/ allowed; GetObject submissions/ denied; DeleteObject notes/ denied (if you chose so).'],
  'The policy JSON, simulator output for 4 actions, and a screenshot of a console upload as a faculty user.', 'Use ${aws:username} to give each faculty member a private drafts/ folder.'),
 ('Advanced', 'Cross-account auditor role', 'An external auditor (another AWS account) must read logs in your account for one month, with MFA.',
  ['Create role AuditorRead with ReadOnlyAccess (or narrower) and a trust policy naming the auditor’s account, requiring aws:MultiFactorAuthPresent and an ExternalId.', 'Limit max session duration to 1 hour.', 'From a second account (or a classmate’s), assume the role and list logs.', 'Show the AssumeRole event in your CloudTrail.'],
  'Trust policy, permission policy, the CloudTrail event, and a removal plan for when the audit ends.', 'Add a permissions boundary so even an admin cannot widen AuditorRead beyond read-only.')])

SIMD = awsfig('IAM lab map: a bucket with menu and finance folders; customer managed policy S3ReadMenu; Interns group; user intern-kabir; MenuReader role; simulator results allow and deny.',
    grp('acct', 10, 10, 620, 200, 'AWS account {acct} — IAM is global', k='acct') +
    svc(80, 40, 'file', 'S3ReadMenu', 'customer managed', 'green', k='pol', w=88) +
    svc(80, 130, 'role', 'Interns', 'group', 'violet', k='grp') +
    svc(200, 130, 'user', 'intern-kabir', 'IAM user', 'blue', k='user', w=80) +
    link(80, 94, 80, 128, k='attach', label='attached') + link(122, 156, 158, 156, k='member', label='member') +
    svc(200, 40, 'role', 'MenuReader', 'role · 1 h creds', 'amber', k='role', w=86) + link(126, 66, 156, 66, k='rattach') +
    grp('region', 290, 26, 200, 170, 'S3 · iam-lab-{acct}', k='bucket') +
    svc(345, 70, 'folder', 'menu/', 'm.txt', 'green', k='menu') + svc(440, 70, 'folder', 'finance/', 'f.txt', 'red', k='fin') +
    svc(390, 140, 'clock', 'CloudTrail', 'every call', 'card', k='trail', w=80) +
    svc(565, 50, 'shield', 'ALLOW', 'GetObject menu/', 'green', k='allow', w=86) + svc(565, 130, 'shield', 'DENY', 'finance/, Delete', 'red', k='deny', w=86), h=222)

SIM = simlab(dict(title='IAM lab: least privilege for an intern', intro='Create the policy, group and user, then prove what the intern can and cannot do. Every step works in the Console or CloudShell tab.',
  diagram=SIMD, lit=['acct', 'bucket', 'menu', 'fin'],
  steps=[
   dict(title='Read an AWS managed policy', goal='Show the JSON of <code>AmazonS3ReadOnlyAccess</code>.', hint='<code>aws iam get-policy-version --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess --version-id v3</code> (find the version with get-policy).',
        answer='aws iam get-policy-version --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess --version-id v3',
        cli=[dict(re=r'^aws iam get-policy-version --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess --version-id v\d+( --query .*)?$', out='{\n    "PolicyVersion": {\n        "Document": {\n            "Version": "2012-10-17",\n            "Statement": [{\n                "Effect": "Allow",\n                "Action": ["s3:Get*", "s3:List*", "s3:Describe*", "s3-object-lambda:Get*", "s3-object-lambda:List*"],\n                "Resource": "*"\n            }]\n        },\n        "VersionId": "v3",\n        "IsDefaultVersion": true\n    }\n}')],
        errors=[dict(re=r'^aws iam get-policy --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess', out='{\n    "Policy": {\n        "PolicyName": "AmazonS3ReadOnlyAccess",\n        "DefaultVersionId": "v3",\n        "AttachmentCount": 0\n    }\n}\n(Now fetch version v3 with get-policy-version.)', ok=True),
                dict(re=r'arn:aws:iam::\d{12}:policy/AmazonS3ReadOnlyAccess', out='An error occurred (NoSuchEntity): Policy … does not exist.\n→ AWS managed policies live under account “aws”: arn:aws:iam::aws:policy/…')],
        console=dict(crumbs='IAM › Policies › AmazonS3ReadOnlyAccess › Permissions', fields=[dict(label='View as', type='select', options=['Visual', 'JSON'], re=r'^JSON$', why='Switch to JSON to read the statement.')], button='Show', out='Effect Allow · Action s3:Get*, s3:List*, … · Resource *'),
        lights=[], explain='Every AWS policy has the same shape: Version, Statement[Effect, Action, Resource, optional Condition]. This one allows reading <b>every</b> bucket (<code>Resource: *</code>) — too broad for an intern.'),
   dict(title='Create policy S3ReadMenu', goal='Create a customer managed policy <code>S3ReadMenu</code> allowing GetObject only on <code>iam-lab-{acct}/menu/*</code>.', hint='<code>aws iam create-policy --policy-name S3ReadMenu --policy-document file://s3readmenu.json</code>', answer='aws iam create-policy --policy-name S3ReadMenu --policy-document file://s3readmenu.json',
        cli=[dict(re=r'^aws iam create-policy --policy-name S3ReadMenu --policy-document file://\S+\.json( --query .*)?( --output \w+)?$', out='{\n    "Policy": {\n        "PolicyName": "S3ReadMenu",\n        "Arn": "arn:aws:iam::{acct}:policy/S3ReadMenu",\n        "DefaultVersionId": "v1",\n        "AttachmentCount": 0\n    }\n}')],
        errors=[dict(re=r'^aws iam create-policy --policy-name S3ReadMenu --policy-document \{', out='Tip: inline JSON on the command line needs careful quoting. Save it to s3readmenu.json and use file://s3readmenu.json.', ok=True)],
        console=dict(crumbs='IAM › Policies › Create policy › JSON', fields=[dict(label='Action', type='select', options=['s3:*', 's3:GetObject', 's3:DeleteObject'], re=r'^s3:GetObject$', why='Least privilege: only s3:GetObject.'), dict(label='Resource ARN', ph='arn:aws:s3:::iam-lab-{acct}/menu/*', re=r'^arn:aws:s3:::iam-lab-{acct}/menu/\*$', why='Object ARN for the menu folder: arn:aws:s3:::iam-lab-{acct}/menu/*'), dict(label='Policy name', ph='S3ReadMenu', re=r'^S3ReadMenu$', why='Name it S3ReadMenu.')], button='Create policy', out='Policy S3ReadMenu created'),
        lights=['pol'], explain='A customer managed policy is a standalone, versioned JSON document in your account. It does nothing until attached to a user, group or role.'),
   dict(title='Group Interns + user intern-kabir', goal='Create group <code>Interns</code>, attach S3ReadMenu, and add user <code>intern-kabir</code>.', hint='create-group, attach-group-policy, create-user, add-user-to-group. In the simulator, the add-user-to-group command completes the step.', answer='aws iam add-user-to-group --group-name Interns --user-name intern-kabir',
        cli=[dict(re=r'^aws iam add-user-to-group --group-name Interns --user-name intern-kabir$', out='')],
        errors=[dict(re=r'^aws iam create-group --group-name Interns$', out='{ "Group": { "GroupName": "Interns", "Arn": "arn:aws:iam::{acct}:group/Interns" } }', ok=True),
                dict(re=r'^aws iam attach-group-policy --group-name Interns --policy-arn arn:aws:iam::{acct}:policy/S3ReadMenu$', out='(attached)', ok=True),
                dict(re=r'^aws iam create-user --user-name intern-kabir$', out='{ "User": { "UserName": "intern-kabir", "Arn": "arn:aws:iam::{acct}:user/intern-kabir" } }', ok=True),
                dict(re=r'^aws iam attach-user-policy', out='Works — but attach policies to groups, not users. Use attach-group-policy on Interns.')],
        console=dict(crumbs='IAM › User groups › Create user group', fields=[dict(label='User group name', ph='Interns', re=r'^Interns$', why='Name the group Interns.'), dict(label='Attach permissions policies', type='select', options=['AdministratorAccess', 'AmazonS3ReadOnlyAccess', 'S3ReadMenu'], re=r'^S3ReadMenu$', why='Least privilege: attach S3ReadMenu, not a broad policy.'), dict(label='Add users', ph='intern-kabir', re=r'^intern-kabir$', why='Add intern-kabir.')], button='Create user group', out='Group Interns created with S3ReadMenu; intern-kabir added'),
        lights=['grp', 'user', 'attach', 'member'], explain='intern-kabir has no policy of his own; he inherits S3ReadMenu through Interns. Next year’s intern? Add them to the group — one action.'),
   dict(title='Prove allowed and denied', goal='Use the Policy Simulator to test <code>s3:GetObject</code> on <code>finance/f.txt</code> for intern-kabir.', hint='<code>aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::{acct}:user/intern-kabir --action-names s3:GetObject --resource-arns arn:aws:s3:::iam-lab-{acct}/finance/f.txt</code>',
        answer='aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::{acct}:user/intern-kabir --action-names s3:GetObject --resource-arns arn:aws:s3:::iam-lab-{acct}/finance/f.txt',
        cli=[dict(re=r'^aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::{acct}:user/intern-kabir --action-names s3:GetObject --resource-arns arn:aws:s3:::iam-lab-{acct}/finance/\S+( --query .*)?( --output \w+)?$', out='s3:GetObject   arn:aws:s3:::iam-lab-{acct}/finance/f.txt   implicitDeny')],
        errors=[dict(re=r'^aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::{acct}:user/intern-kabir --action-names s3:GetObject --resource-arns arn:aws:s3:::iam-lab-{acct}/menu/\S+', out='s3:GetObject   arn:aws:s3:::iam-lab-{acct}/menu/m.txt   allowed\n(Allowed side proven. Now test finance/f.txt to prove the deny side.)', ok=True),
                dict(re=r'^aws iam simulate-principal-policy .*--action-names s3:DeleteObject', out='s3:DeleteObject   …/menu/m.txt   implicitDeny\n(Also denied — good. Now test GetObject on finance/f.txt.)', ok=True)],
        console=dict(crumbs='IAM › Users › intern-kabir › Simulate (Policy Simulator)', fields=[dict(label='Action', type='select', options=['s3:GetObject', 's3:DeleteObject'], re=r'^s3:GetObject$', why='Test s3:GetObject.'), dict(label='Resource', ph='arn:aws:s3:::iam-lab-{acct}/finance/f.txt', re=r'^arn:aws:s3:::iam-lab-{acct}/finance/f\.txt$', why='Test the finance file: arn:aws:s3:::iam-lab-{acct}/finance/f.txt')], button='Run simulation', out='s3:GetObject on finance/f.txt → implicitDeny'),
        lights=['deny', 'allow', 'fin', 'menu'], explain='The simulator ran the real evaluation: GetObject on menu/ is <b>allowed</b> (S3ReadMenu matches), on finance/ it is an <b>implicit deny</b> (nothing allows it). That is your proof of both sides — exactly what lab exams ask.'),
   dict(title='Assume a role', goal='Assume role <code>MenuReader</code> (already created with S3ReadMenu) and get temporary credentials.', hint='<code>aws sts assume-role --role-arn arn:aws:iam::{acct}:role/MenuReader --role-session-name lab</code>', answer='aws sts assume-role --role-arn arn:aws:iam::{acct}:role/MenuReader --role-session-name lab',
        cli=[dict(re=r'^aws sts assume-role --role-arn arn:aws:iam::{acct}:role/MenuReader --role-session-name [\w+=,.@-]+( --query .*)?( --output \w+)?$', out='{\n    "Credentials": {\n        "AccessKeyId": "ASIA5EXAMPLE{rnd}",\n        "SecretAccessKey": "wJalr…",\n        "SessionToken": "IQoJb3JpZ2luX2Vj…",\n        "Expiration": "2026-11-12T11:15:00+00:00"\n    },\n    "AssumedRoleUser": {\n        "Arn": "arn:aws:sts::{acct}:assumed-role/MenuReader/lab"\n    }\n}')],
        errors=[dict(re=r'^aws sts assume-role --role-arn arn:aws:iam::{acct}:role/MenuReader$', out='aws: error: the following arguments are required: --role-session-name\n→ Name the session, e.g. --role-session-name lab (it appears in CloudTrail).')],
        console=dict(crumbs='Account menu › Switch role', fields=[dict(label='Account', ph='{acct}', re=r'^{acct}$', why='Enter your account ID {acct}.'), dict(label='IAM role name', ph='MenuReader', re=r'^MenuReader$', why='Role name: MenuReader')], button='Switch role', out='Now acting as MenuReader @ {acct} (1 hour)'),
        lights=['role', 'rattach', 'trail'], explain='STS checked the role’s <b>trust policy</b> (your account may assume it), then issued temporary keys starting with <b>ASIA</b> plus a session token, valid for one hour. CloudTrail records the AssumeRole call and every action taken with the session.'),
  ]))
