from cloudkit import *

HOOD = under_hood('What sits behind the Region selector — the details architects and SREs rely on.', [
 ('1 · AZ names are shuffled per account; AZ IDs are not',
  '<p>When you see <code>ap-south-1a</code>, AWS has mapped that name to one physical AZ <b>for your account</b>. Another account’s <code>ap-south-1a</code> may be a different AZ. The <b>AZ ID</b> (<code>aps1-az1</code>, <code>aps1-az2</code>, <code>aps1-az3</code>) is the same for everyone. Use IDs when you share subnets (VPC sharing), coordinate a migration with a vendor, or read an AWS Health event that names an AZ.</p>' +
  code('bash', 'See your mapping', "aws ec2 describe-availability-zones --region ap-south-1 --query 'AvailabilityZones[].{Name:ZoneName,Id:ZoneId}' --output table")),
 ('2 · How far apart and how fast',
  '<p>AWS states AZs in a Region are separated by a meaningful distance — many kilometres — yet all within 100 km, linked by redundant, dedicated fibre with low latency (typically low single-digit milliseconds round trip), fast enough for <b>synchronous replication</b> (RDS Multi-AZ, EBS-backed services, Aurora storage across 3 AZs). Between Regions, latency follows distance: light in fibre covers roughly 200 km per millisecond, so Mumbai → N. Virginia (~13,000 km) can never be faster than about 65 ms one way, and real paths are longer.</p>'),
 ('3 · Partitions: worlds that do not share accounts',
  '<p>Regions are grouped into <b>partitions</b>: <code>aws</code> (commercial Regions, including India), <code>aws-cn</code> (China, operated by local partners, separate accounts), <code>aws-us-gov</code> (GovCloud) and the AWS European Sovereign Cloud. An IAM user in one partition cannot be used in another — the partition is the first field of every ARN: <code>arn:<b>aws</b>:s3:::bucket</code>.</p>'),
 ('4 · Global, regional and zonal — and where the control plane lives',
  table(['Scope', 'Examples', 'Failure blast radius'], [['Global', 'IAM, Route 53, CloudFront, Organizations', 'control plane hosted in one Region (often us-east-1); data plane global and highly available'], ['Regional', 'S3, DynamoDB, Lambda, SQS, VPC', 'service is spread across the Region’s AZs for you'], ['Zonal', 'EC2 instance, EBS volume, subnet, NAT gateway', 'you must spread across AZs yourself']], minw=560) +
  '<p>Lesson: regional managed services (S3, DynamoDB, Lambda) give you multi-AZ for free; zonal resources (EC2, EBS) make multi-AZ <i>your</i> job.</p>'),
 ('5 · Following the money: data-transfer paths',
  table(['Path', 'Typical charge'], [['Internet → AWS (data in)', 'free'], ['Within the same AZ (private IP)', 'free'], ['Between AZs in a Region', 'charged per GB in each direction (≈ USD 0.01/GB each way)'], ['Between Regions', 'charged per GB (varies by Region pair)'], ['AWS → internet (data out)', 'charged per GB after the first 100 GB/month free'], ['Origin → CloudFront', 'free; CloudFront → users charged at CDN rates']], minw=480) +
  '<p>Architects watch these paths: a chatty service calling a database in another AZ millions of times a day can cost more than the servers.</p>'),
])

