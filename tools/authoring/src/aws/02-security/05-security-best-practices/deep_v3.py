from cloudkit import *

LADDER = ladder([
 ('Security = locks (prevent), CCTV (record), a guard (detect) and an alarm (respond). AWS secures its buildings; you secure your account settings and data.',
  'List the locks, CCTV, guard and alarm of your college or office building. Then match each to an AWS service from this lesson.',
  'Who is responsible for locking your AWS “doors” (MFA, permissions)?', 'You — AWS secures the cloud itself; you secure what you put in it.'),
 ('Know the ten baseline settings and which service does what: CloudTrail records, GuardDuty detects, Security Hub collects.',
  'Do hands-on Step 1 (CloudTrail trail) or the simulator.',
  'Which service tells you who deleted a bucket?', 'CloudTrail.'),
 ('Enable GuardDuty, generate sample findings, route high severity to e-mail with EventBridge + SNS.',
  'Do hands-on Steps 2–3 and receive the alert e-mail.',
  'GuardDuty vs Inspector?', 'GuardDuty detects active threats from logs; Inspector finds software vulnerabilities and exposure.'),
 ('Automate response (Lambda to deactivate keys/isolate instances), Config rules with remediation, Security Hub standards and posture score.',
  'Write a Lambda that, given a GuardDuty finding for an IAM user, deactivates that user’s access keys; test with a sample finding.',
  'Why snapshot an instance before terminating it during an incident?', 'To preserve evidence (disk contents) for investigation.'),
 ('Run security at organisation scale: delegated administrators, org-wide GuardDuty/Security Hub, log archive account, SCP guard-rails, incident playbooks, regulatory reporting timelines.',
  'Design a multi-account security architecture for a fintech: accounts, delegated admins, log flows, SCPs, playbooks.',
  'CERT-In requires reporting within how many hours?', 'Six hours from noticing specified incidents (April 2022 directions); plus 180-day log retention in India.')])

HOOD = under_hood('How the detection services work internally — and what they cost.', [
 ('1 · Where GuardDuty gets its data',
  '<p>GuardDuty reads CloudTrail management events, VPC Flow Logs and Route 53 DNS query logs <b>directly from AWS’s internal streams</b> — you do not need to enable flow logs or pay for them separately for GuardDuty. Optional protection plans add S3 data events, EKS audit logs and runtime monitoring, RDS login activity, Lambda network activity and malware scanning of EBS volumes and S3 objects.</p>'),
 ('2 · Finding types read like sentences',
  '<p><code>ThreatPurpose:ResourceType/ThreatFamily.Detail!Artifact</code> — e.g. <code>CryptoCurrency:EC2/BitcoinTool.B!DNS</code> means “an EC2 instance queried a domain associated with Bitcoin mining”. Severity 7.0–8.9 = High, 9.0–10 = Critical (newer attack-sequence findings), 4.0–6.9 = Medium.</p>'),
 ('3 · Config vs CloudTrail vs Security Hub CSPM',
  table(['Service', 'Stores', 'Typical question'], [['CloudTrail', 'API events', 'who changed the security group at 3 pm?'], ['Config', 'resource configuration snapshots', 'what did it look like before, and is it compliant?'], ['Security Hub CSPM', 'results of controls (many built on Config rules)', 'how many best-practice checks fail?']], minw=520)),
 ('4 · Organisation-wide security',
  '<p>In AWS Organizations you designate a <b>delegated administrator</b> account for GuardDuty, Security Hub, Inspector, Macie and Config aggregation; new accounts are enrolled automatically. A separate <b>log archive</b> account receives the organisation CloudTrail, with SCPs preventing anyone in member accounts from stopping or deleting it.</p>'),
 ('5 · Cost picture (learning account)',
  table(['Service', 'Free trial / free part', 'After that'], [['CloudTrail', 'event history free; first trail copy of management events free', 'S3 storage; data events extra'], ['GuardDuty', '30-day free trial', 'by volume of events/logs analysed — small for small accounts'], ['Security Hub / CSPM', '30-day trial', 'per check / per resource'], ['Config', '—', 'per configuration item recorded + per rule evaluation'], ['Inspector', '15-day trial', 'per instance/image/function scanned']], minw=520) +
  '<p>Turn them on in learning accounts during labs; in real accounts they are among the cheapest insurance you can buy.</p>'),
])

