# v3 depth sections for 1.1 (imported by _body.py)
from cloudkit import *

HOOD = under_hood('What really happens between your keyboard and AWS. You do not need this to pass CLF-C02, but it is what separates someone who <i>uses</i> AWS from someone who can <i>debug</i> it.', [
 ('1 · Every action is an HTTPS request to a service endpoint',
  '<p>Each service has endpoints per Region, such as <code>https://ec2.ap-south-1.amazonaws.com</code> or <code>https://s3.ap-south-1.amazonaws.com</code>. A few services are <b>global</b> and have one endpoint for the whole account.</p>' +
  table(['Scope', 'Examples', 'What it means for you'], [['Global', 'IAM, Route 53, CloudFront, Organizations', 'create once, used in every Region; IAM changes apply everywhere'], ['Regional', 'S3 buckets, VPC, Lambda, DynamoDB, RDS', 'resources live in one Region; pick it deliberately'], ['Zonal (inside a Region)', 'EC2 instances, EBS volumes, subnets', 'live in one Availability Zone; spread across AZs for availability']], minw=520) +
  '<p>Run any CLI command with <code>--debug</code> to see the exact endpoint, headers and response.</p>'),
 ('2 · How AWS knows it is really you: Signature Version 4 (SigV4)',
  '<p>Your secret access key is <b>never sent</b> over the network. The CLI/SDK uses it to <b>sign</b> each request; AWS repeats the same calculation and compares signatures.</p>'
  '<ol><li><b>Canonical request</b> — method, path, query, sorted headers and a SHA-256 hash of the body are written in a fixed format.</li>'
  '<li><b>String to sign</b> — <code>AWS4-HMAC-SHA256</code>, the timestamp, the <i>scope</i> (<code>20261112/ap-south-1/ec2/aws4_request</code>) and the hash of the canonical request.</li>'
  '<li><b>Signing key</b> — derived in a chain: HMAC(“AWS4”+secret, date) → HMAC(·, region) → HMAC(·, service) → HMAC(·, “aws4_request”). A key for one day, Region and service cannot sign for another.</li>'
  '<li><b>Signature</b> — HMAC-SHA256(signing key, string to sign), added to the <code>Authorization</code> header.</li>'
  '<li><b>AWS verifies</b> — recomputes it, checks the timestamp is recent (a few minutes), then hands the request to IAM for authorisation.</li></ol>'
  + code('text', 'What the Authorization header looks like (shortened)', 'Authorization: AWS4-HMAC-SHA256 Credential=AKIAEXAMPLE/20261112/ap-south-1/ec2/aws4_request,\n  SignedHeaders=host;x-amz-date, Signature=5d672d79c15b13162d9279b0855cfba6789a8edb4c82c400e06b5924a6f2b5d7') +
  '<p>This is why a wrong system clock causes <code>SignatureDoesNotMatch</code> or “Signature expired” errors, and why temporary credentials carry an extra session token.</p>'),
 ('3 · Names for everything: ARNs',
  '<p>An <b>Amazon Resource Name</b> uniquely identifies a resource in policies and APIs: <code>arn:partition:service:region:account-id:resource</code>.</p>' +
  table(['Resource', 'ARN', 'Notice'], [['IAM user', 'arn:aws:iam::123456789012:user/riya-admin', 'no Region (IAM is global)'], ['S3 bucket', 'arn:aws:s3:::tiffingo-menu', 'no Region or account (bucket names are globally unique)'], ['S3 objects under a prefix', 'arn:aws:s3:::tiffingo-menu/images/*', 'wildcards allowed in policies'], ['EC2 instance', 'arn:aws:ec2:ap-south-1:123456789012:instance/i-0abc…', 'Region and account included'], ['AWS managed policy', 'arn:aws:iam::aws:policy/ReadOnlyAccess', 'account is the word “aws”']], minw=560)),
 ('4 · Limits, throttling and retries',
  '<p>Every API has a request rate limit and every account has <b>service quotas</b> (for example, how many vCPUs of On-Demand instances you may run). Exceed a rate and AWS answers <code>ThrottlingException</code> or <code>RequestLimitExceeded</code>; the SDKs and CLI retry automatically with <b>exponential backoff and jitter</b> (wait 1×, 2×, 4×… plus randomness). You can tune it with <code>AWS_RETRY_MODE=standard|adaptive</code> and <code>AWS_MAX_ATTEMPTS</code>.</p>'),
 ('5 · “I just created it — why can’t I see it?” Eventual consistency',
  '<p>AWS is a distributed system. Some changes take a moment to reach every server: a new IAM policy can take a few seconds to apply, and an EC2 <code>Describe</code> call right after <code>RunInstances</code> may briefly not return the new instance. Scripts should <b>wait</b> (<code>aws ec2 wait instance-running</code>) or retry rather than fail. Amazon S3 is an exception: since December 2020 it gives strong read-after-write consistency for all objects.</p>'),
])