ROLES = by_role('Every role meets global infrastructure, but at a different layer.', [
 ('Software developer (backend)', 'Writes code that must survive an AZ failure.', 'SDK Region config (<code>AWS_REGION</code>), multi-AZ RDS endpoints, retries with backoff, health-check endpoints (<code>/health</code>).', 'Make the order API stateless so any instance in any AZ can serve any request; keep sessions in ElastiCache/DynamoDB, not on the server.', 'Statelessness, idempotent retries, timeouts.'),
 ('App / mobile developer', 'Wants fast screens for users far away.', 'CloudFront in front of S3/API Gateway, Route 53 latency routing, Amplify hosting.', 'Dubai users load the menu photos from a nearby edge; API calls still go to Mumbai.', 'Caching headers (Cache-Control), CDN invalidations.'),
 ('Data analyst', 'Must know where data lives before querying or sharing it.', 'Athena/QuickSight in the same Region as the data; cross-Region queries cost transfer.', 'A Mumbai data lake queried from a Singapore QuickSight account → slow and charged; move the dashboard to ap-south-1.', 'Data locality and residency.'),
 ('Data engineer', 'Designs where pipelines run and how data is replicated.', 'S3 Cross-Region Replication, Glue/EMR in the data’s Region, DynamoDB global tables.', 'Replicate the curated zone to Hyderabad for DR; keep raw data only in Mumbai to save cost.', 'Replication, partition placement, transfer cost.'),
 ('ML / AI engineer', 'GPU and model availability differ by Region.', 'Check SageMaker instance types and Bedrock model availability per Region; training data in the same Region.', 'A foundation model is not yet in Mumbai — use cross-Region inference only if data rules allow, otherwise wait or self-host.', 'Region availability checks, data residency for training data.'),
 ('DevOps / cloud engineer', 'Implements the resilience ladder.', 'Subnets in every AZ, Auto Scaling across AZs, Route 53 failover, AWS Backup cross-Region copies, AWS Health events.', 'Game day: simulate an AZ failure (AWS Fault Injection Service) and prove the app survives.', 'Multi-AZ by default, DR runbooks, chaos testing.'),
 ('Security engineer', 'Enforces “data stays in India”.', 'SCP denying actions outside approved Regions (<code>aws:RequestedRegion</code>), Config rules, CloudTrail in all Regions.', 'Block any resource creation outside ap-south-1/ap-south-2 for the bank’s accounts.', 'Region guard-rails, multi-Region logging.')])

DOMAINS = by_domain('Region and AZ choices are often decided by the industry.', [
 ('Banking / fintech', 'payments, lending, UPI', 'ap-south-1 multi-AZ + DR in ap-south-2; SCPs limiting Regions', 'RBI payment-data storage in India; documented DR drills'),
 ('Healthcare', 'patient records, imaging', 'India Regions; Outposts or on-premises for scanners; encrypted cross-Region backups', 'DPDP; ABDM; data residency in contracts'),
 ('Retail / e-commerce', 'festival-sale traffic', 'multi-AZ Auto Scaling, CloudFront for images, Route 53 health checks', 'load-test per AZ capacity; N+1 sizing'),
 ('Education', 'exams, video lectures', 'Mumbai Region, CloudFront for video to all states, Local Zones rarely needed', 'exam-day peaks; student data under DPDP'),
 ('Gaming / live media', 'real-time multiplayer, live streaming', 'Delhi/Kolkata Local Zones for game servers, CloudFront/IVS for streams', 'latency budgets per city'),
 ('Manufacturing / IoT', 'factory lines, sensors', 'Outposts or Greengrass at the plant, data lake in the Region', 'plant keeps working if the internet link drops'),
 ('Government', 'citizen portals', 'India Regions only, MeitY-empanelled offerings', 'MeitY and CERT-In requirements')])

