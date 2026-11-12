from cloudkit import *

HOOD = under_hood('What happens behind the sign-up, sign-in and billing screens.', [
 ('1 · Root sign-in vs IAM user sign-in',
  '<p>Root signs in with the <b>e-mail address</b> used at sign-up. IAM users sign in at an <b>account-specific URL</b>: <code>https://ACCOUNT_ID.signin.aws.amazon.com/console</code>, or a friendlier alias you create (<code>aws iam create-account-alias --account-alias tiffingo</code> → <code>https://tiffingo.signin.aws.amazon.com/console</code>). Two different doors: if a user tries the root door with their user name, sign-in fails.</p>'),
 ('2 · How an authenticator-app MFA code works',
  '<p>When you scan the QR code, AWS and your phone share a secret. Every <b>30 seconds</b> both compute a 6-digit code from that secret and the current time (the TOTP standard, RFC 6238). AWS accepts the code if it matches its own calculation — nothing is sent to your phone. That is why the phone clock must be correct, and why AWS asks for <b>two consecutive codes</b> when you set it up. <b>Passkeys / security keys</b> use public-key cryptography (FIDO2) instead: the private key never leaves the device, so they resist phishing.</p>'),
 ('3 · Where credentials live',
  table(['Credential', 'Who uses it', 'Lifetime', 'Risk if leaked'], [['Root password + MFA', 'account owner, rare tasks', 'until changed', 'total control (MFA blocks most attacks)'], ['IAM user password', 'person, console', 'until changed / policy', 'that user’s permissions'], ['Access key (AKIA…)', 'CLI/SDK', 'until deleted — <b>long-term</b>', 'that identity’s permissions until noticed'], ['Temporary credentials (ASIA… + session token)', 'roles, SSO, CloudShell', 'minutes to hours', 'expires automatically'], ['Instance profile role', 'apps on EC2', 'rotated automatically', 'scoped to the role']], minw=600) +
  '<p>Rule of thumb: prefer anything temporary. Long-term keys are the #1 cause of leaked-credential incidents.</p>'),
 ('4 · How billing really works',
  '<p>Every service emits <b>usage records</b> (hours, GB-months, requests). The billing system rates them with that day’s price list, applies Free Tier allowances, then <b>credits</b>, and adds the result to the month’s bill. Cost data refreshes <b>a few times a day</b>, so budgets and Cost Explorer are hours behind real usage — a budget is an <i>early warning</i>, not a real-time brake. The invoice is issued in the first days of the next month.</p>'),
 ('5 · What “closing an account” does',
  '<p>A closed account enters a <b>post-closure period of 90 days</b> during which you can reopen it; after that the account and its content are permanently deleted. Resources may still exist in that window, which is why you should <b>delete resources first</b>, then close. The account’s e-mail cannot be reused for a new AWS account.</p>'),
])