PRO = (
 '  <h3>How organisations use AWS (illustrative cases)</h3>\n' + realcases([
   ('An ed-tech start-up in Pune (500 → 50,000 students)', 'Exam-result day crashed its single server every year.', 'Web tier on EC2 Auto Scaling behind a load balancer, videos in S3 + CloudFront, database on RDS Multi-AZ.', 'Handles 30× traffic on result day; pays for the peak only for a few hours.'),
   ('A Mumbai lending company (regulated)', 'Auditors need logs, encryption and data in India.', 'Workloads in ap-south-1, KMS encryption, CloudTrail to a locked log account, AWS Artifact reports for audits.', 'Passes audits with evidence from the console instead of spreadsheets.'),
   ('A media house in Bengaluru', 'Nightly video processing took 10 hours on in-house servers.', 'Files land in S3, events trigger processing on Spot Instances and Lambda, results back to S3.', 'Job finishes in under 2 hours at a fraction of the cost.')]) +
 '  <p class="muted" style="font-size:.9em">These are typical patterns, described generically — not specific named companies.</p>\n'
 '  <h3>AWS Support plans (changed in 2025–26)</h3>\n' + table(['Plan', 'Starts at', 'What you get'], [
   ['Basic', 'free, every account', 'account & billing help, documentation, re:Post forums, Health Dashboard, core Trusted Advisor checks'],
   ['Business Support+', 'USD 29 / month minimum per account', 'AI-assisted help with your account context, 24×7 engineers by phone/chat/web, under 30 min human engagement for business-critical down cases, full Trusted Advisor, Support API'],
   ['Enterprise Support', 'USD 5,000 / month minimum', 'everything above + designated Technical Account Manager, up to 15-minute response for production-critical cases, Security Incident Response'],
   ['Unified Operations', 'contract', 'TAM + domain specialist engineers, architecture guidance, critical workload reviews']], minw=600) +
 '  <p>Developer Support, Business Support and Enterprise On-Ramp are discontinued on <b>1 January 2027</b> (except in AWS GovCloud). Older exam material still names them — read the current AWS Support page before you answer exam or interview questions about plans.</p>\n'
 '  <h3>The six pillars every design review checks (AWS Well-Architected Framework)</h3>\n' + table(['Pillar', 'Question it asks'], [['Operational excellence', 'Can we run and improve it safely (automation, runbooks, small changes)?'], ['Security', 'Are identities, data and traffic protected and audited?'], ['Reliability', 'Does it recover from failure and handle demand?'], ['Performance efficiency', 'Are we using the right resources as needs change?'], ['Cost optimization', 'Are we paying only for what delivers value?'], ['Sustainability', 'Are we minimising energy and resources used?']], minw=480) +
 cost_calc('Worked cost example: TiffinGo’s first small website (Mumbai, On-Demand)', [
   ['EC2 t3.micro (Linux)', '730 hours', 'USD 0.0112 / hour', 'USD 8.18'],
   ['EBS gp3 disk', '8 GB', '≈ USD 0.09 / GB-month', '≈ USD 0.73'],
   ['S3 Standard (menu photos)', '10 GB', 'USD 0.025 / GB-month', 'USD 0.25'],
   ['Data out to the internet', '20 GB', 'first 100 GB / month free', 'USD 0.00']],
   '≈ USD 9.2 / month (≈ ₹780 at ₹85 per US$)',
   'Prices for ap-south-1 at the time of writing; always confirm with the AWS Pricing Calculator. On a Free plan account, credits cover this. Stopping the instance at night would cut the EC2 line by about half.') +
 '  <h3>Errors you will meet in your first week — and how to fix them</h3>\n' + errors_table([
   ('Unable to locate credentials. You can configure credentials by running "aws configure".', 'any CLI command on a new laptop', 'no credentials found in env vars, ~/.aws, SSO cache or instance role', 'use CloudShell, or <code>aws configure sso</code> / <code>aws configure</code>'),
   ('You must specify a region. You can also configure your region by running "aws configure".', 'regional service calls', 'no default Region set', '<code>aws configure set region ap-south-1</code> or add <code>--region</code>'),
   ('An error occurred (InvalidClientTokenId) ... The security token included in the request is invalid.', 'after copying keys', 'wrong/deleted access key ID', 'check the key in IAM → Security credentials; create a new one'),
   ('An error occurred (SignatureDoesNotMatch) ...', 'all calls fail from one machine', 'wrong secret key, or the machine clock is several minutes off', 'sync the clock (NTP); re-enter the secret'),
   ('An error occurred (ExpiredToken) ... The security token included in the request is expired', 'SSO/role sessions', 'temporary credentials expired', '<code>aws sso login</code> or re-assume the role'),
   ('An error occurred (AccessDenied) / (UnauthorizedOperation) ... is not authorized to perform: ec2:RunInstances', 'creating resources', 'your identity lacks that permission', 'ask for the specific permission; Module 2 shows how to read the message'),
   ('An error occurred (OptInRequired) ...', 'using a newer Region', 'opt-in Regions are disabled by default', 'Account → AWS Regions → enable the Region'),
   ('An error occurred (ThrottlingException) ... Rate exceeded', 'scripts in tight loops', 'API rate limit', 'let the SDK retry; add backoff; use pagination')]) +
 '  <h3>CLI cheat sheet for this lesson</h3>\n' + cheatsheet([
   ('aws sts get-caller-identity', 'who am I, in which account'), ('aws configure list', 'where your credentials and Region come from'),
   ('aws ec2 describe-regions --query "Regions[].RegionName" --output text', 'Regions enabled for your account'),
   ('aws ssm get-parameters-by-path --path /aws/service/global-infrastructure/regions/ap-south-1/services --query "length(Parameters)"', 'how many services Mumbai offers'),
   ('aws service-quotas get-service-quota --service-code ec2 --quota-code L-1216C47A', 'your vCPU quota for standard On-Demand instances'),
   ('aws <command> --debug', 'see the endpoint, signed headers and raw response'),
   ('aws cloudtrail lookup-events --max-results 5', 'your most recent API calls')]) +
 checklist('Before you build anything real on AWS', ['Root user has MFA and no access keys (Lesson 1.2).', 'You work as an IAM/Identity Center user with MFA.', 'A budget with e-mail alerts exists.', 'You know which Region you are in (top-right of the console, or <code>aws configure list</code>).', 'CloudTrail event history shows your own recent actions.', 'You have checked the service you need is available in your Region.']) +
 refs([('Overview of Amazon Web Services (whitepaper)', 'https://docs.aws.amazon.com/whitepapers/latest/aws-overview/introduction.html'), ('AWS Well-Architected Framework', 'https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html'), ('AWS Support plans', 'https://docs.aws.amazon.com/awssupport/latest/user/aws-support-plans.html'), ('Getting started with AWS', 'https://docs.aws.amazon.com/getting-started/')])
)