PRO = (
 '  <h3>Commands architects run in the first hour on a new account</h3>\n' + cheatsheet([
   ("aws ec2 describe-regions --all-regions --query 'Regions[].[RegionName,OptInStatus]' --output table", 'which Regions are enabled'),
   ("aws ec2 describe-availability-zones --region ap-south-1 --query 'AvailabilityZones[].[ZoneName,ZoneId]' --output table", 'AZ name → AZ ID mapping'),
   ('aws ec2 describe-availability-zones --region ap-south-1 --all-availability-zones --filters Name=zone-type,Values=local-zone', 'Local Zones and opt-in status'),
   ('aws ec2 modify-availability-zone-group --group-name ap-south-1-del-1 --opt-in-status opted-in', 'enable the Delhi Local Zone'),
   ('aws account enable-region --region-name ap-south-2', 'enable an opt-in Region (Hyderabad)'),
   ('aws ec2 describe-instance-type-offerings --location-type availability-zone-id --filters Name=instance-type,Values=g5.xlarge --region ap-south-1', 'which AZs offer an instance type'),
   ('aws health describe-events --region us-east-1 --filter eventStatusCodes=open', 'open AWS Health events (needs Business Support+ or higher for the API)')]) +
 cost_calc('Worked example: the price of multi-AZ for TiffinGo (Mumbai)', [
   ['Second t3.small web server (other AZ)', '730 h', '≈ USD 0.022 / h', '≈ USD 16'],
   ['RDS db.t3.micro Multi-AZ instead of Single-AZ', '730 h', '≈ 2× single-AZ price', '≈ + USD 18'],
   ['Inter-AZ traffic (app ↔ DB)', '100 GB', '≈ USD 0.01 / GB each way', '≈ USD 2'],
   ['Application Load Balancer', '730 h + LCUs', '≈ USD 0.0239 / h + usage', '≈ USD 20']],
   '≈ USD 56 / month extra (≈ ₹4,800)',
   'Approximate ap-south-1 prices; confirm in the Pricing Calculator. Compare with the cost of a two-hour lunch outage: for TiffinGo that is ~600 lost orders.') +
 '  <h3>Errors and surprises</h3>\n' + errors_table([
   ('An error occurred (OptInRequired) when calling the DescribeInstances operation: You are not subscribed to this service', 'calling a Region you have not enabled', 'opt-in Region (e.g. ap-south-2) not enabled', 'enable it in Account → AWS Regions or <code>aws account enable-region</code>'),
   ('Could not connect to the endpoint URL: "https://ec2.ap-south-3.amazonaws.com/"', 'typo in Region', 'no such Region/endpoint', 'check <code>aws ec2 describe-regions</code> for the exact code'),
   ('InsufficientInstanceCapacity: We currently do not have sufficient capacity in the Availability Zone you requested', 'launching a popular instance type', 'temporary capacity shortage in that AZ', 'try another AZ or instance type; use Auto Scaling with several AZs/types'),
   ('Unsupported: Your requested instance type is not supported in your requested Availability Zone', 'Local Zone or specific AZ', 'type not offered there', 'check with describe-instance-type-offerings'),
   ('The subnet ID … does not exist (after copying a template)', 'sharing templates between accounts', 'subnet/AZ names differ per account', 'parameterise subnets; use AZ IDs in docs')]) +
 checklist('Global infrastructure design checklist', ['Region chosen with the four-question test and recorded.', 'Every tier in at least two AZs (subnets, instances, database).', 'Capacity sized to survive losing one AZ (N+1).', 'Backups copied to a second Region (e.g. ap-south-2).', 'Static content behind CloudFront.', 'SCP or policy limits Regions where resources may be created.', 'You know your AZ IDs.']) +
 refs([('Regions and Availability Zones', 'https://aws.amazon.com/about-aws/global-infrastructure/regions_az/'), ('Available Local Zones', 'https://docs.aws.amazon.com/local-zones/latest/ug/available-local-zones.html'), ('AZ IDs for your resources', 'https://docs.aws.amazon.com/ram/latest/userguide/working-with-az-ids.html'), ('Reliability pillar — Well-Architected', 'https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html')])
)

PROJ = projects([
 ('Basic', 'Region decision for three businesses', 'Choose Regions for: a Pune coaching institute, a Dubai-and-India spice exporter, and a US-only start-up run from Bengaluru.',
  ['Apply the four-question test to each.', 'State primary Region and DR Region.', 'Say whether CloudFront is needed and why.'],
  'A one-page table with reasons.', 'Add the expected latency from each user base (use the Step 3 loop).'),
 ('Intermediate', 'AZ map and capacity plan', 'TiffinGo needs 6 web servers at lunch peak and must survive losing one AZ.',
  ['Draw the VPC with one public and one private subnet per AZ (3 AZs).', 'Decide how many servers per AZ so that losing any one AZ still leaves ≥ 6 (answer: 3 per AZ = 9 total).', 'Place the database primary and standby.', 'Estimate monthly cost with the Pricing Calculator.'],
  'Diagram + capacity reasoning + cost estimate.', 'Compare with a 2-AZ design (how many servers are then needed?).'),
 ('Advanced', 'Latency and Region-availability report (script)', 'Your company wants data on 6 candidate Regions before a decision.',
  ['Write a Bash or Python script that, for each Region: measures TCP connect time (3 samples, average), counts services from the SSM parameters, and checks if g5 and m7i instance types are offered.', 'Output a CSV and sort by latency.', 'Write a recommendation paragraph.'],
  'Script, CSV and recommendation.', 'Run it from CloudShell in two Regions and explain the differences.')])

