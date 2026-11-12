from cloudkit import *

HOOD = under_hood('What the CLI and SDKs do before a single byte reaches AWS — the knowledge that solves 80% of “it works on my machine” problems.', [
 ('1 · The credential provider chain, in order',
  '<p>The CLI (and every SDK) checks these sources <b>in order</b> and uses the <b>first</b> it finds:</p>' +
  table(['#', 'Source', 'Example', 'Typical use'], [
    ['1', 'Command-line options', '<code>--profile dev</code>, <code>--region</code>', 'one-off override'],
    ['2', 'Environment variables', '<code>AWS_ACCESS_KEY_ID</code>, <code>AWS_SESSION_TOKEN</code>, <code>AWS_PROFILE</code>', 'CI pipelines, containers'],
    ['3', 'Web identity / SSO / assume-role profiles in <code>~/.aws/config</code>', '<code>sso_session</code>, <code>role_arn</code>', 'developers (recommended)'],
    ['4', 'Shared credentials file', '<code>~/.aws/credentials</code>', 'legacy long-term keys'],
    ['5', 'Container credentials', 'ECS task role endpoint; CloudShell', 'containers, CloudShell'],
    ['6', 'EC2 instance metadata (IMDSv2)', 'instance profile role', 'apps on EC2']], minw=600) +
  '<p>Classic bug: an old <code>AWS_ACCESS_KEY_ID</code> exported in <code>.bashrc</code> silently overrides your SSO profile. Run <code>aws configure list</code> — the <b>Type</b> column shows which source won.</p>'),
 ('2 · How SSO sign-in works on a laptop',
  '<ol><li><code>aws sso login</code> opens a browser to your IAM Identity Center portal (device-authorisation flow).</li><li>You sign in with password + MFA once; a token is cached in <code>~/.aws/sso/cache/</code> (typically valid for hours).</li><li>For each command the CLI exchanges the token for <b>temporary role credentials</b> for the chosen account and permission set.</li><li>When the session expires you see <code>Token has expired and refresh failed</code> — just run <code>aws sso login</code> again.</li></ol><p>No long-term secret ever lands on the laptop — a lost laptop is a much smaller incident.</p>'),
 ('3 · Retries, timeouts and what --debug shows',
  '<p>The CLI retries throttling and transient errors automatically (<code>standard</code> mode: up to 3 attempts with exponential backoff; <code>adaptive</code> adds client-side rate limiting). <code>aws s3 ls --debug 2&gt;&amp;1 | less</code> shows: which credential source was used, the endpoint, the signed headers (not the secret), retries and the raw response. Learn to read it — it ends most debugging sessions.</p>'),
 ('4 · High-level vs low-level commands',
  table(['Command family', 'Example', 'Behaviour'], [['High-level <code>aws s3</code>', '<code>aws s3 sync ./site s3://b/</code>', 'many API calls for you: multipart upload, parallel transfers, compares sizes/timestamps'], ['Low-level <code>aws s3api</code>', '<code>aws s3api put-object …</code>', 'exactly one API operation; full control of every parameter'], ['Waiters', '<code>aws ec2 wait instance-running</code>', 'polls a Describe call until a state is reached or times out'], ['Dry run', '<code>--dry-run</code> (EC2)', 'checks permissions; returns DryRunOperation if allowed']], minw=560)),
 ('5 · CloudShell internals',
  '<p>Each CloudShell session is a small Linux compute environment managed by AWS in the Region you opened it from, with your console credentials delivered through a container credential endpoint. <code>$HOME</code> (1 GB) persists per Region; data there is deleted if you do not use CloudShell in that Region for a long period (120 days). It has outbound internet access by default; a <b>VPC environment</b> option places it in your VPC to reach private resources.</p>'),
])