PROJ = projects([
 ('Basic', 'Map a real business onto AWS', 'Pick a business you know — a coaching class, a hospital, a kirana chain.',
  ['List 8 needs (website, files, database, logins, reports, backups, alerts, budget).', 'Map each need to a service family and one AWS service.', 'Mark each service as global, regional or zonal.', 'Check each is available in ap-south-1 with the SSM command.'],
  'A one-page table and a four-layer diagram.', 'Add the Azure and Google Cloud names for each service.'),
 ('Intermediate', 'Region comparison report with the CLI', 'TiffinGo may expand to Hyderabad. Which services are missing there?',
  ['Save the service list for ap-south-1 and ap-south-2 to two files with <code>aws ssm get-parameters-by-path ... --query "Parameters[].Value" --output text | tr "\\t" "\\n" | sort</code>.', 'Use <code>comm -23</code> to list services in Mumbai but not in Hyderabad.', 'Pick three of the missing services and say whether TiffinGo needs them.'],
  'The two lists, the difference, and a short recommendation.', 'Repeat for a non-Indian Region and comment on latency vs services.'),
 ('Advanced', 'Read-only account inventory tool in Python', 'Your manager asks: “What do we have running, in which Region?”',
  ['In CloudShell write <code>inventory.py</code> with boto3: list enabled Regions (<code>ec2.describe_regions</code>).', 'For each Region count EC2 instances by state and Lambda functions.', 'Count S3 buckets and print each bucket’s Region (<code>get_bucket_location</code>).', 'Handle <code>ClientError</code> for Regions you cannot access, and print a table.'],
  'The script, its output on your account, and two lines on what you would add next.', 'Export to CSV and upload to an S3 bucket with a date-stamped name.')])