SIMD = awsfig('Map: AWS Cloud with Mumbai Region (three AZs), Hyderabad Region, Delhi and Kolkata Local Zones, and an edge location; parts light up as you explore.',
    grp('cloud', 10, 10, 620, 210, 'AWS Cloud (partition aws)', k='cloud') +
    grp('region', 22, 30, 330, 150, 'ap-south-1 Mumbai', k='mum') +
    grp('az', 34, 52, 96, 90, 'aps1-az1', k='az1') + grp('az', 140, 52, 96, 90, 'aps1-az2', k='az2') + grp('az', 246, 52, 96, 90, 'aps1-az3', k='az3') +
    svc(82, 76, 'server', 'DCs', '', 'blue', k='az1', w=60) + svc(188, 76, 'server', 'DCs', '', 'blue', k='az2', w=60) + svc(294, 76, 'server', 'DCs', '', 'blue', k='az3', w=60) +
    grp('region', 364, 30, 120, 70, 'ap-south-2 Hyderabad', k='hyd') +
    grp('onprem', 364, 110, 120, 70, 'Local Zones', k='lz') + t(424, 144, 'Delhi · Kolkata', 7.4, 'ink', bold=True) + t(424, 160, 'parent ap-south-1', 6.2, 'ink2') +
    t(424, 66, 'opt-in Region', 6.8, 'ink2') +
    svc(560, 40, 'globe', 'Edge', 'CloudFront PoP', 'amber', k='edge', w=80) +
    svc(560, 120, 'meter', 'Latency', 'measured', 'green', k='lat', w=80) +
    link(352, 120, 362, 140, k='lzlink'), h=232)