ROLES = by_role('Security is everyone’s job — here is each role’s part.', [
 ('Software developer (backend)', 'Writes secure code and responds to findings in their services.', 'Secrets Manager, Inspector findings for their images, CodeGuru/linters, dependency updates.', 'Inspector flags a vulnerable library in the order-service image; developer bumps the version and redeploys.', 'Dependency hygiene, secret handling.'),
 ('App / mobile developer', 'Protects front ends and APIs.', 'WAF on CloudFront/API Gateway, Cognito, HTTPS, Shield Standard (automatic).', 'Add a WAF rate-based rule after a login brute-force attempt.', 'WAF rules, auth flows.'),
 ('Data analyst', 'Handles sensitive data carefully.', 'Macie findings, Lake Formation permissions, masked datasets.', 'Uses the masked customer table, not raw PII.', 'Data classification awareness.'),
 ('Data engineer', 'Keeps data platforms secure and auditable.', 'CloudTrail data events for S3, Macie on landing zones, KMS per zone, Lake Formation.', 'Macie flags PAN-like values in raw/ — pipeline adds masking before curated/.', 'Data security controls in pipelines.'),
 ('ML / AI engineer', 'Secures training data, models and AI endpoints.', 'GuardDuty for SageMaker/EKS, Bedrock Guardrails, private endpoints, KMS.', 'A chatbot uses Bedrock Guardrails to block personal data in responses.', 'AI-specific risks (prompt injection, data leakage).'),
 ('DevOps / cloud engineer', 'Builds the baseline and automation.', 'Organizations, Control Tower, org-wide GuardDuty/Security Hub, EventBridge, SSM.', 'New accounts are born with the baseline via Control Tower; findings flow to a central account.', 'Security automation at scale.'),
 ('Security engineer', 'Detects, responds, reports.', 'Security Hub, GuardDuty, Detective, Athena on CloudTrail, incident runbooks.', 'Runs the Monday incident review and files the CERT-In report within 6 hours when required.', 'Investigation, playbooks, regulation.')])

DOMAINS = by_domain('Security baselines and obligations by industry.', [
 ('Banking / fintech', 'payments, lending', 'org-wide GuardDuty + Security Hub, log archive account, SCPs, 24×7 SOC integration', 'RBI cyber-security framework; CERT-In 6 h; DPDP 72 h detailed report'),
 ('Healthcare', 'patient data', 'Macie on all buckets with PHI, Inspector, strict CloudTrail data events', 'DPDP/ABDM; HIPAA for US patients'),
 ('Retail / e-commerce', 'sales peaks, payments', 'WAF + Shield on storefronts, GuardDuty, automated isolation', 'PCI DSS logging and monitoring'),
 ('Education', 'student portals, exams', 'baseline per lab account, alerts to faculty admin, Secrets Manager for portal DB', 'student data under DPDP; exam integrity'),
 ('Manufacturing / IoT', 'plants, devices', 'IoT Device Defender, network isolation, GuardDuty', 'OT safety; incident response with plant teams'),
 ('Government', 'citizen services', 'India Regions, central logging 180+ days, SOC integration', 'CERT-In directions; MeitY guidelines')])