SIMD = awsfig('Diagram: you in CloudShell send API requests to service endpoints; IAM checks them; services such as S3 run on Regions and AZs; CloudTrail records every call; billing meters usage.',
    svc(60, 40, 'user', 'You', 'CloudShell', 'blue', k='you') +
    link(96, 66, 150, 66, k='req', label='signed HTTPS') +
    grp('cloud', 150, 14, 470, 190, 'AWS Cloud', k='cloud') +
    svc(215, 40, 'app', 'API endpoint', 'sts / ssm / s3', 'amber', k='api', w=80) +
    svc(215, 120, 'shield', 'IAM', 'allowed?', 'red', k='iam') + link(215, 93, 215, 118, k='auth') +
    grp('region', 290, 30, 180, 160, 'Region ap-south-1', k='region') +
    svc(335, 60, 'list', 'SSM params', 'service list', 'violet', k='ssm') + svc(425, 60, 'bucket', 'S3', 'your buckets', 'green', k='s3') +
    svc(380, 130, 'clock', 'CloudTrail', 'event history', 'card', k='trail', w=80) +
    svc(550, 60, 'meter', 'Billing', 'us-east-1', 'amber', k='bill') + svc(550, 130, 'chart', 'Free Tier', 'usage vs limit', 'green', k='free', w=76) +
    link(256, 66, 296, 66, k='call'), h=214)