PRO = (
 '  <h3>How companies set up accounts (not one account for everything)</h3>\n' + table(['Account', 'Purpose', 'Typical guard-rail'], [
   ['Management (payer)', 'billing, AWS Organizations', 'no workloads at all; very few people'], ['Security / audit', 'central CloudTrail logs, security tools', 'read-only for most; logs locked'], ['Production', 'live customer systems', 'strict change process, least privilege'], ['Development / test', 'build and test', 'budgets, cheaper sizes, automatic shut-down'], ['Sandbox (per learner)', 'experiments', 'small budget, auto-cleanup']], minw=560) +
 '  <p>Accounts are the strongest isolation boundary AWS has: a mistake in a sandbox cannot touch production. AWS Organizations groups them, applies <b>service control policies</b> (for example “nobody may leave ap-south-1” or “nobody may disable CloudTrail”) and gives one consolidated bill. People sign in once through <b>IAM Identity Center</b> and pick an account and role.</p>\n'
 '  <h3>Day-one hardening beyond this lab</h3>\n' + table(['Setting', 'Where', 'Why'], [
   ['Alternate contacts (billing, operations, security)', 'Account settings', 'AWS security notices reach the right team, not one inbox'],
   ['Account alias', 'IAM dashboard', 'readable sign-in URL'], ['IAM Access Analyzer', 'IAM', 'finds resources shared outside the account'],
   ['Cost Anomaly Detection', 'Billing → Cost Anomaly Detection', 'machine-learning alerts for unusual spend (catches Kabir’s GPU bill)'],
   ['CloudTrail trail to S3', 'CloudTrail', 'keep audit logs beyond 90 days'], ['Block Public Access for S3 (account level)', 'S3 settings', 'no bucket can be made public by mistake'],
   ['Password policy', 'IAM → Account settings', 'length and rotation rules for IAM users']], minw=560) +
 cost_calc('Worked example: what a forgotten lab can cost (Mumbai, On-Demand)', [
   ['EC2 t3.micro left running', '730 hours', 'USD 0.0112 / hour', 'USD 8.18'],
   ['EC2 m5.large “just testing”', '730 hours', '≈ USD 0.10 / hour', '≈ USD 73'],
   ['NAT gateway left behind', '730 hours', '≈ USD 0.056 / hour + data', '≈ USD 41+'],
   ['Elastic IP not attached', '730 hours', 'USD 0.005 / hour', 'USD 3.65']],
   '≈ USD 126 for one forgotten month', 'Approximate ap-south-1 prices; confirm in the Pricing Calculator. Since February 2024 every public IPv4 address is charged (≈ USD 0.005/hour) whether attached or not. A zero-spend budget e-mails you on the first cent.') +
 '  <h3>Errors you may meet while setting up</h3>\n' + errors_table([
   ('Your authentication information is incorrect. Please try again.', 'IAM user signing in', 'wrong door (root page), wrong account ID/alias, or wrong password', 'use the account-specific sign-in URL; ask an admin to reset the password'),
   ('Your MFA code could not be validated', 'MFA sign-in or setup', 'phone clock out of sync, or codes not consecutive during setup', 'turn on automatic time on the phone; wait for two fresh codes'),
   ('An error occurred (EntityAlreadyExists) when calling the CreateUser operation', 'creating a user', 'that user name already exists', 'pick another name or reuse the existing user'),
   ('An error occurred (PasswordPolicyViolation) ...', 'create-login-profile', 'password does not meet the account password policy', 'longer password with mixed characters'),
   ('An error occurred (AccessDeniedException) when calling the CreateBudget operation', 'creating budgets as a user', 'IAM access to Billing is not activated, or no budgets permission', 'root: Account → “IAM user and role access to Billing information” → Activate'),
   ('Your account is pending verification', 'right after sign-up', 'card or phone verification still running', 'wait (usually minutes); check e-mail; contact Support if it takes hours')]) +
 '  <h3>CLI cheat sheet for account setup</h3>\n' + cheatsheet([
   ('aws iam get-account-summary', 'account-level counters, incl. root MFA and root keys'),
   ('aws iam create-account-alias --account-alias tiffingo', 'friendly sign-in URL'),
   ('aws iam generate-credential-report; aws iam get-credential-report', 'CSV of every user: password, MFA, key age'),
   ('aws iam list-mfa-devices --user-name riya-admin', 'is MFA on for this user?'),
   ('aws budgets describe-budgets --account-id ACCOUNT_ID', 'your budgets and current spend'),
   ('aws freetier get-account-plan-state --region us-east-1', 'Free/Paid plan, credits, end date'),
   ('aws account put-alternate-contact --alternate-contact-type SECURITY --name ... --title ... --email-address ... --phone-number ...', 'security contact for AWS notices')]) +
 checklist('Account-ready checklist (tick all before Module 2)', ['Root: MFA on, no access keys, password in a safe place.', 'Admin user with MFA; you have signed in with it.', 'Account alias created (optional).', 'Zero-spend budget and a monthly budget with e-mail alerts.', 'Alternate security contact set.', 'You know your plan (Free/Paid), credits and end date.']) +
 refs([('Choosing an AWS Free Tier plan', 'https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/free-tier-plans.html'), ('AWS Support plans', 'https://docs.aws.amazon.com/awssupport/latest/user/aws-support-plans.html'), ('Getting started with AWS', 'https://docs.aws.amazon.com/getting-started/')])
)

PROJ = projects([
 ('Basic', 'Safe personal learning account', 'You will use AWS for this whole course.',
  ['Create the account on the Free plan.', 'Root MFA (passkey or app), no root keys.', 'Admin user with MFA; account alias.', 'Zero-spend + $5 monthly budgets.'],
  'Screenshots (or CLI output) proving each item, with the account ID masked.', 'Add Cost Anomaly Detection with an e-mail subscription.'),
 ('Intermediate', 'Credential report audit', 'Your college lab account has 40 IAM users created by different faculty over two years.',
  ['Generate the credential report and open it as CSV.', 'Find users with a password but no MFA.', 'Find access keys older than 90 days or never used.', 'Write a one-page remediation list (who, what, by when).'],
  'The filtered CSV and the remediation list.', 'Automate it: a script that prints the three lists from the report.'),
 ('Advanced', 'Multi-account design for an institute', 'An institute wants separate environments for 4 centres, faculty and students.',
  ['Draw an Organizations tree: management, security, shared-services, one OU for centres, one for student sandboxes.', 'Write three SCPs in plain English (e.g. only ap-south-1; no disabling CloudTrail; no large instance types in sandboxes).', 'Describe how a faculty member signs in once and reaches the right account (Identity Center permission sets).', 'Estimate cost controls per sandbox (budget actions).'],
  'A diagram, the SCP list and a half-page explanation.', 'Write one SCP in JSON and validate it with IAM Access Analyzer policy validation.')])

