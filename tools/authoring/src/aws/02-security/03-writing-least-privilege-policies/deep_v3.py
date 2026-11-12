from cloudkit import *

LADDER = ladder([
 ('Least privilege means giving people only what their job needs — like a house-sitter who may water plants but not open your cupboard.',
  'Write a “house-sitter rule” for your home in five lines: who, may do what, where, when, never.',
  'Is it safer to give “all access, just in case”?', 'No — extra access turns small mistakes or stolen passwords into big losses.'),
 ('A policy lists actions (upload, read) on resources (one folder) — no wildcards like s3:*.',
  'Read the FacultyNotes policy in the Deep dive and mark each answer to the five questions.',
  'Which part of the policy says “which folder”?', 'The Resource (an ARN such as arn:aws:s3:::edu-content/notes/*).'),
 ('Write prefix-scoped S3 policies, validate with Access Analyzer, prove four actions with the simulator.',
  'Do the hands-on Steps 1–2 (or the simulator).',
  'What is the difference between implicitDeny and explicitDeny?', 'implicitDeny: nothing allowed it; explicitDeny: a Deny statement matched — no Allow can override it.'),
 ('Use conditions (MFA, HTTPS, IP, Region), policy variables and explicit Deny guard-rails; understand NotAction risks.',
  'Add an MFA-required Deny for uploads and test with the simulator’s context key aws:MultiFactorAuthPresent.',
  'Why does aws:SourceIp fail for traffic through a VPC endpoint?', 'Requests via VPC endpoints carry private addresses; use aws:SourceVpce/aws:SourceVpc instead.'),
 ('Scale with ABAC, permission sets, SCP/RCP guard-rails, automated policy checks in CI and unused-access reviews.',
  'Write a custom policy check (Access Analyzer CheckNoNewAccess) that fails if a policy change adds s3:DeleteObject.',
  'A team keeps re-tagging resources to gain access under ABAC. Fix?', 'Deny changing the controlling tag (aws:TagKeys / ResourceTag conditions) except for an admin role.')])

HOOD = under_hood('Details that decide whether a policy really does what you think.', [
 ('1 · How conditions are combined',
  '<ul><li>Multiple <b>keys</b> in one Condition block → all must match (AND).</li><li>Multiple <b>values</b> for one key → any can match (OR).</li><li>Multiple <b>operators</b> → AND.</li><li>A missing key makes most operators false — use <code>…IfExists</code> when a key may be absent (e.g. MFA for CLI calls).</li><li>Multi-valued keys (tag lists) need <code>ForAnyValue:</code> or <code>ForAllValues:</code>.</li></ul>'),
 ('2 · NotAction and NotResource traps',
  '<p><code>"Effect": "Allow", "NotAction": "iam:*"</code> allows <i>everything except IAM</i> — including deleting databases. Use NotAction mostly with <b>Deny</b>: “Deny NotAction [list of allowed services]” builds a service allow-list. Always simulate both a forbidden and an allowed action.</p>'),
 ('3 · The S3 permission families',
  table(['Family', 'Examples', 'Resource'], [['Bucket', 'ListBucket, GetBucketPolicy, PutBucketVersioning', 'arn:aws:s3:::bucket'], ['Object', 'GetObject, PutObject, DeleteObject', 'arn:aws:s3:::bucket/key'], ['Object versions', 'GetObjectVersion, DeleteObjectVersion', 'arn:aws:s3:::bucket/key'], ['Account', 'ListAllMyBuckets, GetAccountPublicAccessBlock', '*']], minw=520) +
  '<p>Versioned buckets: “never delete” must deny <code>s3:DeleteObject</code> <b>and</b> <code>s3:DeleteObjectVersion</code>; recovering a deleted file needs DeleteObject on the delete marker version or a copy of an older version.</p>'),
 ('4 · Where least privilege is enforced besides IAM',
  '<ul><li><b>Bucket policies</b> (resource side): HTTPS-only, VPC-only, organisation-only.</li><li><b>KMS key policies</b>: who may encrypt/decrypt with each key (Lesson 2.4).</li><li><b>S3 Block Public Access</b>: account/bucket guard against public policies and ACLs.</li><li><b>SCPs/RCPs</b>: organisation-wide maximums.</li><li><b>Permissions boundaries</b>: let teams create roles safely.</li></ul>'),
 ('5 · Size and readability',
  '<p>Managed policies are limited to 6,144 characters (whitespace excluded); split by purpose, use <code>Sid</code>s, and keep one statement per idea. Readable policies are reviewable policies.</p>'),
])