SIM = simlab(dict(title='Explore Regions, AZs and Local Zones', intro='Use real commands (or the Console tab). Watch the map: each step reveals one layer of AWS’s physical world.',
  diagram=SIMD, lit=['cloud'],
  steps=[
   dict(title='List Regions and opt-in status', goal='List all Regions with their opt-in status.', hint='<code>aws ec2 describe-regions --all-regions</code> with a query on RegionName and OptInStatus.', answer="aws ec2 describe-regions --all-regions --query 'Regions[].[RegionName,OptInStatus]' --output table",
        cli=[dict(re=r"^aws ec2 describe-regions --all-regions( --query .*)?( --output \w+)?$", out='-----------------------------------------\n|            DescribeRegions            |\n+-----------------+---------------------+\n|  ap-south-1     |  opt-in-not-required|\n|  ap-south-2     |  not-opted-in       |\n|  ap-southeast-1 |  opt-in-not-required|\n|  me-central-1   |  not-opted-in       |\n|  us-east-1      |  opt-in-not-required|\n|  … (34 more)    |                     |\n+-----------------+---------------------+')],
        errors=[dict(re=r'^aws ec2 describe-regions$', out='(Only enabled Regions are listed.) Add --all-regions to see opt-in Regions such as ap-south-2.', ok=True)],
        console=dict(crumbs='EC2 › Global View › Region explorer', fields=[dict(label='Show', type='select', options=['Enabled Regions', 'All Regions'], re=r'^All Regions$', why='Choose All Regions to see opt-in Regions too.')], button='Refresh', out='39 Regions listed · ap-south-1 Enabled · ap-south-2 Not enabled (opt-in)'),
        lights=['mum', 'hyd'], explain='Regions launched after March 2019 (like Hyderabad) are <b>opt-in</b>: AWS will not create anything there until you enable them. This keeps resources from appearing in Regions you never chose.'),
   dict(title='Map AZ names to AZ IDs', goal='Show the AZ names and AZ IDs for <code>ap-south-1</code>.', hint='<code>aws ec2 describe-availability-zones --region ap-south-1</code>; query ZoneName and ZoneId.', answer="aws ec2 describe-availability-zones --region ap-south-1 --query 'AvailabilityZones[].[ZoneName,ZoneId]' --output table",
        cli=[dict(re=r"^aws ec2 describe-availability-zones( --region ap-south-1)?( --query .*)?( --output \w+)?$", out='----------------------------------\n|   DescribeAvailabilityZones    |\n+--------------+-----------------+\n|  ap-south-1a |  aps1-az3       |\n|  ap-south-1b |  aps1-az1       |\n|  ap-south-1c |  aps1-az2       |\n+--------------+-----------------+\n(this mapping is for this account; yours may differ)')],
        errors=[dict(re=r'^aws ec2 describe-availability-zones --region ap-south-3', out='Could not connect to the endpoint URL: "https://ec2.ap-south-3.amazonaws.com/"\n→ No such Region. Mumbai is ap-south-1.')],
        console=dict(crumbs='EC2 › Settings › Zones', fields=[dict(label='Zone type', type='select', options=['Availability Zones', 'Local Zones', 'Wavelength Zones'], re=r'^Availability Zones$', why='Choose Availability Zones.')], button='Show', out='ap-south-1a → aps1-az3 · ap-south-1b → aps1-az1 · ap-south-1c → aps1-az2'),
        lights=['az1', 'az2', 'az3'], explain='Three isolated AZs, each one or more data centres with its own power and network, within 100 km of each other. In this account “1a” is physically <b>aps1-az3</b> — in another account it could be aps1-az1.'),
   dict(title='Find the Local Zones', goal='List the Local Zones of <code>ap-south-1</code> with their opt-in status.', hint='Add <code>--all-availability-zones --filters Name=zone-type,Values=local-zone</code>.', answer='aws ec2 describe-availability-zones --region ap-south-1 --all-availability-zones --filters Name=zone-type,Values=local-zone',
        cli=[dict(re=r"^aws ec2 describe-availability-zones( --region ap-south-1)? --all-availability-zones --filters Name=zone-type,Values=local-zone( --query .*)?( --output \w+)?$", out='ap-south-1-ccu-1a   aps1-ccu1-az1   not-opted-in   parent aps1-az1   India (Kolkata)\nap-south-1-del-1a   aps1-del1-az1   not-opted-in   parent aps1-az3   India (Delhi)')],
        errors=[dict(re=r"^aws ec2 describe-availability-zones( --region ap-south-1)? --filters Name=zone-type,Values=local-zone$", out='[]\n→ Local Zones you have not opted in to are hidden. Add --all-availability-zones.', ok=True)],
        console=dict(crumbs='EC2 › Settings › Zones › Local Zones', fields=[dict(label='Zone type', type='select', options=['Availability Zones', 'Local Zones', 'Wavelength Zones'], re=r'^Local Zones$', why='Choose Local Zones.')], button='Show', out='India (Delhi) ap-south-1-del-1a · India (Kolkata) ap-south-1-ccu-1a — both Not opted in'),
        lights=['lz', 'lzlink'], explain='Local Zones hang off a parent Region (Mumbai) and offer selected services in Delhi and Kolkata for single-digit-millisecond latency to users there.'),
   dict(title='Opt in to the Delhi Local Zone', goal='Enable the Delhi Local Zone group (free — you pay only for what you launch there).', hint='<code>aws ec2 modify-availability-zone-group --group-name ap-south-1-del-1 --opt-in-status opted-in</code>', answer='aws ec2 modify-availability-zone-group --region ap-south-1 --group-name ap-south-1-del-1 --opt-in-status opted-in',
        cli=[dict(re=r'^aws ec2 modify-availability-zone-group( --region ap-south-1)? --group-name ap-south-1-del-1 --opt-in-status opted-in$', out='{\n    "Return": true\n}')],
        errors=[dict(re=r'^aws ec2 modify-availability-zone-group( --region ap-south-1)? --group-name ap-south-1-del-1a', out='An error occurred (InvalidParameterValue): The zone group name ap-south-1-del-1a is not valid.\n→ Use the group name ap-south-1-del-1 (without the final letter).')],
        console=dict(crumbs='EC2 › Settings › Zones › ap-south-1-del-1 › Manage', fields=[dict(label='Zone group', type='select', options=['ap-south-1-del-1', 'ap-south-1-ccu-1'], re=r'^ap-south-1-del-1$', why='Choose the Delhi group.'), dict(label='Opted in', type='check', must=True, why='Tick Opted in.')], button='Update', out='ap-south-1-del-1 is now Opted in'),
        lights=['lz'], explain='Opting in makes the Delhi zone appear like an extra AZ of Mumbai. Next you would create a subnet in <code>ap-south-1-del-1a</code> and launch supported instance types there.'),
   dict(title='Measure latency to Regions', goal='Measure TCP connect time from CloudShell (Mumbai) to EC2 endpoints in several Regions.', hint='Loop over Regions with <code>curl -s -o /dev/null -w \'%{time_connect}\'</code>. In the simulator, the one-line form works too.', answer="for r in ap-south-1 ap-southeast-1 eu-west-1 us-east-1; do printf '%s ' $r; curl -s -o /dev/null -w '%{time_connect}s\\n' https://ec2.$r.amazonaws.com/; done",
        cli=[dict(re=r"^for r in .*; do .*curl .*time_connect.*; done$", out='ap-south-1 0.004s\nap-southeast-1 0.037s\neu-west-1 0.121s\nus-east-1 0.196s'), dict(re=r"^curl -s -o /dev/null -w '?%\{time_connect\}.*https://ec2\.(?<r>[a-z0-9-]+)\.amazonaws\.com/?$", out='0.0{rnd}s  (simulated single sample for {r})')],
        lights=['edge', 'lat'], explain='Connect time grows with distance: a few ms inside Mumbai, ~35 ms to Singapore, 120–200 ms to Europe and the US. This is physics — why you pick a Region near users and cache content at the edge.'),
  ]))

