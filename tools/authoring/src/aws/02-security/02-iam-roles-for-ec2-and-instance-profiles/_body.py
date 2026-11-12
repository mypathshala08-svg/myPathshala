import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
sys.path.insert(0, HERE)
from scenes import imds_scene, keys_vs_role, proof_picture
def cap(frames, steps, title, intro, panel, aria, hid, delay=5500):
    return anim_one('Animated', title, intro, panel, aria, cap_frames(frames, steps), [s[0] + '.' for s in steps], delay=delay, hid=hid)
def row3(k, items, tones, cap_):
    o = ''
    for i, l in enumerate(items):
        on = i <= k
        bx = box(20 + i * 112, 34, 100, 74, tones[i] if on else 'card', rx=8)
        o += (f'<g class="sa-glow">{bx}</g>' if i == k else bx) + (sa_tick(112 + i * 112, 38, 7) if i < k else '')
        for j, w in enumerate(l.split('|')): o += t(70 + i * 112, 60 + j * 14, w, 7.2 if j == 0 else 6.6, 'ink', bold=(j == 0))
        if i < 2: o += arrow(120 + i * 112, 71, 132 + i * 112, 71)
    return o + t(180, 132, cap_, 7.2, 'ink', bold=True)
def mk(t3, items, tones, caps, steps, ttl, intro, panel, aria, hid):
    return cap([t(180, 12, t3[k], 9, 'ink', bold=True) + row3(k, items, tones, caps[k]) for k in range(3)], steps, ttl, intro, panel, aria, hid)
def vt(n, name, tone, d, an, sc, ex, gd, anim, use, avoid, plain, how, words, diff, where, rw, pro):
    return vtype(n, name, tone, d, an, sc, ex, gd, anim, use, avoid, plain=plain, how=how, words=words, diff=diff, where=where, realworld=rw, pro=pro)




hk = hook('A developer copied TiffinGo’s server image to a test account — with an AWS access key inside a config file. Six months later the key was still working, from someone else’s computer.',
    'Keys on servers get copied into images, backups, Git and logs, and they never expire on their own. The professional answer is an <b>IAM role attached to the EC2 instance</b> through an <b>instance profile</b>: the server asks the <b>instance metadata service</b> for <b>temporary credentials</b> that rotate automatically. This lesson shows exactly how that works, how to scope the role to folders (“read notes, write logs, never touch submissions”), and on <b>your own</b> account (or in the simulator) you will launch a server that tests its own permissions and writes the proof to S3 — without you ever logging in.',
    ['Software on AWS gets a role, never keys.', 'Instance profile = how a role is attached to EC2; IMDSv2 = how the app fetches the keys.', 'Prove both sides: what the server can do and what it cannot.'])

def story_scene():
    o = t(180, 12, 'A key in a config file', 9, 'ink', bold=True)
    o += box(8, 28, 160, 74, 'red', rx=8) + t(88, 48, 'Key in the image', 8.4, 'ink', bold=True) + t(88, 64, 'copied to test account', 7, 'ink2') + t(88, 78, 'still valid 6 months later', 7, 'ink2') + t(88, 92, 'used from outside', 7.4, 'ink', bold=True)
    o += box(192, 28, 160, 74, 'green', rx=8) + t(272, 48, 'Instance role', 8.4, 'ink', bold=True) + t(272, 64, 'nothing on disk', 7, 'ink2') + t(272, 78, 'keys rotate hourly', 7, 'ink2') + t(272, 92, 'folder-level limits', 7.4, 'ink', bold=True)
    o += t(180, 122, 'If it is not stored, it cannot leak', 7.6, 'ink', bold=True)
    return o
scene_svg = scene('Left: an access key inside a server image was copied to a test account and still worked six months later from outside. Right: an instance role stores nothing on disk, rotates keys and limits access by folder.', story_scene(), 'Servers get <tspan font-weight="700" class="s-acc">roles</tspan>, not keys.', h=132)
dialogue = '''K> Sir, the app needs to read S3. Without keys, how does it log in?
A> The server itself gets an identity — a role. Inside every EC2 instance there is a special address, 169.254.169.254, that hands the app temporary keys for that role.
R> And if someone hacks the server and copies them?
A> They expire within hours, and the role can only do what its policy says — read notes, write logs. With IMDSv2 it is also much harder to trick the server into revealing them.
K> How do we prove that in the lab exam?
A> From the server: one command that works, one that fails with AccessDenied. Save both outputs. Let’s build it.'''

def bigpic():
    o = t(320, 14, 'Role → instance profile → instance → metadata → temporary keys', 10.5, 'ink', bold=True)
    steps = [('role', 'IAM role', 'LabAppRole', 'amber'), ('file', 'Trust policy', 'ec2.amazonaws.com', 'violet'), ('key', 'Permission policy', 'notes/ read, logs/ write', 'green'), ('app', 'Instance profile', 'container for the role', 'blue'), ('server', 'EC2 instance', 'launched with profile', 'blue'), ('chip', 'IMDSv2', '169.254.169.254', 'violet'), ('list', 'SDK / CLI', 'uses ASIA… keys', 'green')]
    for i, (icn, a, b, tn) in enumerate(steps):
        x = 50 + i * 90
        o += svc(x, 40, icn, a, b, tn, w=84)
        if i < 6: o += arrow(x + 42, 66, x + 48, 66)
    o += sa_building(20, 120, 600, 120, 'What the role can reach in S3 (bucket edu-content)', 'green')
    o += svc(130, 150, 'folder', 'notes/', 'GetObject ✓', 'green', w=110) + svc(320, 150, 'folder', 'logs/', 'PutObject ✓', 'blue', w=110) + svc(510, 150, 'folder', 'submissions/', 'no Allow + Deny ✘', 'red', w=120)
    o += t(320, 258, 'The policy decides what the server can do; the instance profile decides which server gets the role.', 7.6, 'ink2')
    return o