PRO = (
 '  <h3>Security commands worth memorising</h3>\n' + cheatsheet([
   ('aws cloudtrail lookup-events --lookup-attributes AttributeKey=AccessKeyId,AttributeValue=AKIA…', 'everything a key did (last 90 days)'),
   ('aws iam update-access-key --user-name U --access-key-id AKIA… --status Inactive', 'contain a leaked key immediately'),
   ('aws guardduty list-findings --detector-id D --finding-criteria \'{"Criterion":{"severity":{"Gte":7}}}\'', 'high-severity findings'),
   ('aws securityhub get-findings --filters \'{"SeverityLabel":[{"Value":"CRITICAL","Comparison":"EQUALS"}]}\'', 'critical findings in Security Hub'),
   ('aws configservice describe-compliance-by-config-rule', 'which rules are failing'),
   ('aws ec2 create-snapshot --volume-id vol-… --description "incident evidence"', 'preserve evidence before cleanup'),
   ('aws ec2 modify-instance-attribute --instance-id i-… --groups sg-isolation', 'isolate an instance (empty security group)')]) +
 '  <h3>Errors and surprises</h3>\n' + errors_table([
   ('InsufficientS3BucketPolicyException: Incorrect S3 bucket policy is detected for bucket', 'create-trail', 'bucket policy does not let CloudTrail write', 'add the GetBucketAcl + PutObject statements for cloudtrail.amazonaws.com'),
   ('BadRequestException: The request is rejected because a detector already exists for the current account', 'create-detector', 'GuardDuty already on in this Region', 'use list-detectors to get the existing ID'),
   ('No alert e-mails arrive', 'EventBridge → SNS', 'subscription not confirmed, or topic policy does not allow events.amazonaws.com', 'confirm the e-mail; set the topic policy'),
   ('InvalidAccessException: Account … is not subscribed to AWS Security Hub', 'securityhub calls', 'Security Hub not enabled in that Region', 'enable it (or the CSPM part) first'),
   ('Findings only from one Region', 'investigations', 'services enabled in one Region only', 'enable in all used Regions; deny unused Regions with SCPs')]) +
 checklist('Monthly security review (30 minutes)', ['Security Hub posture score trend; top 5 failing controls assigned.', 'All High/Critical GuardDuty findings closed with notes.', 'Credential report: no unused keys, MFA everywhere.', 'Access Analyzer: no unexpected external access; unused access trimmed.', 'Inspector criticals patched.', 'One incident drill with sample findings.']) +
 refs([('AWS Security Reference Architecture', 'https://docs.aws.amazon.com/prescriptive-guidance/latest/security-reference-architecture/welcome.html'), ('Amazon GuardDuty user guide', 'https://docs.aws.amazon.com/guardduty/latest/ug/what-is-guardduty.html'), ('AWS Security Hub user guide', 'https://docs.aws.amazon.com/securityhub/latest/userguide/what-is-securityhub.html'), ('AWS Security Incident Response guide', 'https://docs.aws.amazon.com/whitepapers/latest/aws-security-incident-response-guide/welcome.html')])
)

PROJ = projects([
 ('Basic', 'Baseline audit of your learning account', 'Check your own account against the ten-setting baseline.',
  ['Go through the baseline picture item by item.', 'Mark each as done / missing with evidence (CLI output or screenshot).', 'Fix three missing items.'],
  'A ten-row table with evidence.', 'Turn on Security Hub CSPM for 30 days and record the score.'),
 ('Intermediate', 'Detection-to-alert pipeline', 'Make sure a high-severity finding reaches you within minutes.',
  ['CloudTrail trail + GuardDuty.', 'EventBridge rule severity ≥ 7 → SNS e-mail (and SMS if allowed).', 'Generate a sample finding; time how long the e-mail takes.', 'Write a one-page runbook: who acts, first three commands.'],
  'Pipeline screenshots, timing, runbook.', 'Add a Lambda target that posts to a chat channel webhook.'),
 ('Advanced', 'Automated key containment', 'If a key is used anomalously, disable it automatically and preserve evidence.',
  ['Lambda (role: iam:UpdateAccessKey, cloudtrail:LookupEvents) triggered by GuardDuty IAM findings.', 'Deactivate the key named in the finding; store the last 50 events of that key in S3.', 'Notify via SNS with a summary.', 'Test with a sample finding and a test user’s key.'],
  'Code, IAM policy, test evidence, and risks of auto-remediation.', 'Add an approval step with Step Functions for production accounts.')])