SIM = simlab(dict(title='Explore AWS from CloudShell', intro='Type real commands in <b>CloudShell</b> (or use the <b>Console</b> tab where a step has one). Watch which part of AWS each command touches.',
  diagram=SIMD, lit=['you'],
  free=[dict(re=r'^aws configure list$', out='      Name                    Value             Type    Location\n      ----                    -----             ----    --------\n   profile                <not set>             None    None\n access_key     ****************WXYZ     container-role\n secret_key     ****************abcd     container-role\n    region               ap-south-1              env    AWS_REGION')],
  steps=[
   dict(title='Who am I?', goal='Prove you are signed in as a user, not root.', hint='STS answers “who is calling”.', answer='aws sts get-caller-identity',
        cli=[dict(re=r'^aws sts get-caller-identity( --query \S+)?( --output \w+)?$', out='{\n    "UserId": "AIDA5EXAMPLE{rnd}",\n    "Account": "{acct}",\n    "Arn": "arn:aws:iam::{acct}:user/{you}"\n}')],
        lights=['req', 'api', 'auth', 'iam'], explain='The CLI signed a <code>GetCallerIdentity</code> request with SigV4 and sent it to the STS endpoint. AWS verified the signature and returned your identity. This call works even with zero permissions — it is the first thing to run when debugging.'),
   dict(title='Count services in Mumbai', goal='Count the services offered in <code>ap-south-1</code> using the public SSM parameters.', hint='Path: <code>/aws/service/global-infrastructure/regions/ap-south-1/services</code>, query <code>length(Parameters)</code>.',
        answer="aws ssm get-parameters-by-path --path /aws/service/global-infrastructure/regions/ap-south-1/services --query 'length(Parameters)'",
        cli=[dict(re=r"^aws ssm get-parameters-by-path --path /aws/service/global-infrastructure/regions/ap-south-1/services( --query '?length\(Parameters\)'?)?( --output \w+)?$", out='261\n(simulated number — run it on your account for today’s real count)')],
        errors=[dict(re=r'^aws ssm get-parameters-by-path --path /aws/service/global-infrastructure/regions/ap-south-1$', out='{\n    "Parameters": [ … only the Region’s own details … ]\n}\nAdd /services to the path to list services.', ok=True)],
        lights=['call', 'region', 'ssm'], explain='AWS publishes Region and service availability as public Parameter Store values. The CLI fetched them page by page (pagination is automatic) and JMESPath <code>length()</code> counted them on your side.'),
   dict(title='List your buckets', goal='List the S3 buckets in your account.', hint='<code>aws s3 ls</code> or <code>aws s3api list-buckets</code>.', answer='aws s3 ls',
        cli=[dict(re=r'^aws s3 ls$', out='2026-11-02 10:14:09 tiffingo-menu-{rnd}\n2026-11-05 18:40:51 tiffingo-logs-{rnd}'), dict(re=r"^aws s3api list-buckets( --query .*)?( --output \w+)?$", out='{\n    "Buckets": [\n        {"Name": "tiffingo-menu-{rnd}", "CreationDate": "2026-11-02T10:14:09+00:00"},\n        {"Name": "tiffingo-logs-{rnd}", "CreationDate": "2026-11-05T18:40:51+00:00"}\n    ]\n}')],
        console=dict(crumbs='S3 › General purpose buckets', fields=[dict(label='Find buckets by name', ph='(leave empty to list all)', re=r'.*')], button='Refresh', out='2 buckets: tiffingo-menu-{rnd}, tiffingo-logs-{rnd}'),
        lights=['s3'], explain='Opening the S3 console page and typing <code>aws s3 ls</code> both send the same <b>ListBuckets</b> API call. The console is just another API client.'),
   dict(title='Find your calls in CloudTrail', goal='Show the recent <code>ListBuckets</code> events and who made them.', hint='<code>aws cloudtrail lookup-events --lookup-attributes AttributeKey=EventName,AttributeValue=ListBuckets</code>',
        answer='aws cloudtrail lookup-events --lookup-attributes AttributeKey=EventName,AttributeValue=ListBuckets --max-results 5',
        cli=[dict(re=r'^aws cloudtrail lookup-events --lookup-attributes AttributeKey=EventName,AttributeValue=ListBuckets( --max-results \d+)?( --query .*)?( --output \w+)?$', out='EventTime                  Username     EventSource          UserAgent\n2026-11-12T10:21:44+05:30  {you}   s3.amazonaws.com     aws-cli/2.x (CloudShell)\n2026-11-12T10:20:02+05:30  {you}   s3.amazonaws.com     console (AWS Management Console)')],
        errors=[dict(re=r'^aws cloudtrail lookup-events --lookup-attributes AttributeKey=EventName,AttributeValue=listbuckets', out='(no events)\nEvent names are case-sensitive: ListBuckets.', ok=True)],
        console=dict(crumbs='CloudTrail › Event history', fields=[dict(label='Lookup attribute', type='select', options=['Event name', 'User name', 'Resource type'], re=r'^Event name$', why='Filter by Event name.'), dict(label='Value', ph='ListBuckets', re=r'^ListBuckets$', why='Event names are case-sensitive: ListBuckets.')], button='Apply', out='2 events: ListBuckets by {you} — one from the CLI, one from the console'),
        lights=['trail'], explain='CloudTrail recorded both calls — same API, different user agents. Event history keeps 90 days of management events free; a <i>trail</i> stores them longer in S3.'),
   dict(title='Check your Free Tier usage', goal='See your account plan and Free Tier usage.', hint='Billing APIs live in us-east-1: <code>aws freetier get-account-plan-state --region us-east-1</code>.', answer='aws freetier get-account-plan-state --region us-east-1',
        cli=[dict(re=r'^aws freetier get-account-plan-state --region us-east-1( --query .*)?$', out='{\n    "accountId": "{acct}",\n    "accountPlanType": "FREE",\n    "accountPlanStatus": "ACTIVE",\n    "accountPlanRemainingCredits": {"amount": 187.42, "unit": "USD"},\n    "accountPlanExpirationDate": "2027-04-30T00:00:00+00:00"\n}'), dict(re=r'^aws freetier get-free-tier-usage --region us-east-1( --query .*)?( --output \w+)?$', out='Service         Description                          Actual   Limit\nAmazon S3       5 GB of Standard storage             0.4      5\nAWS Lambda      1M free requests per month           1210     1000000')],
        errors=[dict(re=r'^aws freetier get-account-plan-state$', out='Could not connect to the endpoint URL: "https://freetier.ap-south-1.amazonaws.com/"\n→ The Free Tier API is served from us-east-1. Add --region us-east-1.')],
        console=dict(crumbs='Billing and Cost Management › Free Tier', fields=[dict(label='View', type='select', options=['Account plan and credits', 'Free Tier usage'], re=r'.+', why='Choose a view.')], button='View', out='Plan FREE · ACTIVE · credits remaining USD 187.42 · ends 30 Apr 2027'),
        lights=['bill', 'free'], explain='Billing data is global and served from us-east-1 whatever Region you use. The values above are simulated — yours will differ.'),
  ]))