ROLES = by_role('How each role actually uses the console, CLI and SDKs day to day.', [
 ('Software developer (backend)', 'Lives in the IDE and terminal; console only to check.', 'SSO profiles, AWS Toolkit, SDK clients with paginators, <code>aws logs tail --follow</code>.', 'Debug a failing Lambda: <code>aws logs tail /aws/lambda/order-api --since 10m --follow</code>, fix code, redeploy from the IDE.', 'Credential chain, SDK error codes, log tailing.'),
 ('App / mobile developer', 'Uses Amplify CLI/console and S3/CloudFront commands for front ends.', 'Amplify, <code>aws s3 sync</code>, <code>aws cloudfront create-invalidation</code>.', 'Deploy a new build: <code>aws s3 sync dist/ s3://web --delete</code> then invalidate <code>/*</code> on CloudFront.', 'Sync semantics, cache invalidation.'),
 ('Data analyst', 'Mostly console (Athena, QuickSight); CLI to fetch results.', '<code>aws athena start-query-execution</code>, <code>aws s3 cp</code> of result CSVs.', 'Schedule a daily query and download the CSV into Excel.', 'Running Athena from the CLI, S3 paths.'),
 ('Data engineer', 'Scripts and pipelines; console to inspect jobs.', '<code>aws s3 sync</code>, <code>aws glue start-job-run</code>, <code>aws emr add-steps</code>, boto3 in Airflow tasks.', 'A boto3 task lists new files with a paginator and starts a Glue job only when data has arrived.', 'Pagination, idempotency, waiters.'),
 ('ML / AI engineer', 'Notebooks with the SDK; CLI for data movement.', 'SageMaker Python SDK, boto3 <code>bedrock-runtime</code>, <code>aws s3 cp --recursive</code> for datasets.', 'Call a Bedrock model from Python with <code>invoke_model</code>; stream large datasets to S3 with multipart upload.', 'SDK auth in notebooks (execution roles), large transfers.'),
 ('DevOps / cloud engineer', 'CLI and IaC all day; console for incidents.', 'Profiles per account, <code>--query</code>, CloudFormation/Terraform, CI pipelines with OIDC roles.', 'Find every unencrypted EBS volume in all Regions with one loop and a JMESPath filter.', 'Bash/PowerShell scripting, multi-account profiles.'),
 ('Security engineer', 'Read-only CLI across accounts; console for investigations.', 'SecurityAudit role profiles, <code>aws iam get-credential-report</code>, <code>aws cloudtrail lookup-events</code>, Access Analyzer.', 'Find every access key older than 90 days across 30 accounts in a script.', 'Cross-account roles, report parsing.')])

DOMAINS = by_domain('Access rules differ by industry — mostly about who may touch production and how it is recorded.', [
 ('Banking / fintech', 'regulated production', 'no human console write access to prod; changes only via pipelines; break-glass roles with alerts', 'RBI audit trails; maker-checker for changes'),
 ('Healthcare', 'patient-data systems', 'read-only console for support staff; CLI access through bastion/Session Manager with logging', 'DPDP; least privilege on data'),
 ('Retail / e-commerce', 'fast releases', 'developers deploy via CI/CD; console for monitoring during sales', 'change freezes before festival sales'),
 ('Education', 'many short-lived lab users', 'CloudShell for students (no keys), sandbox accounts, auto-cleanup scripts', 'never share one login across a batch'),
 ('Start-ups', 'small teams', 'SSO from day one, one profile per account, IaC early', 'avoid “everyone is admin with keys”'),
 ('Government', 'citizen systems', 'access via approved networks, full CloudTrail, SSO with MFA', 'CERT-In log retention')])