ROLES = by_role('Least privilege looks different from each desk.', [
 ('Software developer (backend)', 'Requests precise permissions for each service the app calls.', 'IAM policies in IaC next to the code; AccessDenied messages; simulator.', 'Order service: dynamodb:PutItem on Orders, sqs:SendMessage on one queue — written in the same pull request as the feature.', 'Translating code calls into actions and ARNs.'),
 ('App / mobile developer', 'Scopes end users to their own data.', 'Cognito identity pools with ${cognito-identity.amazonaws.com:sub} prefixes; pre-signed URLs.', 'Each user uploads only to uploads/&lt;their-id&gt;/.', 'Policy variables for app users.'),
 ('Data analyst', 'Read only the datasets needed.', 'Lake Formation column/row-level permissions; S3 prefix read; Athena workgroups.', 'Analyst sees sales_curated but not customer phone numbers.', 'Requesting dataset-level access.'),
 ('Data engineer', 'Pipelines with minimum reach.', 'Glue job role per pipeline; prefix-scoped S3; KMS key grants.', 'Ingest job: write raw/2026/*; transform job: read raw/, write curated/.', 'Per-stage roles; avoiding s3:* in ETL roles.'),
 ('ML / AI engineer', 'Separate training data and model access.', 'SageMaker execution roles scoped to datasets/ and models/; Bedrock model-level permissions.', 'Fine-tuning job cannot read the HR bucket even if a path is mistyped.', 'Scoping data and model access.'),
 ('DevOps / cloud engineer', 'Owns policy templates and guard-rails.', 'Permission sets, boundaries, SCPs, policy checks in CI.', 'PR fails automatically if a policy adds iam:* or s3:Delete* without approval.', 'Policy-as-code.'),
 ('Security engineer', 'Measures and shrinks privilege.', 'Access Analyzer unused access, last accessed, external access findings.', 'Quarterly report: 30% of permissions unused → removed.', 'Least-privilege metrics.')])

DOMAINS = by_domain('Least privilege requirements by industry.', [
 ('Banking / fintech', 'payments, loan data', 'separate read/approve roles (maker-checker), Deny without MFA, data perimeter conditions', 'RBI: segregation of duties, periodic access review'),
 ('Healthcare', 'patient data', 'ABAC by department/ward tags; explicit Deny on export locations', 'DPDP/ABDM: need-to-know access'),
 ('Retail / e-commerce', 'orders, payments', 'per-service roles, no human write access to production data', 'PCI DSS: restrict access to cardholder data by need'),
 ('Education', 'notes, submissions, grades', 'faculty: notes/ only; accountants: fees/ only; auditors: read-only; Deny on submissions for staff roles', 'student privacy; proof of access in audits'),
 ('Media', 'unreleased content', 'prefix per project, time-bound conditions for embargoed content', 'contractual embargoes'),
 ('Government', 'citizen records', 'role-based + ABAC, MFA everywhere, Region restrictions', 'MeitY/CERT-In controls')])