ROLES = by_role('Every role needs an identity — but not the same one. Getting access right on day one avoids both blocked engineers and over-powered accounts.', [
 ('Software developer', 'Needs to deploy and debug in dev, read-only in prod.', 'Identity Center permission set “Developer” in the dev account; “ReadOnly” in prod; CLI via <code>aws configure sso</code>.', 'Runs <code>aws sso login</code> each morning; gets 8-hour temporary credentials; no access keys on the laptop.', 'SSO profiles, never committing credentials, using roles in code.'),
 ('App / mobile developer', 'Needs Amplify/Cognito/API Gateway in dev; never needs root or billing.', 'Developer permission set scoped to app services; separate sandbox account for experiments.', 'Creates a Cognito user pool in the sandbox, deletes it at the end of the sprint.', 'Working inside a budgeted sandbox.'),
 ('Data analyst', 'Needs to query data, not create infrastructure.', 'Read access to specific S3 prefixes / Lake Formation tables, Athena and QuickSight permissions.', 'Signs in through SSO to an analytics account; queries only the curated tables.', 'Understanding that access is per dataset, not per account.'),
 ('Data engineer', 'Builds pipelines in dev; deploys to prod through CI/CD.', 'Data-engineering permission set (Glue, EMR, S3 prefixes); prod changes only via pipeline role.', 'Tests a Glue job in dev; merges to main; the pipeline deploys it to prod.', 'Separating human access from deployment roles.'),
 ('ML / AI engineer', 'Needs SageMaker/Bedrock and GPU quota; GPU costs are high.', 'ML permission set; service quota requests for GPU instances; strict budgets and budget actions.', 'Requests a quota increase for g-series instances before a training run; sets a budget action to stop notebooks at a threshold.', 'Quotas, budgets and stopping idle notebooks.'),
 ('DevOps / cloud engineer', 'Owns the account structure itself.', 'Administrator in management/security accounts (rarely used, MFA-enforced), break-glass procedure for root.', 'Creates new accounts for a new project from a template with guard-rails already on.', 'Organizations, SCPs, Identity Center, account vending.'),
 ('Security engineer', 'Audits everyone else.', 'SecurityAudit / read-only across all accounts, write access only in the security account.', 'Monthly: credential report, unused access keys, Access Analyzer findings.', 'Reading credential reports and CloudTrail.')])

DOMAINS = by_domain('How the account set-up changes by industry.', [
 ('Banking and fintech', 'regulated workloads', 'separate accounts per environment and per business line; SCPs restricting Regions to India; break-glass root procedure with dual control', 'RBI outsourcing guidelines; audit evidence of who can access what'),
 ('Healthcare', 'patient data', 'dedicated accounts for patient-data workloads; Business Support+ or higher for 24×7 help; strict alternate security contact', 'DPDP; ABDM; HIPAA BAA if serving US patients'),
 ('Education / training institutes', 'student labs', 'one sandbox account per student or batch (Organizations), small budgets with actions, automatic cleanup', 'student personal data; avoid sharing one admin login across a class'),
 ('Start-ups', 'move fast, tiny team', 'start with management + one workload account, Identity Center from day one, Free plan credits then Paid plan', 'do not let the founder’s root e-mail be the only access path'),
 ('Government', 'citizen data', 'MeitY-empanelled offerings, India Regions only, procurement through approved channels', 'MeitY and CERT-In requirements')])

NEWBIE = newbie('Opening an AWS account is like opening a bank account: you get a <b>master key</b> (root user) that can do everything — so you lock it in a safe and use a <b>normal card</b> (admin user) every day. A <b>budget alert</b> is like an SMS from your bank when you spend too much.',
  [('Account', 'your own private space in AWS, with its own bill'), ('Root user', 'the master login created at sign-up'), ('MFA', 'a second check, like an OTP on your phone'), ('Free Tier', 'free credits and limits for learning'), ('Budget', 'a spending limit that sends you alerts')])
LADDER = ladder([
 ('An AWS account is your space; the first login (root) is a master key — keep it safe; turn on OTP-style MFA.', 'Turn on two-step login (OTP) for your email or UPI app — the same idea as MFA.', 'Should you share your root password with a friend helping you?', 'Never. Create a separate login for anyone helping.'),
 ('Create an account, choose the Free plan, enable MFA on root, create an admin user, set a budget.', 'Do the hands-on lab (or the simulator) end to end.', 'Which identity should you use every day?', 'The admin user (or SSO), never root.'),
 ('Understand Free vs Paid plan, credits, always-free and trials; read your plan with the freetier API.', 'Run get-account-plan-state and get-free-tier-usage and explain each field.', 'What happens when a Free plan ends without upgrade?', 'The account closes; data is kept 90 days, then deleted.'),
 ('Harden an account: alternate contacts, Access Analyzer, Cost Anomaly Detection, CloudTrail trail, password policy.', 'Generate the credential report and find users without MFA.', 'Why are root access keys dangerous even with a strong password?', 'Keys bypass MFA and cannot be limited by IAM policies.'),
 ('Design multi-account setups with Organizations, SCPs and Identity Center; plan break-glass access.', 'Draw an account structure for an institute with SCPs for sandboxes.', 'Which account should hold no workloads at all?', 'The management (payer) account.')])