PRO = (
 '  <h3>Ten commands professionals type every week</h3>\n' + cheatsheet([
   ('aws sso login --profile prod-readonly', 'start a short-lived session for a profile'),
   ("aws ec2 describe-instances --filters Name=instance-state-name,Values=running --query 'Reservations[].Instances[].[InstanceId,InstanceType,Tags[?Key==`Name`]|[0].Value]' --output table", 'running instances with their Name tag'),
   ('aws logs tail /aws/lambda/order-api --since 15m --follow', 'live-tail application logs'),
   ('aws s3 sync ./build s3://my-site --delete --exclude "*.map"', 'deploy a static site'),
   ('aws s3 ls s3://bucket/prefix/ --recursive --human-readable --summarize', 'size of a folder'),
   ("aws cloudformation describe-stacks --query 'Stacks[].[StackName,StackStatus]' --output table", 'stack status'),
   ('aws ec2 wait instance-running --instance-ids i-0123…', 'block until ready (scripts)'),
   ('aws iam simulate-principal-policy --policy-source-arn ARN --action-names s3:GetObject', 'would this identity be allowed?'),
   ('for r in $(aws ec2 describe-regions --query "Regions[].RegionName" --output text); do …; done', 'run anything in every Region'),
   ('aws configure export-credentials --profile dev --format env', 'print temporary credentials for another tool')]) +
 '  <h3>Errors from the CLI — and fixes</h3>\n' + errors_table([
   ('The config profile (dev) could not be found', 'using --profile', 'profile name typo or not in ~/.aws/config', '<code>aws configure list-profiles</code>; add with <code>aws configure sso</code>'),
   ('Error when retrieving token from sso: Token has expired and refresh failed', 'SSO profiles', 'session expired', '<code>aws sso login --profile dev</code>'),
   ('Bad value for --query Buckets[.Name: Expecting: ...', 'JMESPath', 'syntax error in the query', 'quote the query in single quotes; check brackets'),
   ('Parameter validation failed: Invalid bucket name', 's3api calls', 'name breaks S3 rules (uppercase, underscores…)', 'lowercase letters, digits, hyphens; 3–63 chars'),
   ('An error occurred (BucketAlreadyExists) when calling the CreateBucket operation', 'aws s3 mb', 'bucket names are global; someone owns it', 'add a unique suffix (account ID or date)'),
   ('An error occurred (DryRunOperation) … Request would have succeeded, but DryRun flag is set.', '--dry-run', 'not an error — permission check passed', 'remove --dry-run to run for real'),
   ('aws: error: argument command: Invalid choice', 'any command', 'typo, or CLI v1 lacks a newer service', 'check spelling; upgrade to the latest CLI v2')]) +
 checklist('Professional CLI hygiene', ['CLI v2, kept up to date.', 'SSO profiles; no long-term keys on laptops.', 'One profile per account/role, named clearly (prod-readonly, dev-admin).', 'Prompt shows the active profile (avoid running dev commands in prod).', 'Scripts use <code>set -euo pipefail</code>, waiters and pagination.', 'Destructive commands reviewed; <code>--dry-run</code> where available.']) +
 refs([('AWS CLI v2 user guide', 'https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html'), ('Filtering output with --query', 'https://docs.aws.amazon.com/cli/latest/userguide/cli-usage-filter.html'), ('Configuring IAM Identity Center authentication with the CLI', 'https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html'), ('AWS CloudShell user guide', 'https://docs.aws.amazon.com/cloudshell/latest/userguide/welcome.html')])
)

PROJ = projects([
 ('Basic', 'Console vs CLI race', 'Do the same task both ways and time yourself.',
  ['Console: create a bucket, upload 3 files, share one with a presigned URL, delete everything.', 'CLI: the same with the Step 3 commands.', 'Record time, number of clicks/commands, and mistakes.'],
  'A small table and two sentences on when you would use each.', 'Turn the CLI version into a reusable script with the bucket name as an argument.'),
 ('Intermediate', 'Batch onboarding script', 'A new batch of 30 students needs a folder each in a shared bucket.',
  ['Create <code>students.csv</code> with roll numbers.', 'Write a Bash loop that creates <code>s3://BUCKET/batch-2026/ROLL/</code> markers and uploads a welcome file to each.', 'Make it idempotent (running twice does not duplicate or fail).', 'Print a summary with <code>--query</code>/<code>wc -l</code>.'],
  'The script, its output and the S3 listing.', 'Add a <code>--dry-run</code> flag to your own script that only prints what it would do.'),
 ('Advanced', 'Multi-Region inventory in Python (SDK)', 'Ops wants a daily list of running instances and unattached volumes in every Region.',
  ['boto3: loop over enabled Regions; use paginators for <code>describe_instances</code> and <code>describe_volumes</code>.', 'Collect running instances (id, type, AZ, Name tag) and volumes with state <code>available</code> (unattached, still billed).', 'Write a CSV and upload it to S3 with a dated key.', 'Handle <code>ClientError</code> and throttling gracefully.'],
  'Code, a sample CSV and the S3 object key.', 'Schedule it with EventBridge Scheduler + Lambda (Module 7/9).')])