PRO = (
 '  <h3>Policy toolbox commands</h3>\n' + cheatsheet([
   ('aws accessanalyzer validate-policy --policy-type IDENTITY_POLICY --policy-document file://p.json', 'lint a policy'),
   ('aws accessanalyzer check-no-new-access --existing-policy-document file://old.json --new-policy-document file://new.json --policy-type IDENTITY_POLICY', 'block changes that widen access'),
   ('aws accessanalyzer start-policy-generation --policy-generation-details principalArn=ROLE_ARN --cloud-trail-details …', 'generate a policy from real activity'),
   ('aws iam simulate-custom-policy --policy-input-list file://p.json --action-names s3:GetObject --resource-arns ARN', 'simulate a policy before attaching it'),
   ('aws iam generate-service-last-accessed-details --arn ARN; aws iam get-service-last-accessed-details --job-id …', 'what is really used'),
   ('aws iam get-policy-version --policy-arn ARN --version-id v1', 'read a managed policy')]) +
 '  <h3>Errors you will see while tightening</h3>\n' + errors_table([
   ('An error occurred (AccessDenied) when calling the ListObjectsV2 operation … no identity-based policy allows the s3:ListBucket action', 'listing a folder', 'ListBucket missing or on the wrong ARN / prefix', 'ListBucket on the bucket ARN with an s3:prefix condition'),
   ('You don’t have permissions to list buckets (console)', 'console users', 'ListAllMyBuckets missing', 'add s3:ListAllMyBuckets and s3:GetBucketLocation on *'),
   ('MalformedPolicyDocument: Policy has invalid action', 'creating a policy', 'typo in an action name', 'validate-policy; check the Service Authorization Reference'),
   ('MalformedPolicyDocument: Resource … must be in ARN format or "*"', 'creating a policy', 'bucket name without arn:aws:s3:::', 'use full ARNs'),
   ('… with an explicit deny in an identity-based policy', 'after adding guard-rails', 'a Deny (e.g. HTTPS/MFA) matched', 'meet the condition or narrow the Deny')]) +
 checklist('Least-privilege checklist for any policy', ['Requirement written as a plain sentence and five answers.', 'No service:* and no "Resource": "*" except for actions that require it.', 'Bucket vs object ARNs correct; prefixes scoped.', 'Must-never rules as explicit Deny (incl. DeleteObjectVersion for versioned buckets).', 'Validated with Access Analyzer; simulated allow and deny.', 'Attached to a group/role, never directly to users.', 'Reviewed quarterly with last-accessed data.']) +
 refs([('Security best practices in IAM — least privilege', 'https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html'), ('IAM condition operators', 'https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_condition_operators.html'), ('Policy variables', 'https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_variables.html'), ('IAM Access Analyzer', 'https://docs.aws.amazon.com/IAM/latest/UserGuide/what-is-access-analyzer.html')])
)

PROJ = projects([
 ('Basic', 'Five-question worksheet', 'Turn three business sentences into policies.',
  ['“Accountants may upload and view fee receipts.”', '“The auditor may view everything in the finance bucket but change nothing.”', '“The web server may read images and write access logs.”', 'For each: answer the five questions, then write the JSON.'],
  'Three worksheets + three policies validated with Access Analyzer.', 'Add an HTTPS-only Deny to each.'),
 ('Intermediate', 'Prove the accountant policy (CityBite-style)', 'Accountant may upload and view sales files but never open backups or delete anything.',
  ['Bucket with sales/ and backups/.', 'Policy: ListBucket (prefix sales/), Get/PutObject on sales/*, Deny backups/*, Deny s3:Delete*.', 'Group Accountants + user.', 'Simulate five actions and record allowed/implicitDeny/explicitDeny.'],
  'Policy, simulator table, and one console screenshot as the accountant.', 'Add versioning and make sure DeleteObjectVersion is denied too.'),
 ('Advanced', 'Policy-as-code gate', 'Your team wants pull requests to fail if a policy widens access.',
  ['Store policies as JSON in Git.', 'Write a script that runs validate-policy and check-no-new-access against the previous version.', 'Run it on a change that adds s3:DeleteObject — it must fail.', 'Document how to approve a legitimate widening.'],
  'Script, two runs (pass/fail) and a short README.', 'Wire it into GitHub Actions using an OIDC role (no keys).')])

SIMD = awsfig('Lab map: bucket edu-content with notes, drafts and submissions; FacultyNotes policy validated; Faculty group with meena and arjun; simulator results.',
    grp('acct', 10, 10, 620, 210, 'AWS account {acct}', k='acct') +
    svc(80, 46, 'file', 'FacultyNotes', 'policy JSON', 'green', k='pol', w=88) + svc(80, 140, 'shield', 'Validated', 'Access Analyzer', 'violet', k='val', w=88) + link(80, 100, 80, 138, k='vl') +
    svc(200, 46, 'role', 'Faculty', 'group', 'violet', k='grp') + link(124, 72, 164, 72, k='att') +
    svc(200, 140, 'user', 'meena · arjun', 'members', 'blue', k='users', w=86) + link(200, 100, 200, 138, k='mem') +
    grp('region', 280, 26, 200, 180, 'S3 · edu-content', k='bucket') +
    svc(330, 66, 'folder', 'notes/', 'read · upload', 'green', k='notes') + svc(430, 66, 'folder', 'drafts/', '${aws:username}', 'amber', k='drafts', w=76) + svc(380, 146, 'folder', 'submissions/', 'explicit Deny', 'red', k='subs', w=86) +
    svc(560, 50, 'shield', 'allowed', 'Put notes/', 'green', k='a1', w=80) + svc(560, 130, 'shield', 'denied', 'submissions/, delete', 'red', k='d1', w=86), h=230)