SIMD = awsfig('Lab map: CloudTrail trail to S3; GuardDuty detector with sample findings; EventBridge rule severity ≥ 7; SNS topic security-alerts; e-mail received.',
    grp('acct', 10, 10, 620, 210, 'AWS account {acct} — security baseline', k='acct') +
    svc(80, 50, 'clock', 'CloudTrail', 'trail: baseline', 'card', k='trail', w=86) + svc(80, 140, 'bucket', 'trail-{acct}', 'logs + digests', 'green', k='tb', w=96) + link(80, 104, 80, 138, k='tl') +
    svc(230, 95, 'shield', 'GuardDuty', 'detector', 'amber', k='gd', w=86) + link(124, 76, 186, 104, k='feed') +
    svc(360, 50, 'file', 'Sample findings', 'severity ≥ 7', 'red', k='find', w=96) + link(274, 112, 312, 80, k='fl') +
    svc(360, 150, 'gear', 'EventBridge', 'guardduty-high', 'blue', k='eb', w=96) + link(360, 104, 360, 148, k='el') +
    svc(500, 150, 'mail', 'SNS', 'security-alerts', 'green', k='sns', w=86) + link(408, 176, 456, 176, k='sl') +
    svc(570, 50, 'user', 'You', 'alert e-mail', 'violet', k='you', w=80) + link(530, 150, 560, 104, k='ml'), h=230)

