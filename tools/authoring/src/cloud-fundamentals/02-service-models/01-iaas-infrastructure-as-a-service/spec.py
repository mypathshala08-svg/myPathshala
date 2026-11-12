import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from svgkit import scn
BODY = body(HERE)
CONCEPT = True
META = dict(module='02-service-models', lesson='01-iaas-infrastructure-as-a-service', n='2.1', module_label='Module 2 · Service models',
    title='IaaS: Infrastructure as a Service',
    desc='Infrastructure as a Service explained with Amazon EC2: what you manage vs the provider, the parts of a server (AMI, instance type, key pair, security group, EBS, user data), what happens inside a launch, the lifecycle and billing, a console walkthrough and a full AWS CLI lab to launch and clean up a web server, with Azure VM and Compute Engine equivalents, mistakes and exam questions.',
    og_desc='Launch a web server in Mumbai in 10 CLI commands: IaaS explained with EC2, animations, console steps and exam questions.',
    minutes=35, level='Beginner',
    lead='IaaS is renting the raw infrastructure: virtual machines, disks and networks. We see <b>what happens inside AWS</b> when you launch, how the <b>lifecycle drives the bill</b>, then launch a <b>web server with the AWS CLI</b> step by step — and delete it.',
    chips=['EC2 · Azure VM · Compute Engine', 'Console + CLI', 'Launch animation', 'Exam questions explained'])
Q = lambda q, o, a, w: dict(q=q, options=o, answer=a, why=w)
QUIZ = mix([
    Q('Beginner: In IaaS, who manages the operating system?', ['The cloud provider', 'The customer', 'Nobody', 'The internet provider'], 1, 'IaaS gives you the infrastructure; you install, patch and run the OS and everything above it.'),
    Q('Beginner: Which is an IaaS service?', ['Amazon EC2', 'Gmail', 'Salesforce', 'AWS Lambda'], 0, 'EC2 rents virtual machines. Gmail/Salesforce are SaaS; Lambda is serverless (FaaS).'),
    Q('Beginner: What does an AMI contain?', ['Billing data', 'The template for the VM’s disk: OS and software', 'The firewall rules', 'Your password'], 1, 'An Amazon Machine Image is the starting disk image; we used Amazon Linux 2023.'),
    Q('Intermediate: SSH times out. The most likely cause is…', ['Wrong AMI', 'The security group does not allow port 22 from your IP', 'Too much RAM', 'Billing'], 1, 'Timeouts mean packets are blocked: check the security group rule, public IP and your current IP.'),
    Q('Intermediate: What happens to the root EBS volume when you terminate an instance (default)?', ['It is kept', 'It is deleted', 'It moves to S3', 'It becomes an AMI'], 1, 'DeleteOnTermination is true for the root volume by default; create an AMI or snapshot first if you need the data.'),
    Q('Intermediate: Instance type c7i.xlarge is best for…', ['Memory-heavy databases', 'CPU-heavy work', 'GPU training', 'Cheap tiny websites'], 1, 'The letter c = compute optimised. r = memory, p/g = GPU, t = small burstable.'),
    Q('Advanced: Which script runs automatically at first boot of an EC2 instance?', ['IAM policy', 'User data', 'Security group', 'CloudTrail'], 1, 'User data is executed by cloud-init as root at launch (our nginx install).'),
    Q('Advanced: In Mumbai a t3.micro running 24×7 for 30 days costs about…', ['$0.33', '$8', '$80', 'Free'], 1, '$0.0112 × 720 h ≈ $8.06, plus disk and public IPv4 charges.')])
REVISION = ['IaaS = rent VMs, disks, networks; you manage OS and above (EC2, Azure VMs, Compute Engine).', 'Parts: AMI, instance type, key pair, security group, EBS, user data, VPC/subnet, public/private IP.',
    'Launch = API call → IAM check → host in AZ → VM + EBS from AMI → network + SG → boot + user data → running.', 'Lifecycle: running bills compute + disk + IP; stopped bills disk (+ IP); terminated deletes root disk.',
    'CLI: ssm get-parameter (AMI) → create-key-pair → create-security-group → run-instances → describe → stop/start → terminate → verify 0.', '849 instance types in Mumbai; letter = purpose (t, m, c, r, i, g/p).']
FAQ = [('Is EC2 included in the AWS free plan?', 'New accounts get credits that cover small instances like t3.micro for practice; always set a budget alert and terminate after labs.'),
    ('What is the difference between stop and terminate?', 'Stop = shut down, keep the disk (you pay for the disk). Terminate = delete the instance and, by default, its root disk.'),
    ('Do I need SSH for this lesson?', 'Not for the CLI steps; SSH is used in the mini project to edit the page. On Windows use the built-in OpenSSH client or EC2 Instance Connect.'),
    ('Why Amazon Linux 2023?', 'It is AWS’s own Linux, free, tuned for EC2 and uses dnf. Ubuntu works too; the user name changes to ubuntu.'),
    ('Was the lab run on a real AWS account?', 'The outputs come from an AWS-compatible emulator (moto) with the real AWS CLI, so commands and formats match; IDs and IPs will differ on your account.')]
SCN_INTRO = 'IaaS interview questions.'
SCENARIOS = (scn('Any company', 'Fresher', '“What is IaaS? Give an example.”', 'Basic service-model question.', 'Can you state what you manage?', '<p>“IaaS provides virtual machines, storage and networking on demand; we manage the OS, runtime and apps. Example: Amazon EC2 — I choose an AMI, instance type, key pair and security group.”</p>', 'Calling Gmail or Beanstalk IaaS.') +
    scn('Startup', 'Fresher', 'Web server is not reachable', 'nginx installed, browser times out.', 'Can you troubleshoot step by step?', '<ul><li>Security group allows 80? Public IP present? nginx running (<code>systemctl status nginx</code>)? User data log (<code>/var/log/cloud-init-output.log</code>)?</li></ul>', 'Recreating the server without finding the cause.') +
    scn('Finance', 'Mid-level', 'Surprise EC2 bill', 'Servers were “stopped”.', 'Do you know lifecycle billing?', '<ul><li>Stopped instances still pay for EBS and public IPs; terminate unused, release Elastic IPs, delete snapshots, use budgets and tags.</li></ul>', '“Stopped means free.”') +
    scn('Architecture', 'Mid-level', 'Choose an instance type', 'Spark job needs 200 GB RAM.', 'Do you know families?', '<ul><li>Memory-optimised (r family), right-size from metrics, Graviton (g suffix) for cost if software supports ARM.</li></ul>', 'Picking the biggest t instance.'))