SIM = simlab(dict(title='Write and prove the faculty policy', intro='Validate the policy, create the group, then prove allowed, explicitly denied and implicitly denied actions.',
  diagram=SIMD, lit=['acct', 'bucket', 'notes', 'drafts', 'subs'],
  steps=[
   dict(title='Catch a typo before deploying', goal='Validate <code>bad.json</code> (it contains <code>s3:GetObjects</code>) with Access Analyzer.', hint='<code>aws accessanalyzer validate-policy --policy-type IDENTITY_POLICY --policy-document file://bad.json</code>', answer='aws accessanalyzer validate-policy --policy-type IDENTITY_POLICY --policy-document file://bad.json',
        cli=[dict(re=r'^aws accessanalyzer validate-policy --policy-type IDENTITY_POLICY --policy-document file://bad\.json( --query .*)?( --output \w+)?$', out='{\n    "findings": [{\n        "findingType": "ERROR",\n        "issueCode": "INVALID_ACTION",\n        "findingDetails": "The action s3:GetObjects does not exist.",\n        "locations": [{"path": [{"value": "Statement"}, {"index": 2}, {"value": "Action"}, {"index": 0}]}]\n    }]\n}')],
        errors=[dict(re=r'^aws accessanalyzer validate-policy --policy-type IDENTITY_POLICY --policy-document file://faculty\.json', out='{ "findings": [] }\n(The good policy is clean. Now validate bad.json to see a caught mistake.)', ok=True)],
        console=dict(crumbs='IAM › Policies › Create policy › JSON editor', fields=[dict(label='Validation panel shows', type='select', options=['0 errors', '1 error: INVALID_ACTION s3:GetObjects'], re=r'^1 error', why='Look for the ERROR finding the typo causes.')], button='Review', out='ERROR · INVALID_ACTION · s3:GetObjects does not exist'),
        lights=['val', 'vl'], explain='Access Analyzer parsed the policy grammar and checked every action against the service reference. A typo would have meant “nobody can read notes” in production — caught in one second.'),
   dict(title='Create FacultyNotes', goal='Create the customer managed policy <code>FacultyNotes</code> from <code>faculty.json</code>.', hint='<code>aws iam create-policy --policy-name FacultyNotes --policy-document file://faculty.json</code>', answer='aws iam create-policy --policy-name FacultyNotes --policy-document file://faculty.json',
        cli=[dict(re=r'^aws iam create-policy --policy-name FacultyNotes --policy-document file://faculty\.json( --query .*)?( --output \w+)?$', out='{ "Policy": { "PolicyName": "FacultyNotes", "Arn": "arn:aws:iam::{acct}:policy/FacultyNotes", "DefaultVersionId": "v1" } }')],
        errors=[dict(re=r'^aws iam create-policy --policy-name FacultyNotes --policy-document file://bad\.json', out='An error occurred (MalformedPolicyDocument) when calling the CreatePolicy operation: Policy has invalid action\n→ Fix the typo; use faculty.json.')],
        console=dict(crumbs='IAM › Policies › Create policy', fields=[dict(label='Policy name', ph='FacultyNotes', re=r'^FacultyNotes$', why='Name it FacultyNotes.'), dict(label='Statements include Deny submissions/*', type='check', must=True, why='The never-rule must be present.')], button='Create policy', out='FacultyNotes created (v1)'),
        lights=['pol'], explain='Four statements: console listing, ListBucket with s3:prefix (notes/, own drafts), Get/Put on notes/ and drafts/${aws:username}/, and an explicit Deny on submissions/*.'),
   dict(title='Faculty group with two members', goal='Create group <code>Faculty</code>, attach FacultyNotes, add <code>meena</code> and <code>arjun</code>.', hint='create-group, attach-group-policy, then add-user-to-group for both users. Adding arjun completes the step.', answer='aws iam add-user-to-group --group-name Faculty --user-name arjun',
        cli=[dict(re=r'^aws iam add-user-to-group --group-name Faculty --user-name arjun$', out='')],
        errors=[dict(re=r'^aws iam (create-group --group-name Faculty|attach-group-policy --group-name Faculty --policy-arn arn:aws:iam::{acct}:policy/FacultyNotes|add-user-to-group --group-name Faculty --user-name meena|create-user --user-name (meena|arjun))$', out='(done)', ok=True)],
        console=dict(crumbs='IAM › User groups › Create user group', fields=[dict(label='Group name', ph='Faculty', re=r'^Faculty$', why='Name it Faculty.'), dict(label='Policy', type='select', options=['AmazonS3FullAccess', 'FacultyNotes'], re=r'^FacultyNotes$', why='Attach FacultyNotes, not full access.'), dict(label='Users (comma-separated)', ph='meena, arjun', re=r'^\s*meena\s*,\s*arjun\s*$', why='Add meena, arjun')], button='Create user group', out='Faculty: FacultyNotes · meena, arjun'),
        lights=['grp', 'users', 'att', 'mem'], explain='Next semester’s new teacher = one add-user-to-group. No new permissions to write — the lab-exam “one action” requirement.'),
   dict(title='Prove: submissions are explicitly denied', goal='Simulate <code>s3:GetObject</code> on <code>submissions/a1.txt</code> for meena.', hint='<code>aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::{acct}:user/meena --action-names s3:GetObject --resource-arns arn:aws:s3:::edu-content/submissions/a1.txt</code>',
        answer='aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::{acct}:user/meena --action-names s3:GetObject --resource-arns arn:aws:s3:::edu-content/submissions/a1.txt',
        cli=[dict(re=r'^aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::{acct}:user/meena --action-names s3:GetObject --resource-arns arn:aws:s3:::edu-content/submissions/\S+( --query .*)?( --output \w+)?$', out='s3:GetObject   arn:aws:s3:::edu-content/submissions/a1.txt   explicitDeny   (matched statement: NeverSubmissions)')],
        errors=[dict(re=r'^aws iam simulate-principal-policy .*--action-names s3:PutObject --resource-arns arn:aws:s3:::edu-content/notes/\S+', out='s3:PutObject   …/notes/l2.txt   allowed   (matched: ReadWriteNotes)\n(Allowed side proven. Now test submissions.)', ok=True)],
        console=dict(crumbs='IAM › Policy Simulator', fields=[dict(label='User', type='select', options=['meena', 'arjun'], re=r'^meena$', why='Simulate meena.'), dict(label='Action', type='select', options=['s3:PutObject', 's3:GetObject'], re=r'^s3:GetObject$', why='Test GetObject.'), dict(label='Resource', ph='arn:aws:s3:::edu-content/submissions/a1.txt', re=r'^arn:aws:s3:::edu-content/submissions/a1\.txt$', why='Use the submissions file ARN.')], button='Run simulation', out='GetObject submissions/a1.txt → explicitDeny (NeverSubmissions)'),
        lights=['subs', 'd1'], explain='<b>explicitDeny</b> means a Deny statement matched — even if someone later attaches AmazonS3FullAccess to Faculty, this stays denied.'),
   dict(title='Prove: own drafts only', goal='Simulate <code>s3:PutObject</code> for <b>arjun</b> on <code>drafts/arjun/d.txt</code>.', hint='Same command with user arjun and resource drafts/arjun/d.txt.', answer='aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::{acct}:user/arjun --action-names s3:PutObject --resource-arns arn:aws:s3:::edu-content/drafts/arjun/d.txt',
        cli=[dict(re=r'^aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::{acct}:user/arjun --action-names s3:PutObject --resource-arns arn:aws:s3:::edu-content/drafts/arjun/\S+( --query .*)?( --output \w+)?$', out='s3:PutObject   …/drafts/arjun/d.txt   allowed   (${aws:username} = arjun)')],
        errors=[dict(re=r'^aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::{acct}:user/arjun --action-names s3:PutObject --resource-arns arn:aws:s3:::edu-content/drafts/meena/\S+', out='s3:PutObject   …/drafts/meena/d.txt   implicitDeny\n(Correct — arjun cannot write to meena’s drafts. Now test his own folder.)', ok=True)],
        console=dict(crumbs='IAM › Policy Simulator', fields=[dict(label='User', type='select', options=['meena', 'arjun'], re=r'^arjun$', why='Simulate arjun.'), dict(label='Resource', ph='arn:aws:s3:::edu-content/drafts/arjun/d.txt', re=r'^arn:aws:s3:::edu-content/drafts/arjun/d\.txt$', why='Use arjun’s own drafts ARN.')], button='Run simulation', out='PutObject drafts/arjun/d.txt → allowed'),
        lights=['drafts', 'a1'], explain='The same policy gave meena and arjun different private folders: ${aws:username} was replaced by the caller’s name at evaluation time.'),
  ]))