SIM = simlab(dict(title='Turn on detection and get your first alert', intro='Create the trail, enable GuardDuty, generate sample findings and route high severity to your e-mail.',
  diagram=SIMD, lit=['acct'],
  steps=[
   dict(title='CloudTrail trail (all Regions)', goal='Create trail <code>baseline</code> to bucket <code>trail-{acct}</code>, multi-Region, with log file validation.', hint='<code>aws cloudtrail create-trail --name baseline --s3-bucket-name trail-{acct} --is-multi-region-trail --enable-log-file-validation</code>',
        answer='aws cloudtrail create-trail --name baseline --s3-bucket-name trail-{acct} --is-multi-region-trail --enable-log-file-validation',
        cli=[dict(re=r'^aws cloudtrail create-trail --name baseline --s3-bucket-name trail-{acct}( --is-multi-region-trail| --enable-log-file-validation){2}( --query .*)?$', out='{\n    "Name": "baseline",\n    "S3BucketName": "trail-{acct}",\n    "IsMultiRegionTrail": true,\n    "LogFileValidationEnabled": true,\n    "TrailARN": "arn:aws:cloudtrail:ap-south-1:{acct}:trail/baseline"\n}')],
        errors=[dict(re=r'^aws cloudtrail create-trail --name baseline --s3-bucket-name trail-{acct}$', out='Created — but single-Region and without validation. Attackers love unwatched Regions. Add --is-multi-region-trail --enable-log-file-validation.'),
                dict(re=r'^aws cloudtrail create-trail .*--s3-bucket-name (?!trail-{acct})\S+', out='An error occurred (InsufficientS3BucketPolicyException): Incorrect S3 bucket policy is detected for bucket …\n→ Use trail-{acct}, whose policy lets CloudTrail write.')],
        console=dict(crumbs='CloudTrail › Trails › Create trail', fields=[dict(label='Trail name', ph='baseline', re=r'^baseline$', why='Name it baseline.'), dict(label='Log file validation', type='check', must=True, why='Enable log file validation.'), dict(label='Apply to all Regions', type='check', must=True, why='Multi-Region trail.')], button='Create trail', out='Trail baseline created · all Regions · validation on'),
        lights=['trail', 'tb', 'tl'], explain='From now on every management event in every Region is written to S3, with hourly digest files that prove logs were not altered — evidence for auditors and investigators.'),
   dict(title='Enable GuardDuty', goal='Create a GuardDuty detector in ap-south-1.', hint='<code>aws guardduty create-detector --enable</code>', answer='aws guardduty create-detector --enable',
        cli=[dict(re=r'^aws guardduty create-detector --enable( --query .*)?( --output \w+)?$', out='{\n    "DetectorId": "12abc34d567e8fa901bc2d34e56789f0"\n}')],
        console=dict(crumbs='GuardDuty › Get started', fields=[dict(label='Enable GuardDuty (30-day free trial)', type='check', must=True, why='Tick to enable.')], button='Enable GuardDuty', out='GuardDuty enabled · detector 12abc34d…'),
        lights=['gd', 'feed'], explain='GuardDuty now reads CloudTrail, VPC Flow Logs and DNS logs from AWS’s internal streams — no agents, no extra log charges.'),
   dict(title='Generate sample findings', goal='Generate sample findings and list the high-severity ones.', hint='<code>aws guardduty create-sample-findings --detector-id 12abc34d567e8fa901bc2d34e56789f0</code>', answer='aws guardduty create-sample-findings --detector-id 12abc34d567e8fa901bc2d34e56789f0',
        cli=[dict(re=r'^aws guardduty create-sample-findings --detector-id 12abc34d567e8fa901bc2d34e56789f0( --finding-types .*)?$', out='(sample findings created)\n$ aws guardduty get-findings … --query Findings[].[Type,Severity]\nCryptoCurrency:EC2/BitcoinTool.B!DNS                         8\nUnauthorizedAccess:IAMUser/InstanceCredentialExfiltration.OutsideAWS   8\nBackdoor:EC2/C&CActivity.B!DNS                               8')],
        errors=[dict(re=r'^aws guardduty create-sample-findings$', out='aws: error: the following arguments are required: --detector-id')],
        console=dict(crumbs='GuardDuty › Settings › Sample findings', fields=[dict(label='Generate sample findings', type='check', must=True, why='Tick to generate.')], button='Generate', out='Sample findings generated — filter Severity: High to view'),
        lights=['find', 'fl'], explain='Each sample is marked [SAMPLE] and harmless, but looks exactly like a real finding — ideal for testing alerts and runbooks.'),
   dict(title='EventBridge rule severity ≥ 7', goal='Create rule <code>guardduty-high</code> matching GuardDuty findings with severity ≥ 7.', hint='<code>aws events put-rule --name guardduty-high --event-pattern file://pattern.json</code>', answer='aws events put-rule --name guardduty-high --event-pattern file://pattern.json',
        cli=[dict(re=r'^aws events put-rule --name guardduty-high --event-pattern (file://\S+|.+)$', out='{\n    "RuleArn": "arn:aws:events:ap-south-1:{acct}:rule/guardduty-high"\n}')],
        console=dict(crumbs='EventBridge › Rules › Create rule', fields=[dict(label='Event source', type='select', options=['AWS events', 'Partner events'], re=r'^AWS events$', why='AWS events.'), dict(label='Pattern: severity ≥', ph='7', re=r'^7$', why='Use 7 (High and above).')], button='Next', out='Rule guardduty-high: aws.guardduty, severity ≥ 7'),
        lights=['eb', 'el'], explain='EventBridge receives every GuardDuty finding as an event; the numeric matcher passes only High and Critical ones on.'),
   dict(title='Send to SNS e-mail', goal='Add SNS topic <code>security-alerts</code> as the rule target.', hint='<code>aws events put-targets --rule guardduty-high --targets Id=sns,Arn=arn:aws:sns:ap-south-1:{acct}:security-alerts</code>', answer='aws events put-targets --rule guardduty-high --targets Id=sns,Arn=arn:aws:sns:ap-south-1:{acct}:security-alerts',
        cli=[dict(re=r'^aws events put-targets --rule guardduty-high --targets Id=\w+,Arn=arn:aws:sns:ap-south-1:{acct}:security-alerts$', out='{\n    "FailedEntryCount": 0,\n    "FailedEntries": []\n}\n… 2 minutes later, in your inbox:\n  AWS Notification Message — GuardDuty Finding: CryptoCurrency:EC2/BitcoinTool.B!DNS (severity 8)')],
        errors=[dict(re=r'^aws sns (create-topic --name security-alerts|subscribe .*)$', out='(done — remember to click the confirmation link in the e-mail)', ok=True)],
        console=dict(crumbs='EventBridge › Rules › guardduty-high › Targets', fields=[dict(label='Target', type='select', options=['Lambda function', 'SNS topic', 'SQS queue'], re=r'^SNS topic$', why='Choose SNS topic.'), dict(label='Topic', ph='security-alerts', re=r'^security-alerts$', why='Use security-alerts.')], button='Create rule', out='Target SNS security-alerts added — alert e-mail received'),
        lights=['sns', 'sl', 'you', 'ml'], explain='The chain is complete: GuardDuty → EventBridge → SNS → your inbox in minutes. In production add a Lambda target that also contains the threat automatically.'),
  ]))