ROLES = by_role('Cloud is not one job. The same AWS account is used very differently by each role — here is what each one actually touches in a normal week.', [
 ('Software developer (backend)', 'Builds APIs and services; wants fast, repeatable environments.', 'EC2 or containers (ECS/Fargate), Lambda, RDS/DynamoDB, SQS, CloudWatch Logs, SDKs (boto3, AWS SDK for Java/JS), CodeBuild/GitHub Actions.', 'Ship an order API: code in Git → CI builds a container → deployed to ECS → logs and errors visible in CloudWatch.', 'IAM roles for apps (no keys in code), SDK retries/pagination, reading CloudWatch logs.'),
 ('App / mobile developer', 'Builds web and mobile front ends; wants sign-in, storage and APIs without running servers.', 'Amplify, Cognito (user sign-up/login), API Gateway + Lambda, S3 + CloudFront, DynamoDB, SNS push.', 'TiffinGo app: users sign in with Cognito, upload a profile photo to S3 with a pre-signed URL, get push notifications.', 'Pre-signed URLs, CORS, Cognito tokens, CDN caching.'),
 ('Data analyst', 'Answers business questions with SQL and dashboards; does not want to manage clusters.', 'Athena (SQL on S3), QuickSight dashboards, Redshift (warehouse), Glue Data Catalog, S3 exports.', '“Which locality orders most after 9 pm?” — query a month of order logs in S3 with Athena, chart it in QuickSight.', 'SQL on files, partitions, cost per query (Athena bills by data scanned).'),
 ('Data engineer', 'Builds pipelines that move and clean data reliably.', 'S3 data lake, Glue (ETL, crawlers), EMR (Spark), Kinesis (streams), Step Functions/MWAA (orchestration), Lake Formation (permissions), Redshift.', 'Nightly: raw orders land in <code>s3://lake/raw/</code> → Glue job cleans to Parquet in <code>curated/</code> → partitions registered → analysts query.', 'Partitioning, file formats (Parquet), idempotent jobs, IAM for data access.'),
 ('ML / AI engineer', 'Trains, deploys and monitors models; increasingly builds generative-AI features.', 'SageMaker (notebooks, training, endpoints), Bedrock (foundation models via API, knowledge bases), S3 for datasets, GPU instances, CloudWatch for model metrics.', 'Demand forecast trained on SageMaker; a support chatbot answering from TiffinGo’s FAQ using a Bedrock knowledge base.', 'GPU cost control, data security, model endpoints and monitoring.'),
 ('DevOps / cloud engineer', 'Owns accounts, networks, deployments, reliability and cost.', 'Organizations, IAM Identity Center, VPC, CloudFormation/CDK/Terraform, CloudWatch alarms, Systems Manager, Budgets.', 'Create dev and prod environments from the same template; alarms page on-call; monthly cost review.', 'Infrastructure as code, networking, incident response, FinOps.'),
 ('Security engineer', 'Makes sure everything above is safe and auditable.', 'IAM Access Analyzer, CloudTrail, GuardDuty, Security Hub, KMS, Config rules, WAF.', 'Detect a public bucket within minutes and auto-remediate; prove to auditors who accessed customer data.', 'Least privilege, logging, detection and response.')])