SIMD = awsfig('CLI flow: your command in CloudShell finds credentials, reads configuration, signs the request, reaches S3 and EC2 endpoints, and output is shaped by --query.',
    svc(55, 40, 'list', 'Command', 'CloudShell', 'blue', k='cmd') +
    svc(155, 20, 'key', 'Credentials', 'container-role', 'amber', k='cred', w=80) + svc(155, 92, 'file', 'Config', 'region, output', 'card', k='cfg', w=80) +
    link(92, 66, 114, 46, k='l1') + link(92, 66, 114, 118, k='l2') +
    svc(260, 56, 'shield', 'SigV4', 'signed HTTPS', 'red', k='sign') + link(196, 46, 224, 72, k='l3') + link(196, 118, 224, 90, k='l4') +
    grp('region', 330, 14, 180, 150, 'ap-south-1', k='reg') +
    svc(380, 40, 'bucket', 'S3', 'mb / cp / presign', 'green', k='s3') + svc(465, 40, 'server', 'EC2', 'dry-run', 'blue', k='ec2') +
    svc(420, 108, 'clock', 'CloudTrail', 'every call', 'card', k='trail', w=80) +
    svc(580, 56, 'chart', '--query', 'table / text', 'violet', k='q') + link(296, 82, 334, 82, k='l5'), h=180)