BIG = bigfig('Chain: an IAM role with a trust policy for ec2.amazonaws.com and a permission policy is placed in an instance profile; the instance is launched with the profile; the SDK fetches temporary keys from IMDSv2; the role can read notes, write logs and is denied submissions in the S3 bucket.', bigpic(), h=268)

picture = (newbie('Think of a <b>company car</b>. The car (server) does not carry the owner’s house keys. Instead, every morning the car gets a <b>day pass</b> from the security office (temporary keys from the role), which opens only the gates it needs. If the pass is stolen, it stops working tonight.',
            [('EC2 instance', 'a virtual computer (server) in AWS'), ('Role', 'a set of permissions a server can “wear”'), ('Instance profile', 'the clip that attaches the role to the server'), ('Metadata service', 'a private help desk inside the server that hands out the day pass'), ('Temporary credentials', 'keys that expire automatically')]) +
    '  <p>Every AWS service that runs your code has a way to give it a role. For EC2 the path looks like this:</p>\n' + BIG +
    '\n  <h3>Situation 1 — where do the app’s credentials live?</h3>\n' + keys_vs_role() +
    '\n  <h3>Situation 2 — the proof examiners ask for</h3>\n' + proof_picture())

SOLVE = imds_scene()

def mapfig():
    o = t(320, 16, 'Seven ways AWS compute gets credentials', 11, 'ink', bold=True)
    items = [('1', 'EC2 instance profile', 'role for a server', 'blue'), ('2', 'IMDSv2', 'token-protected metadata', 'violet'), ('3', 'EC2 service role trust', 'ec2.amazonaws.com', 'amber'), ('4', 'Lambda execution role', 'role for a function', 'green'),
             ('5', 'ECS task role', 'role per container task', 'blue'), ('6', 'EKS Pod Identity / IRSA', 'role per Kubernetes pod', 'card'), ('7', 'Service-linked role', 'AWS-managed role for a service', 'red')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 12 + (i % 4) * 156; y = 32 + (i // 4) * 84
        o += box(x, y, 148, 70, tn, rx=8) + pin(x + 16, y + 16, n) + t(x + 80, y + 34, a, 7.8, 'ink', bold=True) + t(x + 78, y + 54, b, 6.8, 'ink2')
    o += t(320, 210, 'Same idea everywhere: the platform assumes a role for your code and hands it temporary keys.', 7.4, 'ink2')
    return o
MAP = bigfig('Map of seven ways compute gets credentials: EC2 instance profile, IMDSv2, EC2 service role trust, Lambda execution role, ECS task role, EKS Pod Identity or IRSA, service-linked role.', mapfig(), h=222)

def cr(n, name, tone, d, an, ex, tip, A, use, avoid, plain, how, words, diff, rw, pro):
    return vt(n, name, tone, d, an, ex, tip, '', A, use, avoid, plain, how, words, diff, ['CLF-C02 Domain 2', 'SAA-C03 / Developer Associate', 'C-DAC lab exams'], rw, pro)

A1 = mk(['Role', 'Instance profile', 'Instance'], ['role|permissions|+ trust', 'profile|holds one|role', 'instance|launched|with profile'], ['amber', 'blue', 'green'],
        ['create the role with an EC2 trust policy', 'put it in an instance profile (console does this automatically)', 'launch or attach the profile to the instance'],
        [('Role', 'Permissions + trust for EC2.', ''), ('Profile', 'Container for exactly one role.', ''), ('Attach', 'At launch or later.', '')], 'Instance profile', 'The clip between role and server.', 'Profile', 'Animation: role; instance profile; instance.', 'r1anim')
T1 = cr(1, 'EC2 instance profile', 'blue',
    'An <b>instance profile</b> is a container for one IAM role that you attach to an EC2 instance; EC2 then assumes the role on the instance’s behalf and exposes its temporary credentials to software through the instance metadata service. The console creates a profile with the same name as the role automatically; with the CLI you create it and add the role yourself.',
    'A lanyard clip: the badge (role) hangs on it, and the clip attaches the badge to one person (server).',
    'EduSpark’s portal server runs with profile <i>PortalRole</i>: read notes/, write logs/.',
    'Tip: you can replace a running instance’s profile (<code>replace-iam-instance-profile-association</code>) without restarting it.', A1,
    'any software on EC2 needs AWS access.', 'you are tempted to run aws configure on a server.',
    'The attachment that gives a server its role.',
    [('Create role', 'Trust ec2.amazonaws.com.'), ('Create profile', 'create-instance-profile.'), ('Add role', 'add-role-to-instance-profile.'), ('Attach', '--iam-instance-profile Name=…'), ('Verify', 'aws sts get-caller-identity on the server.')],
    [('instance profile', 'role container for EC2'), ('association', 'link between profile and instance'), ('iam:PassRole', 'permission needed to give a role to a service')],
    table(['', 'Role', 'Instance profile'], [['Holds permissions', 'yes', 'no — holds the role'], ['Attached to', 'nothing directly', 'EC2 instance'], ['Created by console', 'yes', 'automatically with the role']], minw=420),
    'Exam answer for “EC2 app needs S3, no keys”: IAM role via instance profile.',
    'The person launching the instance needs <code>iam:PassRole</code> for that role — that is how AWS stops people from attaching admin roles they do not own.')

A2 = mk(['PUT token', 'GET with token', 'Hop limit 1'], ['PUT|/api/token|TTL ≤ 6 h', 'GET|metadata|header token', 'hop|stops proxies|containers'], ['violet', 'amber', 'green'],
        ['request a session token with PUT', 'send the token in a header on every metadata GET', 'a hop limit of 1 keeps the token inside the instance'],
        [('PUT token', 'Session-oriented, up to 6 hours.', ''), ('GET', 'Header X-aws-ec2-metadata-token.', ''), ('Protect', 'Blocks SSRF-style theft.', '')], 'IMDSv2', 'Metadata behind a token.', 'IMDSv2', 'Animation: PUT token; GET with token; hop limit.', 'r2anim')
T2 = cr(2, 'IMDSv2 (instance metadata service v2)', 'violet',
    'The <b>instance metadata service</b> at <code>169.254.169.254</code> gives software on an instance information about itself — including its role credentials; <b>IMDSv2</b> requires a session token obtained with a PUT request, which defends against server-side request forgery and open-proxy attacks that could steal credentials with IMDSv1’s simple GETs.',
    'A help desk that first asks for your staff token before handing anything over.',
    'Set <code>HttpTokens=required</code> on every instance — newer AMIs and accounts can make it the default.',
    'Tip: in a lab, check with <code>curl -s http://169.254.169.254/latest/meta-data/</code> — with IMDSv2 required it returns <code>401</code>.', A2,
    'always — require IMDSv2 on all instances.', 'old software that only supports IMDSv1 (update the SDK).',
    'A private address inside the server that hands out its role keys — safely.',
    [('PUT', '/latest/api/token.'), ('Header', 'X-aws-ec2-metadata-token-ttl-seconds.'), ('GET', 'with X-aws-ec2-metadata-token.'), ('Require', 'HttpTokens=required.'), ('Hop limit', '1 (2 for containers).')],
    [('SSRF', 'tricking a server into making requests for an attacker'), ('hop limit', 'how many network hops the token may travel'), ('link-local', '169.254.x.x, reachable only from the instance')],
    table(['', 'IMDSv1', 'IMDSv2'], [['Request', 'plain GET', 'PUT for token, then GET with header'], ['SSRF risk', 'high', 'much lower'], ['Recommended', 'no', 'yes (required)']], minw=420),
    'Security exams and real breaches: SSRF + IMDSv1 is a classic credential-theft path.',
    'Enforce with an SCP or IAM condition <code>ec2:MetadataHttpTokens = required</code> on RunInstances.')

A3 = mk(['Trust policy', 'EC2 assumes', 'STS keys'], ['trust|Principal|ec2.amazonaws.com', 'assume|for the|instance', 'keys|delivered|via IMDS'], ['amber', 'violet', 'green'],
        ['the role’s trust policy names ec2.amazonaws.com', 'EC2 assumes the role for the instance', 'STS returns keys that EC2 delivers through IMDS'],
        [('Trust', 'Service principal ec2.amazonaws.com.', ''), ('Assume', 'Done by EC2, not you.', ''), ('Deliver', 'Through IMDS, refreshed.', '')], 'Service role trust', 'Who may wear the badge.', 'Trust', 'Animation: trust policy; EC2 assumes; STS keys.', 'r3anim')
T3 = cr(3, 'EC2 service role trust policy', 'amber',
    'A role for EC2 has a <b>trust policy</b> allowing the service principal <code>ec2.amazonaws.com</code> to call <code>sts:AssumeRole</code>; without it, the role cannot be used by instances (the console’s “AWS service → EC2” choice writes it for you).',
    'The visitor badge says “valid for company cars only”.',
    'Trust JSON: <code>{"Effect":"Allow","Principal":{"Service":"ec2.amazonaws.com"},"Action":"sts:AssumeRole"}</code>.',
    'Tip: add conditions like <code>aws:SourceAccount</code> to trust policies for extra safety in shared environments.', A3,
    'you create any role for EC2.', 'you put a user ARN instead of the service principal.',
    'The rule saying which service may use the role.',
    [('Principal', 'Service: ec2.amazonaws.com.'), ('Action', 'sts:AssumeRole.'), ('Condition', 'optional SourceAccount.'), ('Profile', 'Wraps the role.'), ('PassRole', 'Launcher needs it.')],
    [('service principal', 'an AWS service named in a policy'), ('AssumeRole', 'STS action to borrow a role'), ('confused deputy', 'a service tricked into acting for the wrong party')],
    table(['Compute', 'Service principal'], [['EC2', 'ec2.amazonaws.com'], ['Lambda', 'lambda.amazonaws.com'], ['ECS tasks', 'ecs-tasks.amazonaws.com']], minw=360),
    'Error “Invalid principal in policy” usually means a typo in the service name.',
    'One role per application, not one shared “EC2Role” for every server.')

A4 = mk(['Function', 'Execution role', 'Logs + calls'], ['function|any trigger|runtime', 'role|lambda.amazonaws.com|trust', 'use|CloudWatch Logs|+ your services'], ['green', 'amber', 'blue'],
        ['every Lambda function has one execution role', 'Lambda assumes it each time the function runs', 'it needs log permissions plus whatever the code calls'],
        [('Function', 'Your code.', ''), ('Role', 'Execution role, trusted by Lambda.', ''), ('Use', 'Logs + exact service actions.', '')], 'Lambda execution role', 'A role per function.', 'Lambda', 'Animation: function; execution role; logs and calls.', 'r4anim')
T4 = cr(4, 'Lambda execution role', 'green',
    'A <b>Lambda execution role</b> is the IAM role a function assumes when it runs; it needs CloudWatch Logs permissions (e.g. AWSLambdaBasicExecutionRole) plus exactly the actions the code performs, and its credentials reach the code as environment variables managed by Lambda.',
    'A courier’s delivery pass, valid only while a delivery is in progress.',
    'TiffinGo’s SMS function: logs + sns:Publish on one topic.',
    'Tip: separate roles per function — a shared role turns one bug into account-wide risk.', A4,
    'you create any Lambda function.', 'you reuse an admin role “for now”.',
    'The permissions a serverless function runs with.',
    [('Trust', 'lambda.amazonaws.com.'), ('Logs', 'Basic execution policy.'), ('Actions', 'Exact services.'), ('Env vars', 'Creds injected.'), ('Review', 'Last accessed.')],
    [('execution role', 'role the function runs as'), ('resource policy', 'who may invoke the function'), ('basic execution', 'permission to write logs')],
    table(['', 'Execution role', 'Function resource policy'], [['Answers', 'what the function may do', 'who may invoke the function'], ['Trusted by', 'lambda.amazonaws.com', '—']], minw=420),
    'Lesson 3.6 builds functions with execution roles.',
    'If the function cannot write logs you get no logs at all — always include the basic execution permissions.')

A5 = mk(['Task definition', 'Task role', 'Container SDK'], ['task|containers|definition', 'taskRoleArn|app permissions|per task', 'SDK|container creds|endpoint'], ['blue', 'amber', 'green'],
        ['the task definition names a task role', 'ECS delivers that role’s credentials to the containers', 'the SDK in the container finds them automatically'],
        [('Define', 'taskRoleArn in the task definition.', ''), ('Deliver', 'Container credentials endpoint.', ''), ('Use', 'SDK chain step 5.', '')], 'ECS task role', 'A role per container task.', 'ECS', 'Animation: task definition; task role; container SDK.', 'r5anim')
T5 = cr(5, 'ECS task role (and task execution role)', 'blue',
    'In Amazon ECS the <b>task role</b> gives the application containers their AWS permissions, while the separate <b>task execution role</b> lets ECS itself pull images from ECR and write logs; credentials are served to containers through a container credentials endpoint, not the instance metadata.',
    'Two passes: one for the delivery boy (task role), one for the van driver who brings him (execution role).',
    'Order-API task role: dynamodb:PutItem on Orders; execution role: ECR pull + logs.',
    'Tip: mixing the two roles is the commonest ECS permission bug.', A5,
    'you run containers on ECS/Fargate.', 'you rely on the EC2 host’s instance role for container apps (too broad).',
    'The permissions a container application runs with.',
    [('Task role', 'App permissions.'), ('Execution role', 'Pull image, logs.'), ('Endpoint', 'Container credentials.'), ('SDK', 'Finds it.'), ('Isolation', 'Per task.')],
    [('task', 'running copy of a task definition'), ('Fargate', 'serverless containers'), ('ECR', 'container image registry')],
    table(['', 'Task role', 'Task execution role'], [['Used by', 'your code', 'ECS agent'], ['Typical permissions', 'S3, DynamoDB, SQS…', 'ECR pull, CloudWatch Logs, secrets']], minw=420),
    'Module 9 (ECS and EKS) uses both.',
    'Block containers from reaching the host’s IMDS so they cannot borrow the instance role.')

A6 = mk(['Pod', 'Service account', 'Role'], ['pod|in EKS|cluster', 'k8s SA|annotated|or associated', 'role|per app|temporary'], ['card', 'amber', 'green'],
        ['a Kubernetes pod runs your app', 'its service account is linked to an IAM role', 'the pod gets that role’s temporary credentials'],
        [('Pod', 'Your app in EKS.', ''), ('Link', 'Pod Identity association or IRSA (OIDC).', ''), ('Use', 'Per-pod least privilege.', '')], 'EKS Pod Identity / IRSA', 'A role per pod.', 'EKS', 'Animation: pod; service account; role.', 'r6anim')
T6 = cr(6, 'EKS Pod Identity and IRSA', 'card',
    'In Amazon EKS, <b>EKS Pod Identity</b> (newer, simpler) or <b>IAM Roles for Service Accounts (IRSA, via OIDC)</b> map a Kubernetes service account to an IAM role, so each pod gets its own temporary AWS credentials instead of sharing the worker node’s role.',
    'Different staff in the same building each get their own badge, not the building’s master key.',
    'The recommendation-engine pod can read the features bucket; the web pod cannot.',
    'Tip: prefer EKS Pod Identity for new clusters; IRSA remains common.', A6,
    'you run multiple apps on EKS.', 'you give the node role all app permissions.',
    'Separate AWS permissions for each app in Kubernetes.',
    [('Service account', 'Kubernetes identity.'), ('Association', 'Pod Identity or IRSA.'), ('Role', 'Trust for EKS.'), ('SDK', 'Finds creds.'), ('Audit', 'Per-pod in CloudTrail.')],
    [('pod', 'smallest unit running in Kubernetes'), ('service account', 'identity of a pod'), ('OIDC', 'federation standard used by IRSA')],
    table(['', 'Pod Identity', 'IRSA'], [['Set-up', 'EKS add-on + association', 'OIDC provider + annotated SA'], ['Trust principal', 'pods.eks.amazonaws.com', 'cluster OIDC provider']], minw=420),
    'Appears in advanced container/security interviews.',
    'Audit which pods still rely on the node role — that is usually where over-permission hides.')

A7 = mk(['Service needs', 'AWS creates role', 'Locked by AWS'], ['service|e.g. Auto Scaling|ELB', 'role|service-linked|predefined', 'locked|you cannot|edit perms'], ['red', 'amber', 'green'],
        ['a service needs to act in your account', 'AWS creates a service-linked role with fixed permissions', 'you can view or delete it but not edit its permissions'],
        [('Need', 'Service acts for you.', ''), ('Create', 'Predefined by AWS.', ''), ('Locked', 'Permissions maintained by AWS.', '')], 'Service-linked role', 'Roles AWS manages.', 'SLR', 'Animation: service needs; AWS creates role; locked by AWS.', 'r7anim')
T7 = cr(7, 'Service-linked role', 'red',
    'A <b>service-linked role</b> is a predefined role linked to one AWS service (for example Auto Scaling, Elastic Load Balancing, RDS) with permissions the service needs to call other services for you; AWS defines and maintains its permissions, and you can only delete it once the service no longer uses it.',
    'A contractor badge issued by the building management itself, with fixed access.',
    'AWSServiceRoleForAutoScaling lets Auto Scaling launch and terminate your instances.',
    'Tip: if a console wizard says it will create a role named AWSServiceRoleFor…, that is a service-linked role — expected and safe.', A7,
    'a service creates one automatically.', 'you try to edit its permissions — create your own role instead if needed.',
    'A built-in role AWS creates for its own services.',
    [('Path', '/aws-service-role/.'), ('Name', 'AWSServiceRoleFor….'), ('Perms', 'By AWS.'), ('Trust', 'The service.'), ('Delete', 'When unused.')],
    [('service-linked', 'tied to one service'), ('predefined', 'written by AWS'), ('path', 'folder-like prefix in IAM')],
    table(['', 'Service role (yours)', 'Service-linked role'], [['Who writes permissions', 'you', 'AWS'], ['Editable', 'yes', 'no']], minw=420),
    'Know the difference for SAA and Security exams.',
    'Do not delete service-linked roles to “clean up” — features silently stop working.')

SUMMARY = table(['#', 'Mechanism', 'For', 'Credentials arrive via'], [
    ['1', 'Instance profile', 'EC2', 'IMDS'], ['2', 'IMDSv2', 'EC2 (secure access)', 'token + GET'], ['3', 'Service role trust', 'any role for EC2', 'STS via EC2'], ['4', 'Lambda execution role', 'Lambda', 'environment variables'],
    ['5', 'ECS task role', 'ECS/Fargate', 'container credentials endpoint'], ['6', 'Pod Identity / IRSA', 'EKS pods', 'agent / web identity'], ['7', 'Service-linked role', 'AWS services', 'used by the service itself']], minw=600)

TYPES = ('  <p>Seven ways AWS compute gets credentials, each in the same pattern: definition, plain words, analogy, internal steps, animation, differences, real-world example and an expert tip.</p>\n'
         + challenge(['What does curl 169.254.169.254/latest/meta-data/ return when IMDSv2 is required and no token is sent?', 'Which ECS role pulls the image?', 'What permission does the person launching an instance need to attach a role?'], 'types 2, 5 and 1') + MAP
         + jump(['Profile', 'IMDSv2', 'Trust', 'Lambda', 'ECS', 'EKS', 'Service-linked']) + T1 + T2 + T3 + T4 + T5 + T6 + T7
         + '\n  <h3 style="margin-top:34px">All seven side by side</h3>\n' + SUMMARY)

parts = wwu([
    ('Trust policy', 'ec2.amazonaws.com may assume.', 'Without it, EC2 cannot use the role.', 'Console: AWS service → EC2.'),
    ('Permission policy', 'exact S3 prefixes/actions.', 'What the server can do.', 'notes/ read, logs/ write.'),
    ('Explicit Deny', 'for what must never happen.', 'Survives future Allows.', 'Deny submissions/*, Deny s3:Delete*.'),
    ('Instance profile', 'role container.', 'Attaches role to instance.', '--iam-instance-profile Name=…'),
    ('IMDSv2 required', 'token-based metadata.', 'Stops credential theft via SSRF.', 'HttpTokens=required.'),
    ('Proof', 'allowed + denied outputs.', 'Evidence for audits and exams.', 'Saved to logs/ automatically.')])

DEEP = ('  <h3>The server policy used in this lesson</h3>\n' + code('json', 'LabAppPolicy — read notes, write logs, never submissions, never delete',
 '{\n  "Version": "2012-10-17",\n  "Statement": [\n    {"Sid": "ListNotesAndLogs", "Effect": "Allow", "Action": "s3:ListBucket",\n     "Resource": "arn:aws:s3:::BUCKET",\n     "Condition": {"StringLike": {"s3:prefix": ["notes/*", "logs/*"]}}},\n    {"Sid": "ReadNotes", "Effect": "Allow", "Action": "s3:GetObject",\n     "Resource": "arn:aws:s3:::BUCKET/notes/*"},\n    {"Sid": "WriteLogs", "Effect": "Allow", "Action": "s3:PutObject",\n     "Resource": "arn:aws:s3:::BUCKET/logs/*"},\n    {"Sid": "NeverSubmissions", "Effect": "Deny", "Action": "s3:*",\n     "Resource": "arn:aws:s3:::BUCKET/submissions/*"},\n    {"Sid": "NeverDelete", "Effect": "Deny",\n     "Action": ["s3:DeleteObject", "s3:DeleteObjectVersion", "s3:DeleteBucket"],\n     "Resource": ["arn:aws:s3:::BUCKET", "arn:aws:s3:::BUCKET/*"]}\n  ]\n}') +
 '  <p>Why the two Deny statements? Allows can be added later by mistake (someone attaches a broad policy). An explicit Deny keeps “never read submissions” and “never delete, even if hacked” true forever.</p>\n'
 '  <h3>Talking to IMDSv2 by hand</h3>\n' + code('bash', 'On the instance', 'TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")\ncurl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/iam/security-credentials/\ncurl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/iam/security-credentials/LabAppRole | head -c 200\ncurl -s -o /dev/null -w "%{http_code}\\n" http://169.254.169.254/latest/meta-data/   # 401 = IMDSv2 enforced'))

clouds = vendor_tabs('<p><b>AWS:</b> IAM role + instance profile, IMDSv2; Lambda execution roles; ECS task roles; EKS Pod Identity.</p>',
    '<p><b>Azure:</b> managed identities (system- or user-assigned) on VMs, App Service, Functions; tokens from the Azure Instance Metadata Service; RBAC role assignments.</p>',
    '<p><b>Google Cloud:</b> attach a service account to a VM or Cloud Run service; tokens from the metadata server; Workload Identity for GKE.</p>') + \
    cloud3([['Identity for a VM', 'instance profile role', 'managed identity', 'attached service account'], ['Metadata endpoint', '169.254.169.254 (IMDSv2)', '169.254.169.254 (IMDS)', 'metadata.google.internal'], ['Containers/K8s', 'ECS task role, EKS Pod Identity', 'workload identity', 'Workload Identity Federation for GKE']])

MOCKA.extend([
 mock('aws', ['IAM', 'Roles', 'Create role'], ['Trusted entity', 'Permissions', 'Name, review'], 'Trusted entity', [('Trusted entity type', 'AWS service'), ('Use case', '▾ EC2'), ('Role name', 'LabAppRole')], 'Create role'),
 mock('aws', ['EC2', 'Launch an instance', 'Advanced details'], ['Name and tags', 'AMI', 'Advanced details'], 'Advanced details', [('IAM instance profile', '▾ LabAppRole'), ('Metadata version', '▾ V2 only (token required)'), ('User data', '#!/bin/bash … (tests + report)')], 'Launch instance'),
 mock('aws', ['S3', 'edu-lab-…', 'logs/'], ['Objects', 'Properties'], 'Objects', [('Object', 'logs/proof-i-0abc.txt'), ('Content', 'notes OK · logs OK · submissions DENIED · delete DENIED')], 'Open'),
])

STEP1 = astep('1 · Bucket with three areas + a role scoped to them',
    ['[[S3]] → create <code>edu-lab-ACCOUNTID</code>; upload a file to <code>notes/</code> and one to <code>submissions/</code>.', '[[IAM]] → [[Policies]] → [[Create policy]] → JSON from the Deep dive (replace BUCKET) → <code>LabAppPolicy</code>.', '[[Roles]] → [[Create role]] → [[AWS service]] → [[EC2]] → attach LabAppPolicy → name <code>LabAppRole</code> (the console also creates the instance profile).'],
    "ACC=$(aws sts get-caller-identity --query Account --output text); B=edu-lab-$ACC\naws s3 mb s3://$B --region ap-south-1\necho 'Lecture 1 notes' > l1.txt; echo 'Roll 101 answer' > a1.txt\naws s3 cp l1.txt s3://$B/notes/l1.txt; aws s3 cp a1.txt s3://$B/submissions/a1.txt\ncat > trust.json <<'EOF'\n{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"ec2.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}\nEOF\ncat > policy.json <<EOF\n{\"Version\":\"2012-10-17\",\"Statement\":[\n{\"Effect\":\"Allow\",\"Action\":\"s3:ListBucket\",\"Resource\":\"arn:aws:s3:::$B\",\"Condition\":{\"StringLike\":{\"s3:prefix\":[\"notes/*\",\"logs/*\"]}}},\n{\"Effect\":\"Allow\",\"Action\":\"s3:GetObject\",\"Resource\":\"arn:aws:s3:::$B/notes/*\"},\n{\"Effect\":\"Allow\",\"Action\":\"s3:PutObject\",\"Resource\":\"arn:aws:s3:::$B/logs/*\"},\n{\"Effect\":\"Deny\",\"Action\":\"s3:*\",\"Resource\":\"arn:aws:s3:::$B/submissions/*\"},\n{\"Effect\":\"Deny\",\"Action\":[\"s3:DeleteObject\",\"s3:DeleteObjectVersion\",\"s3:DeleteBucket\"],\"Resource\":[\"arn:aws:s3:::$B\",\"arn:aws:s3:::$B/*\"]}]}\nEOF\naws iam create-role --role-name LabAppRole --assume-role-policy-document file://trust.json >/dev/null\naws iam put-role-policy --role-name LabAppRole --policy-name LabAppPolicy --policy-document file://policy.json\naws iam create-instance-profile --instance-profile-name LabAppRole >/dev/null\naws iam add-role-to-instance-profile --instance-profile-name LabAppRole --role-name LabAppRole\naws iam get-instance-profile --instance-profile-name LabAppRole --query 'InstanceProfile.Roles[].RoleName' --output text",
    '<code>LabAppRole</code> printed as the role inside the instance profile. (The CLI uses an inline policy here for brevity; in production prefer a customer managed policy.)',
    'With the CLI you must create the instance profile yourself — a frequent “role not showing in the launch wizard” cause.')

STEP2 = astep('2 · Launch a server that tests its own permissions (no login)',
    ['[[EC2]] → [[Launch instance]] → Amazon Linux 2023, t3.micro → [[Advanced details]]: IAM instance profile <code>LabAppRole</code>, Metadata version <b>V2 only</b>, paste the user data script below (replace BUCKET).', 'Wait ~2 minutes after the instance is running.'],
    "cat > proof.sh <<EOF\n#!/bin/bash\nexport AWS_DEFAULT_REGION=ap-south-1\nB=$B; I=\\$(TOKEN=\\$(curl -s -X PUT http://169.254.169.254/latest/api/token -H 'X-aws-ec2-metadata-token-ttl-seconds: 300'); curl -s -H \"X-aws-ec2-metadata-token: \\$TOKEN\" http://169.254.169.254/latest/meta-data/instance-id)\nR=/tmp/proof.txt; date > \\$R; aws sts get-caller-identity --query Arn --output text >> \\$R\nt(){ if eval \"\\$2\" >/dev/null 2>&1; then echo \"\\$1: ALLOWED\" >> \\$R; else echo \"\\$1: DENIED\" >> \\$R; fi; }\nt 'read notes'        \"aws s3 cp s3://\\$B/notes/l1.txt -\"\nt 'read submissions'  \"aws s3 cp s3://\\$B/submissions/a1.txt -\"\nt 'delete notes'      \"aws s3 rm s3://\\$B/notes/l1.txt\"\necho \"IMDSv1 call: \\$(curl -s -o /dev/null -w '%{http_code}' http://169.254.169.254/latest/meta-data/)\" >> \\$R\naws s3 cp \\$R s3://\\$B/logs/proof-\\$I.txt\nEOF\nAMI=resolve:ssm:/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64\nID=$(aws ec2 run-instances --image-id $AMI --instance-type t3.micro --iam-instance-profile Name=LabAppRole \\\n  --metadata-options HttpTokens=required,HttpEndpoint=enabled --user-data file://proof.sh \\\n  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=role-lab}]' --query 'Instances[0].InstanceId' --output text)\naws ec2 wait instance-running --instance-ids $ID; echo $ID; sleep 120",
    'the instance ID; after two minutes the server has run the tests itself using only its role.',
    'You never logged in and never typed a key: the server proved its own permissions — exactly what “self-configuring” lab requirements ask.')

STEP3 = astep('3 · Read the proof the server wrote',
    ['[[S3]] → bucket → <code>logs/</code> → open <code>proof-i-….txt</code>.', 'Optional: [[EC2]] → instance → [[Actions]] → [[Security]] → [[Modify IAM role]] to see the attached role.'],
    "aws s3 ls s3://$B/logs/\naws s3 cp s3://$B/logs/proof-$ID.txt -\naws ec2 describe-instances --instance-ids $ID --query 'Reservations[0].Instances[0].[IamInstanceProfile.Arn,MetadataOptions.HttpTokens]' --output text",
    'the date, <code>arn:aws:sts::…:assumed-role/LabAppRole/i-0…</code>, then <code>read notes: ALLOWED</code>, <code>read submissions: DENIED</code>, <code>delete notes: DENIED</code>, <code>IMDSv1 call: 401</code>; and the profile ARN with <code>required</code>.',
    'The identity line shows the server acted as an assumed role session named after the instance — that is what CloudTrail records too.')

prac = practical(AWS_INTRO + ' You launch one t3.micro for a few minutes (Free Tier / credits cover it) and delete everything at the end.', [AWS_SETUP, STEP1, STEP2, STEP3],
    cleanup="<code>aws ec2 terminate-instances --instance-ids $ID; aws ec2 wait instance-terminated --instance-ids $ID; aws iam remove-role-from-instance-profile --instance-profile-name LabAppRole --role-name LabAppRole; aws iam delete-instance-profile --instance-profile-name LabAppRole; aws iam delete-role-policy --role-name LabAppRole --policy-name LabAppPolicy; aws iam delete-role --role-name LabAppRole; aws s3 rb s3://$B --force</code> — note: the role’s own Deny blocks deletes only for the server; you (admin) can still delete.")

mist = mistakes([
    ['Running aws configure on a server.', 'Habit from laptops.', 'Attach an instance profile role; delete ~/.aws/credentials.'],
    ['Role created with the CLI but missing from the launch wizard.', 'No instance profile.', 'create-instance-profile + add-role-to-instance-profile.'],
    ['AccessDenied for iam:PassRole when launching.', 'Launcher lacks PassRole.', 'Grant iam:PassRole on that role ARN only.'],
    ['IMDSv1 left enabled.', 'Default on old AMIs/templates.', 'HttpTokens=required everywhere; enforce with SCP.'],
    ['One shared role for every server.', 'Convenience.', 'One role per application; least privilege.'],
    ['Proving only what works.', 'Forgetting the deny side.', 'Always show one ✓ and one AccessDenied.']])

cert = table(['Exam / syllabus', 'What is asked'], [['AWS CLF-C02', 'Roles for applications instead of keys (Domain 2).'], ['SAA-C03 / Developer Associate', 'Instance profiles, PassRole, IMDSv2, Lambda execution roles, ECS task vs execution role.'], ['C-DAC lab exams', '“No passwords or access keys on the server; server may read X and write Y but not Z — prove it.”']], minw=560) + \
    '\n  <h3>Try exam-style questions</h3>\n' + qx('An application on EC2 must write to an S3 bucket. What should you do?', ['store keys in environment variables', 'attach an IAM role via an instance profile', 'make the bucket public', 'use the root user'], 1, 'Instance profile role.') + \
    qx('Which protects instance credentials against SSRF?', ['IMDSv1', 'IMDSv2 with tokens required', 'security groups', 'EBS encryption'], 1, 'IMDSv2.') + \
    qx('Which ECS role lets the agent pull images from ECR?', ['task role', 'task execution role', 'service-linked role', 'instance profile'], 1, 'Execution role.') + \
    qx('A user cannot launch an instance with a role: “not authorized to perform iam:PassRole”. Fix?', ['give AdministratorAccess', 'allow iam:PassRole on that role', 'delete the role', 'use root'], 1, 'PassRole.')

from deep_v3 import HOOD, ROLES, DOMAINS, PRO, PROJ, SIM, LADDER

assemble_v2(HERE, story_h2='A key in a copied server image', hook_html=hk,
    narration='A developer copied TiffinGo’s server image to a test account with an access key inside a config file; months later the key still worked from outside. Arjun Sir replaced it with an instance role: nothing on disk, keys that rotate, folder-level limits.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='IAM roles for EC2 and instance profiles',
    formal='An <b>IAM role for EC2</b> is a role whose trust policy allows <code>ec2.amazonaws.com</code> to assume it; it is attached to an instance through an <b>instance profile</b>, and software on the instance obtains automatically rotated <b>temporary credentials</b> for the role from the <b>instance metadata service</b> (IMDSv2 recommended), so no long-term access keys are stored on the server.',
    simple='Give the server a role instead of keys: it borrows temporary keys that expire, and can only do what the role allows.',
    interview=['“For EC2 apps I create a role trusted by ec2.amazonaws.com, put it in an instance profile, require IMDSv2, and scope the policy to exact prefixes with explicit denies for anything that must never happen.”', '“To prove it, I run one allowed and one denied call from the server and keep the AccessDenied output as evidence.”'],
    terms_rows=[('Instance profile', 'Container attaching a role to EC2.'), ('IMDS', 'Metadata service at 169.254.169.254.'), ('IMDSv2', 'Token-protected metadata access.'), ('Trust policy', 'Who may assume the role.'), ('iam:PassRole', 'Permission to give a role to a service.'), ('Execution role', 'Role a Lambda function runs as.'), ('Task role', 'Role an ECS task runs as.'), ('Temporary credentials', 'ASIA… keys + session token.')],
    exam='Every cloud exam asks “application on EC2 needs AWS access” — answer: IAM role via instance profile, never access keys.',
    picture_h2='From role to running server', picture_html=picture,
    after_picture=[('types', 'Types, one by one', 'Seven ways AWS compute gets credentials, one by one', TYPES)],
    how_h2='How an EC2 server gets permissions without keys', how_intro='Follow the credentials from the role to the app.', how_anim=SOLVE,
    parts_h2='Six parts of a secure server identity', parts_html=parts, lv='',
    myth_rows=[('A server needs aws configure to use the CLI.', 'The instance role is found automatically (chain step 6).', 'Animation step 2.'), ('Temporary keys are less secure.', 'They expire; long-term keys do not.', 'Situation 1.'), ('Denied actions do not need testing.', 'Proving denies is half the evidence.', 'Situation 2.')],
    extra_secs=[('ladder', 'Learn at your level', 'From curious beginner to expert — pick your level', LADDER), ('deep', 'Deep dive', 'The server policy with explicit denies; talking to IMDSv2', DEEP), ('hood', 'Under the hood', 'Credential rotation, PassRole, hop limits, CloudTrail session names', HOOD), ('roles', 'By role', 'How developers, data, ML, DevOps and security people use instance roles', ROLES), ('domains', 'By domain', 'Server identity patterns by industry', DOMAINS), ('pro', 'For working professionals', 'Errors, cheat sheet, checklist', PRO)],
    clouds_html=clouds, practical_html=prac + '\n  <h3 id="simulator">Practice without an account: simulator</h3>\n  <p>Build the role, launch the server and read its proof — the map shows each part as you create it.</p>\n' + SIM, mistakes_html=mist, cert_html=cert, project_html=PROJ,
    can_now=['Create a role for EC2 and its instance profile.', 'Explain how IMDSv2 delivers temporary credentials.', 'Scope a server role to folders with explicit denies.', 'Launch a server that proves its own permissions without login.', 'Choose the right role type for EC2, Lambda, ECS and EKS.'],
    next_html='<a href="../03-writing-least-privilege-policies/">2.3 Writing least-privilege policies</a>.',
    pre='<b>Before you start:</b> Lesson 2.1 (policies, roles) and Module 1.')