DOMAINS = by_domain('Industry changes the rules more than the services. The same building blocks are combined differently — and regulators decide some choices for you.', [
 ('Banking, NBFC, fintech (BFSI)', 'core banking add-ons, UPI/payments, loan apps, fraud scoring', 'workloads in ap-south-1/ap-south-2, KMS encryption with customer-managed keys, CloudTrail to a locked log account, private connectivity (Direct Connect), multi-AZ databases', 'RBI rules on outsourcing and payment-data storage in India; CERT-In 6-hour incident reporting; DPDP Act for personal data; PCI DSS for card data'),
 ('Healthcare and diagnostics', 'patient records, lab reports, telemedicine, imaging', 'S3 with encryption and versioning, strict IAM, audit logs, HL7/FHIR APIs (AWS HealthLake), long-term archive tiers', 'DPDP Act (health data is personal data), ABDM guidelines for digital health in India; HIPAA for US patients'),
 ('Retail and e-commerce', 'catalogue, orders, payments, recommendations, festival-sale peaks', 'CloudFront + S3 for images, Auto Scaling/containers, DynamoDB for carts, ElastiCache, SQS for order queues, Personalize/Bedrock for recommendations', 'load-test before sales; PCI DSS for card data; DPDP for customer data'),
 ('Education and ed-tech', 'LMS, video lectures, exams, assignments', 'S3 + CloudFront for video, lifecycle rules for old submissions, Cognito for student logins, Auto Scaling for result days', 'student data is personal data (DPDP; extra care for minors’ data); exam-day capacity planning'),
 ('Manufacturing and IoT', 'sensor data, predictive maintenance, plant dashboards', 'IoT Core, Kinesis, Timestream, S3 data lake, Greengrass at the edge, SageMaker for anomaly models', 'operational technology (OT) network isolation; edge processing when connectivity is poor'),
 ('Media and entertainment', 'video upload, transcoding, streaming, ads', 'S3, MediaConvert, CloudFront, Spot for batch processing, Lambda triggers', 'content rights by geography (geo-restriction), egress cost is the big bill'),
 ('Government and public sector', 'citizen services, records, dashboards', 'India Regions, MeitY-empanelled offerings for government workloads, strong audit and encryption', 'MeitY cloud empanelment and data-localisation requirements; CERT-In directions')])

NEWBIE = newbie('Imagine you want to start a tiffin business. Instead of buying a big kitchen, you rent a kitchen by the hour — and pay only for the hours you cook. <b>AWS rents computers, storage and software the same way</b>, over the internet.',
  [('Server', 'a computer that runs all day to serve websites or apps'), ('Cloud', 'computers in someone else’s building that you use over the internet'), ('Service', 'one ready-made product, e.g. storage or a database'), ('Region', 'a city/area where AWS has its buildings'), ('API', 'the “order window” through which programs ask AWS to do things')])
LADDER = ladder([
 ('AWS is Amazon renting out computers and storage over the internet, like renting a kitchen by the hour instead of building one.', 'Name three apps you use (UPI, a food app, YouTube) and guess what “computers in the cloud” they need: storing photos, running the app, keeping records.', 'Do you pay for AWS when you are not using it?', 'Mostly no — you pay for what runs or is stored. That is “pay as you go”.'),
 ('AWS has 200+ services in families: compute, storage, databases, networking, security, analytics & AI, management.', 'Open the console’s “All services” page and find one service from each family.', 'Which family does S3 belong to?', 'Storage (object storage).'),
 ('Every click is an API call checked by IAM and logged by CloudTrail; resources live in Regions.', 'Do the hands-on Step 2: find your own ListBuckets calls in CloudTrail.', 'Why do console, CLI and SDK give the same result?', 'They all call the same AWS APIs.'),
 ('Design with the Well-Architected pillars, quotas, cost and support plans in mind.', 'Pick a small app and estimate its monthly cost with the Pricing Calculator; list which pillar each design choice serves.', 'Which pillar is about recovering from failure?', 'Reliability.'),
 ('Explain SigV4, control vs data plane, eventual consistency and global vs regional services, and use them to debug real failures.', 'Run a CLI command with --debug and identify the endpoint, credential source and signed headers.', 'Why does a wrong system clock break AWS calls?', 'SigV4 signatures include a timestamp; requests outside the allowed window are rejected (SignatureDoesNotMatch / expired).')])