SIM = simlab(dict(title='CloudShell drill: from first command to a full cycle', intro='Type the commands as you would in CloudShell. Try a wrong one too — the simulator shows the real error.',
  diagram=SIMD, lit=['cmd'],
  free=[dict(re=r'^aws --version$', out='aws-cli/2.31.x Python/3.13.x Linux/6.x exec-env/CloudShell exe/x86_64.amzn.2023'),
        dict(re=r'^aws sts get-caller-identity( --query Arn --output text)?$', out='arn:aws:iam::{acct}:user/{you}')],
  steps=[
   dict(title='Check where credentials come from', goal='Show which credential source and Region the CLI is using.', hint='<code>aws configure list</code>', answer='aws configure list',
        cli=[dict(re=r'^aws configure list$', out='      Name                    Value             Type    Location\n      ----                    -----             ----    --------\n   profile                <not set>             None    None\n access_key     ****************QW7E     container-role\n secret_key     ****************9x2a     container-role\n    region               ap-south-1              env    [\'AWS_REGION\', \'AWS_DEFAULT_REGION\']')],
        lights=['cred', 'cfg', 'l1', 'l2'], explain='Type <b>container-role</b> means CloudShell handed the CLI temporary credentials from your console session — position 5 in the provider chain. No keys are stored in your home folder.'),
   dict(title='Shape output with --query', goal='Print only the names of Regions starting with <code>ap-</code>, as text.', hint="<code>--query 'Regions[?starts_with(RegionName, `ap-`)].RegionName' --output text</code>",
        answer="aws ec2 describe-regions --query 'Regions[?starts_with(RegionName, `ap-`)].RegionName' --output text",
        cli=[dict(re=r"^aws ec2 describe-regions --query '?Regions\[\?starts_with\(RegionName, ?`ap-`\)\]\.RegionName'? --output text$", out='ap-south-1\tap-northeast-3\tap-northeast-2\tap-southeast-1\tap-southeast-2\tap-northeast-1')],
        errors=[dict(re=r"^aws ec2 describe-regions --query .*\[\?starts_with\(RegionName, ?'ap-'\)", out='Bad value for --query: In JMESPath, string literals inside a filter use backticks or raw quotes inside the outer quotes.\n→ Use `ap-` (backticks) when the whole query is in single quotes.'),
                dict(re=r'^aws ec2 describe-regions$', out='{\n    "Regions": [\n        {"Endpoint": "ec2.ap-south-1.amazonaws.com", "RegionName": "ap-south-1", "OptInStatus": "opt-in-not-required"},\n        … 16 more …\n    ]\n}\n(Correct, but long. Add --query and --output text.)', ok=True)],
        lights=['sign', 'l3', 'l4', 'l5', 'reg', 'ec2', 'q'], explain='The full JSON still came back from EC2; JMESPath kept only matching names on your side and <code>--output text</code> printed them tab-separated — ready for a shell loop.'),
   dict(title='Create a bucket', goal='Create a bucket named <code>cli-lab-{rnd}</code> in ap-south-1.', hint='<code>aws s3 mb s3://cli-lab-{rnd} --region ap-south-1</code>', answer='aws s3 mb s3://cli-lab-{rnd} --region ap-south-1',
        cli=[dict(re=r'^aws s3 mb s3://(?<b>cli-lab-[a-z0-9-]+)( --region ap-south-1)?$', out='make_bucket: {b}')],
        errors=[dict(re=r'^aws s3 mb s3://\S*[A-Z_]\S*', out='make_bucket failed: s3://… An error occurred (InvalidBucketName) when calling the CreateBucket operation: The specified bucket is not valid.\n→ Lowercase letters, numbers, dots and hyphens only.'),
                dict(re=r'^aws s3 mb s3://test$', out='make_bucket failed: s3://test An error occurred (BucketAlreadyExists): The requested bucket name is not available. The bucket namespace is shared by all users of the system.\n→ Bucket names are global. Use cli-lab-{rnd}.')],
        console=dict(crumbs='S3 › Create bucket', fields=[dict(label='Bucket name', key='b', re=r'^cli-lab-[a-z0-9-]+$', ph='cli-lab-{rnd}', why='Use a name starting with cli-lab- (lowercase).'), dict(label='Block all public access', type='check', must=True, why='Keep Block all public access ticked.')], button='Create bucket', out='Bucket {b} created in ap-south-1'),
        lights=['s3', 'trail'], explain='One <b>CreateBucket</b> API call. The name is now reserved worldwide; the bucket itself lives in Mumbai and is private by default.'),
   dict(title='Upload and share for 5 minutes', goal='Upload <code>hello.txt</code> and create a presigned URL valid for 300 seconds.', hint='<code>aws s3 cp hello.txt s3://{b}/</code> then <code>aws s3 presign s3://{b}/hello.txt --expires-in 300</code>. In the simulator, the presign command completes the step.',
        answer='aws s3 presign s3://{b}/hello.txt --expires-in 300',
        cli=[dict(re=r'^aws s3 presign s3://{b}/hello\.txt( --expires-in \d+)?$', out='https://{b}.s3.ap-south-1.amazonaws.com/hello.txt?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=ASIA…%2F20261112%2Fap-south-1%2Fs3%2Faws4_request&X-Amz-Date=20261112T101500Z&X-Amz-Expires=300&X-Amz-SignedHeaders=host&X-Amz-Signature=8f2c…')],
        errors=[dict(re=r'^aws s3 cp hello\.txt s3://{b}/?$', out='upload: ./hello.txt to s3://{b}/hello.txt\n(Uploaded. Now create the presigned URL.)', ok=True)],
        console=dict(crumbs='S3 › {b} › hello.txt › Actions › Share with a presigned URL', fields=[dict(label='Time interval until the presigned URL expires (minutes)', re=r'^5$', ph='5', why='Use 5 minutes.')], button='Create presigned URL', out='Presigned URL copied — valid for 5 minutes'),
        lights=['s3'], explain='No API call was needed for the URL: the CLI <b>signed a GET request locally</b> with your credentials (SigV4 in the query string). Anyone with the link can read that one object until it expires — the bucket stays private.'),
   dict(title='Dry-run, then delete', goal='Check you could launch an instance with <code>--dry-run</code>, then delete the bucket and its contents.', hint='<code>aws ec2 run-instances --dry-run …</code> then <code>aws s3 rb s3://{b} --force</code>. The rb command completes the step.', answer='aws s3 rb s3://{b} --force',
        cli=[dict(re=r'^aws s3 rb s3://{b} --force$', out='delete: s3://{b}/hello.txt\nremove_bucket: {b}')],
        errors=[dict(re=r'^aws ec2 run-instances --dry-run .*', out='An error occurred (DryRunOperation) when calling the RunInstances operation: Request would have succeeded, but DryRun flag is set.\n(Good — you have permission. Nothing was launched.)', ok=True),
                dict(re=r'^aws s3 rb s3://{b}$', out='remove_bucket failed: s3://{b} An error occurred (BucketNotEmpty) when calling the DeleteBucket operation: The bucket you tried to delete is not empty\n→ Add --force to delete objects first.')],
        console=dict(crumbs='S3 › Buckets › {b} › Empty, then Delete', fields=[dict(label='To confirm deletion, type the bucket name', re=r'^{b}$', ph='{b}', why='Type the exact bucket name: {b}')], button='Delete bucket', out='Bucket {b} deleted'),
        lights=['ec2', 'trail'], explain='<code>--force</code> made the CLI list and delete every object (many DeleteObject calls), then DeleteBucket. Every call is in CloudTrail — the audit trail of your lab.'),
  ]))