NEWBIE = newbie('Think of AWS as a company with <b>warehouses in many cities</b>. Each city (Region) has several <b>separate buildings</b> (Availability Zones) so that if one building loses power, the others keep working. Small <b>pickup counters</b> (edge locations) near customers hand out popular items quickly.',
  [('Region', 'a city/area with AWS buildings, e.g. Mumbai'), ('Availability Zone', 'one of several separate buildings in that Region'), ('Data centre', 'the actual building full of computers'), ('Latency', 'the waiting time for data to travel'), ('Edge location', 'a small site near users that keeps copies of content')])
LADDER = ladder([
 ('AWS has buildings in many cities; your data lives where you choose; using two buildings keeps you running if one fails.', 'Look at an AWS Region map and find the two Indian Regions (Mumbai and Hyderabad).', 'Why keep copies in two buildings?', 'If one building has a problem, the other keeps your app running.'),
 ('Region → Availability Zones → data centres; plus Local Zones, Wavelength, Outposts and edge locations.', 'Run describe-availability-zones and list Mumbai’s three AZs.', 'Is an edge location a place to run your servers?', 'No — it caches content and runs DNS/CDN functions.'),
 ('Choose a Region with the four-question test; design multi-AZ; understand AZ IDs.', 'Map AZ names to AZ IDs and compare with a classmate.', 'Why can ap-south-1a differ between accounts?', 'AWS maps AZ names to physical AZs per account; AZ IDs are shared.'),
 ('Plan resilience: multi-AZ vs cross-Region DR; inter-AZ data cost; Local Zones for latency.', 'Design TiffinGo for N+1 across 3 AZs and estimate cost.', 'Which survives a Region-wide outage: multi-AZ or warm standby in a second Region?', 'Warm standby in a second Region.'),
 ('Use partitions, global vs regional control planes, SCP Region guard-rails, AWS Health and fault injection in designs.', 'Write an SCP limiting resources to India Regions and test it in a sandbox.', 'Why do some global services depend on us-east-1?', 'Their control planes are hosted there; data planes are global.')])