NEWBIE = newbie('There are two ways to order food: tap buttons in an app (the <b>console</b>) or send a typed message with your exact order (the <b>CLI</b>). Both reach the same kitchen. Typing is faster when you order the same thing every day — you can copy and resend it.',
  [('Console', 'AWS’s website with buttons and forms'), ('CLI', 'typing commands instead of clicking'), ('CloudShell', 'a ready-made place in the browser to type commands'), ('Command', 'one typed instruction, e.g. aws s3 ls'), ('Script', 'a saved list of commands you can run again')])
LADDER = ladder([
 ('Clicking (console) and typing (CLI) do the same jobs in AWS; typing can be saved and repeated.', 'Open CloudShell and type <code>aws --version</code> — your first command!', 'Which is better for doing the same task 100 times?', 'Typing commands (a script), because it is fast and identical every time.'),
 ('Command shape: aws service operation options; CloudShell is already signed in.', 'Run <code>aws s3 ls</code> and <code>aws sts get-caller-identity</code>.', 'What does aws sts get-caller-identity tell you?', 'Which identity (user/role) and account you are using.'),
 ('Use --query, --output, pagination and profiles; know the credential chain.', 'Do hands-on Step 2 and write one query of your own.', 'Does --query reduce the data AWS sends?', 'No — it filters on your machine after the response arrives.'),
 ('Script safely: set -euo pipefail, waiters, dry runs, SSO profiles per account, idempotent loops.', 'Write the batch-onboarding script from the projects section.', 'Why prefer aws sso login over access keys on a laptop?', 'Short-lived credentials; nothing long-term to leak.'),
 ('Build tools with SDK paginators, retries, multi-Region loops, OIDC for CI/CD; read --debug to fix chain problems.', 'Write the multi-Region inventory in boto3 with paginators.', 'An old AWS_ACCESS_KEY_ID in .bashrc — what happens to your SSO profile?', 'Environment variables come earlier in the chain and silently win.')])
