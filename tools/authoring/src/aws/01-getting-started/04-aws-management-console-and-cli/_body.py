import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
sys.path.insert(0, HERE)
from scenes import cli_scene
sys.path.insert(0, HERE)
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


hk = hook('Kabir spent his whole Saturday clicking through the console to create 60 student folders and permissions for a new batch. On Monday, half had a typo.',
    'Riya wrote a 12-line CLI loop that did the same job in 40 seconds — and ran it again for the next batch without a single mistake. The console is perfect for <b>exploring and learning</b>; the CLI and SDKs are how professionals <b>repeat, automate and audit</b> work. This lesson covers all seven ways to work with AWS, how the CLI finds your credentials, how to shape output with <b>--query</b>, pagination, profiles and SSO — and on <b>your own</b> account (or in the simulator) you will run a complete create–use–delete cycle from CloudShell.',
    ['Console to learn and look; CLI/SDK/IaC to repeat and automate.', 'The CLI looks for credentials in a fixed order — know it.', '<code>--query</code> + <code>--output</code> turn JSON into exactly what you need.'])

def story_scene():
    o = t(180, 12, 'Clicks vs commands', 9, 'ink', bold=True)
    o += box(8, 28, 160, 74, 'red', rx=8) + t(88, 48, '60 folders by hand', 8.4, 'ink', bold=True) + t(88, 64, '1 day of clicking', 7, 'ink2') + t(88, 78, 'typos, no record', 7, 'ink2') + t(88, 92, 'redo next batch', 7.4, 'ink', bold=True)
    o += box(192, 28, 160, 74, 'green', rx=8) + t(272, 48, '12-line CLI loop', 8.4, 'ink', bold=True) + t(272, 64, '40 seconds', 7, 'ink2') + t(272, 78, 'same every time', 7, 'ink2') + t(272, 92, 'saved in Git', 7.4, 'ink', bold=True)
    o += t(180, 122, 'If you will do it twice, script it', 7.6, 'ink', bold=True)
    return o
scene_svg = scene('Left: creating 60 folders by hand takes a day, has typos and leaves no record. Right: a 12-line CLI loop does it in 40 seconds, identically every time, saved in Git.', story_scene(), 'Click to <tspan font-weight="700" class="s-acc">learn</tspan>, script to repeat.', h=132)
dialogue = '''K> Sir, the console is easier. Why learn commands?
A> The console is great for learning and checking. But every click is an API call — and the CLI makes the same calls, a thousand times, without getting tired.
R> Where should we run the CLI? My laptop?
A> Start with CloudShell: it is already logged in as you, free, and has the CLI installed. On a laptop, sign in with SSO — never paste long-term keys.
K> And when the output is a huge JSON?
A> --query picks the fields you want, --output table makes it readable. Let’s see all the ways to talk to AWS.'''

def bigpic():
    o = t(320, 14, 'Seven doors into the same AWS APIs', 11, 'ink', bold=True)
    doors = [('Console', 'browser', 'blue', 'app'), ('Mobile app', 'phone', 'violet', 'phone'), ('CloudShell', 'browser terminal', 'green', 'chip'), ('AWS CLI v2', 'terminal', 'amber', 'list'), ('SDKs', 'Python, Java, JS…', 'blue', 'gear'), ('IaC', 'CloudFormation, CDK, Terraform', 'red', 'file'), ('IDE toolkits', 'VS Code, JetBrains', 'card', 'laptop')]
    for i, (a, b, tn, icn) in enumerate(doors):
        x = 52 + i * 89
        o += svc(x, 30, icn, a, b, tn, w=80)
    for i in range(7):
        o += arrow(52 + i * 89, 84, 320, 120)
    o += box(150, 122, 340, 40, 'amber', rx=8) + t(320, 140, 'Signed HTTPS API requests (SigV4)', 9, 'ink', bold=True) + t(320, 154, 'same authentication, IAM permissions, CloudTrail logging', 7, 'ink2')
    o += arrow(320, 162, 320, 176)
    o += box(150, 178, 340, 34, 'green', rx=8) + t(320, 199, 'AWS services: EC2, S3, IAM, Lambda, …', 8.4, 'ink', bold=True)
    o += t(320, 230, 'Whatever door you use, IAM decides what you may do and CloudTrail records it.', 7.4, 'ink2')
    return o
BIG = bigfig('Seven ways to access AWS — Management Console, Console mobile app, CloudShell, AWS CLI v2, SDKs, infrastructure as code and IDE toolkits — all send signed API requests, checked by IAM and logged in CloudTrail, to the same AWS services.', bigpic(), h=240)

picture = ('  <p>There is only one way into AWS: its <b>APIs</b>. Everything else is a client that calls them for you:</p>\n' + BIG +
    '\n  <h3>Which door, when?</h3>\n' + table(['Task', 'Best door', 'Why'], [
        ['Learn a new service, look around', 'Console', 'visual, guided, shows options'], ['Quick command without installing anything', 'CloudShell', 'already signed in, CLI pre-installed, free'],
        ['Repeat a task, bulk changes, scripts, cron', 'AWS CLI', 'fast, repeatable, scriptable'], ['Application code that uses AWS', 'SDK (e.g. boto3)', 'retries, pagination, types in your language'],
        ['Create whole environments the same way every time', 'IaC (CloudFormation/CDK/Terraform)', 'versioned, reviewable, repeatable'], ['Check an alarm on the move', 'Console mobile app', 'notifications, quick views']], minw=560))

SOLVE = cli_scene()

def mapfig():
    o = t(320, 16, 'Seven ways to work with AWS', 11, 'ink', bold=True)
    items = [('1', 'Management Console', 'web UI', 'blue'), ('2', 'Console mobile app', 'phone', 'violet'), ('3', 'CloudShell', 'browser terminal', 'green'), ('4', 'AWS CLI v2', 'commands', 'amber'),
             ('5', 'SDKs', 'code libraries', 'blue'), ('6', 'Infrastructure as code', 'templates', 'red'), ('7', 'IDE toolkits', 'VS Code, JetBrains', 'card')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 12 + (i % 4) * 156; y = 32 + (i // 4) * 84
        o += box(x, y, 148, 70, tn, rx=8) + pin(x + 16, y + 16, n) + t(x + 80, y + 34, a, 8.2, 'ink', bold=True) + t(x + 78, y + 54, b, 6.8, 'ink2')
    o += t(320, 210, 'All seven call the same APIs; choose by task, not by habit.', 7.4, 'ink2')
    return o
MAP = bigfig('Map of seven ways to work with AWS: Management Console, Console mobile app, CloudShell, AWS CLI v2, SDKs, infrastructure as code, IDE toolkits.', mapfig(), h=222)

def ac(n, name, tone, d, an, ex, tip, A, use, avoid, plain, how, words, diff, rw, pro):
    return vt(n, name, tone, d, an, ex, tip, '', A, use, avoid, plain, how, words, diff, ['CLF-C02 Domain 3 (ways to access AWS)', 'Developer Associate', 'C-DAC labs'], rw, pro)

A1 = mk(['Sign in', 'Search + Region', 'Click → API'], ['sign in|user + MFA|account URL', 'find|unified search|Region menu', 'act|forms|= API calls'], ['blue', 'amber', 'green'],
        ['sign in as your user with MFA', 'find services with unified search; check the Region', 'each form you submit becomes API calls'],
        [('Sign in', 'User + MFA.', ''), ('Navigate', 'Search, favourites, Region.', ''), ('Act', 'Forms call the APIs.', '')],
        'Management Console', 'Visual and guided.', 'Console', 'Animation: sign in; search and Region; click to API.', 'c1anim')
T1 = ac(1, 'AWS Management Console', 'blue',
    'The <b>AWS Management Console</b> is the web interface for AWS: unified search, favourites, a Region selector, per-service pages with forms and dashboards, and tools like CloudShell and Billing — every action it performs is an API call made with your signed-in identity.',
    'A bank’s branch counter: friendly forms and help, perfect for one-off tasks, slow for a thousand transactions.',
    'Riya uses the console to explore a new service and to check a CloudWatch graph during an incident.',
    'Tip: always glance at the Region in the top-right before creating anything — the #1 “where did my resource go?” cause.', A1,
    'you learn a service, explore settings or need a visual check.', 'you repeat the same task many times or must document it exactly.',
    'AWS’s website for clicking through services.',
    [('Sign in', 'Account URL + MFA.'), ('Search', 'Services, features, docs.'), ('Region', 'Top-right selector.'), ('Favourites', 'Pin services.'), ('Multi-session', 'Several identities in one browser.')],
    [('unified search', 'search box for services, features, docs'), ('Region selector', 'top-right menu'), ('multi-session', 'sign in to several accounts/roles at once')],
    table(['', 'Console', 'CLI'], [['Learning', 'excellent', 'harder'], ['Repeatability', 'low', 'high'], ['Audit of exact steps', 'screenshots', 'script in Git']], minw=420),
    'CLF-C02: the console is one of the ways to access AWS; know when CLI/SDK/IaC fit better.',
    'Turn on multi-session support to keep dev and prod accounts open side by side — clearly labelled — instead of signing in and out.')

A2 = mk(['Install app', 'Sign in', 'Check + act'], ['install|iOS/Android|official app', 'sign in|user + MFA|or SSO', 'use|alarms, health|quick actions'], ['violet', 'amber', 'green'],
        ['install the official AWS Console mobile app', 'sign in with your user (MFA) or SSO', 'view alarms, service health, costs; do small actions'],
        [('Install', 'Official app.', ''), ('Sign in', 'User + MFA.', ''), ('Use', 'Alarms, health, billing, small actions.', '')],
        'Console mobile app', 'On-call in your pocket.', 'Mobile', 'Animation: install app; sign in; check and act.', 'c2anim')
T2 = ac(2, 'AWS Console mobile app', 'violet',
    'The <b>AWS Console mobile application</b> lets you view resources, CloudWatch alarms, AWS Health events and billing, receive push notifications and perform a subset of actions from a phone, signed in as an IAM/Identity Center user with MFA.',
    'A banking app: check balance and approve small things anywhere; big operations still happen at the branch.',
    'Arjun Sir gets a CloudWatch alarm push at night and checks the graph before deciding to log in.',
    'Tip: do not sign in as root on a phone app.', A2,
    'you are on call or travelling.', 'you plan to do real changes from a phone.',
    'The AWS app for your phone.',
    [('Install', 'Official store.'), ('Identity', 'User + MFA.'), ('Alarms', 'Push notifications.'), ('Health', 'AWS Health events.'), ('Cost', 'Billing glance.')],
    [('push notification', 'message on your phone'), ('AWS Health', 'events affecting your resources'), ('on-call', 'person responding to alerts')],
    table(['', 'Console app', 'Web console'], [['Best for', 'checking', 'doing'], ['Actions', 'subset', 'all']], minw=360),
    'Rarely tested, but useful to know as an access method.',
    'Pair it with CloudWatch alarms → SNS → mobile push for real on-call readiness.')

A3 = mk(['Open CloudShell', 'Already signed in', 'Run + keep files'], ['open|>_ icon|in console', 'creds|your session|no keys', 'home|1 GB per Region|persists'], ['green', 'amber', 'blue'],
        ['open CloudShell from the console toolbar', 'it is already authenticated as your console identity', 'run commands; files in $HOME persist (1 GB per Region)'],
        [('Open', 'Toolbar icon.', ''), ('Signed in', 'Same identity as the console.', ''), ('Persist', '1 GB home per Region.', '')],
        'CloudShell', 'Zero-setup terminal.', 'CloudShell', 'Animation: open CloudShell; already signed in; run and keep files.', 'c3anim')
T3 = ac(3, 'AWS CloudShell', 'green',
    '<b>AWS CloudShell</b> is a browser-based shell launched from the console, pre-authenticated with your console credentials and pre-installed with the AWS CLI, Python with boto3, Node.js, git and common tools; it gives 1 GB of persistent home storage per Region at no extra charge.',
    'A ready-made lab bench in the classroom: tools out, power on, just start working.',
    'All labs in this course use CloudShell — no installation, no access keys.',
    'Tip: CloudShell is per Region — files saved in Mumbai’s CloudShell are not in Singapore’s.', A3,
    'you need a terminal with AWS tools now.', 'you need long-running jobs (sessions time out when idle) or heavy compute.',
    'A free terminal inside the AWS website.',
    [('Launch', 'Console toolbar.'), ('Identity', 'Console session.'), ('Tools', 'CLI, Python, git…'), ('Storage', '1 GB $HOME / Region.'), ('Upload/download', 'Actions menu.')],
    [('$HOME', 'your persistent folder'), ('session timeout', 'idle sessions end'), ('VPC environment', 'CloudShell inside your VPC for private resources')],
    table(['', 'CloudShell', 'Laptop CLI'], [['Setup', 'none', 'install + sign in'], ['Credentials', 'console session', 'SSO profile (recommended)'], ['Reach private VPC resources', 'with VPC environment', 'via VPN/bastion']], minw=420),
    'Answers “run CLI commands without installing anything or storing credentials”.',
    'Use the Actions menu to upload a script or download results; delete large files to keep under 1 GB.')

A4 = mk(['Type command', 'Credentials + Region', 'Shape output'], ['type|aws s3 ls|service op', 'find|provider chain|profile, Region', 'shape|--query|--output table'], ['amber', 'blue', 'green'],
        ['type: aws service operation [options]', 'the CLI finds credentials and Region automatically', 'shape the JSON with --query and --output'],
        [('Command', 'aws service operation options.', ''), ('Context', 'Credentials, Region, profile.', ''), ('Output', 'JSON, table, text, YAML.', '')],
        'AWS CLI v2', 'Repeatable power.', 'CLI', 'Animation: type command; credentials and Region; shape output.', 'c4anim')
T4 = ac(4, 'AWS CLI version 2', 'amber',
    'The <b>AWS Command Line Interface (v2)</b> is a unified tool to call almost every AWS API from a terminal: <code>aws &lt;service&gt; &lt;operation&gt; [--options]</code>, with profiles, SSO sign-in, automatic pagination, waiters, JMESPath filtering (<code>--query</code>) and output formats (json, yaml, text, table).',
    'A TV remote with every button labelled: once you know the buttons, you never walk to the TV again.',
    '<code>aws s3 sync ./notes s3://eduspark-content/notes/</code> publishes all new lecture notes in one command.',
    'Tip: v2 is the current version — install v2, not v1; check with <code>aws --version</code>.', A4,
    'you repeat, script or document tasks.', 'you paste long-term keys on shared laptops — use SSO profiles.',
    'A typed command tool for controlling AWS.',
    [('Install', 'v2 bundled installer.'), ('Sign in', 'aws configure sso / CloudShell.'), ('Command', 'service + operation.'), ('Query', 'JMESPath.'), ('Script', 'Bash/PowerShell.')],
    [('profile', 'named set of settings/credentials'), ('JMESPath', 'query language for JSON'), ('waiter', 'command that waits for a state')],
    table(['Format', 'Best for'], [['json (default)', 'scripts, jq'], ['table', 'humans'], ['text', 'shell loops (tab-separated)'], ['yaml', 'readable config-like output']], minw=360),
    'CLF-C02 lists the CLI as a programmatic access method; Developer Associate tests --query, pagination and profiles.',
    'Use <code>--dry-run</code> on EC2 commands to test permissions without creating anything, and <code>aws &lt;cmd&gt; help</code> for full docs offline.')

A5 = mk(['Import SDK', 'Create client', 'Call + handle'], ['import|boto3|aws-sdk', 'client|s3, ec2|Region from env', 'call|paginate|catch errors'], ['blue', 'amber', 'green'],
        ['import the SDK for your language', 'create a client; credentials come from the same chain as the CLI', 'call APIs with pagination, retries and error handling'],
        [('Import', 'boto3, AWS SDK for Java/JS/.NET/Go…', ''), ('Client', 'Credentials from the provider chain.', ''), ('Call', 'Paginators, waiters, exceptions.', '')],
        'SDKs', 'AWS inside your code.', 'SDK', 'Animation: import SDK; create client; call and handle.', 'c5anim')
T5 = ac(5, 'AWS SDKs', 'blue',
    '<b>AWS SDKs</b> are language libraries (Python boto3, Java, JavaScript/TypeScript, .NET, Go, Rust, PHP, Ruby, C++, Kotlin, Swift) that wrap the AWS APIs with clients, paginators, waiters, automatic retries and the same credential provider chain as the CLI, so applications can use AWS services from code.',
    'A power socket in the wall: your appliance (app) plugs in and uses electricity (AWS) without knowing how the grid works.',
    'TiffinGo’s order API uses boto3 to put messages on SQS and read menu items from DynamoDB.',
    'Tip: never put keys in code — on AWS compute the SDK picks up the role’s temporary credentials automatically.', A5,
    'your application calls AWS services.', 'a one-off admin task — use the CLI.',
    'Code libraries for using AWS from your programs.',
    [('Install', 'pip install boto3.'), ('Client', 'boto3.client("s3").'), ('Paginate', 'get_paginator().'), ('Errors', 'ClientError codes.'), ('Retries', 'Automatic backoff.')],
    [('client', 'low-level API object'), ('paginator', 'iterates all pages'), ('ClientError', 'exception with AWS error code')],
    table(['Language', 'SDK'], [['Python', 'boto3'], ['JavaScript/TypeScript', 'AWS SDK for JavaScript v3'], ['Java', 'AWS SDK for Java 2.x']], minw=360),
    'Developer Associate tests SDK error handling, retries and credentials.',
    'Data engineers: use paginators on list calls — forgetting them silently returns only the first page.')

A6 = mk(['Write template', 'Deploy stack', 'Same every time'], ['template|YAML/JSON|or code', 'deploy|CloudFormation|Terraform', 'repeat|dev, test, prod|identical'], ['red', 'amber', 'green'],
        ['describe resources in a template or code', 'the IaC tool creates them in the right order', 'deploy the same environment again and again'],
        [('Write', 'Template / CDK code.', ''), ('Deploy', 'Tool works out order and dependencies.', ''), ('Repeat', 'Identical environments; tear down cleanly.', '')],
        'Infrastructure as code', 'Environments from files.', 'IaC', 'Animation: write template; deploy stack; same every time.', 'c6anim')
T6 = ac(6, 'Infrastructure as code (IaC)', 'red',
    '<b>Infrastructure as code</b> defines AWS resources in version-controlled files — AWS CloudFormation templates (YAML/JSON), AWS CDK (TypeScript, Python, Java…) that synthesises CloudFormation, or Terraform (HCL) — so environments are created, changed and deleted consistently and reviewably.',
    'A building blueprint: the same drawing builds identical houses, and changes are marked on the drawing first.',
    'TiffinGo’s dev, test and prod environments come from one CloudFormation template with different parameters.',
    'Tip: if you clicked it in the console, you cannot easily repeat it; if it is in a template, you can.', A6,
    'you build environments more than once or must review changes.', 'you are just exploring a service for the first time.',
    'Building AWS setups from text files instead of clicks.',
    [('Write', 'Template/code.'), ('Review', 'Pull request.'), ('Plan', 'Change set / terraform plan.'), ('Apply', 'Deploy.'), ('Destroy', 'Delete stack.')],
    [('stack', 'resources managed as one unit'), ('change set', 'preview of changes'), ('drift', 'manual changes outside the template')],
    table(['Tool', 'Language', 'State'], [['CloudFormation', 'YAML/JSON', 'managed by AWS'], ['CDK', 'TypeScript, Python…', 'via CloudFormation'], ['Terraform', 'HCL', 'state file you manage']], minw=420),
    'CLF-C02: CloudFormation = IaC; Module 9 goes deep.',
    'Run a drift check after incidents — someone always “just fixes it in the console”.')

A7 = mk(['Install toolkit', 'Sign in', 'Browse + deploy'], ['install|VS Code|JetBrains', 'sign in|SSO profile|same chain', 'use|explorer|deploy, debug'], ['card', 'amber', 'green'],
        ['install the AWS Toolkit in your IDE', 'sign in with an SSO profile', 'browse resources, deploy and debug from the editor'],
        [('Install', 'VS Code / JetBrains extension.', ''), ('Sign in', 'SSO profile.', ''), ('Use', 'Explorer, Lambda deploy, logs, AI help.', '')],
        'IDE toolkits', 'AWS inside your editor.', 'IDE', 'Animation: install toolkit; sign in; browse and deploy.', 'c7anim')
T7 = ac(7, 'IDE toolkits and AI assistants', 'card',
    '<b>AWS Toolkits</b> for VS Code and JetBrains IDEs add an AWS explorer, Lambda/serverless deploy and debug, CloudWatch log viewing and S3 browsing inside the editor, and Amazon Q Developer adds AI help to write, explain and transform code and AWS commands.',
    'A cook’s station with the spice rack and the oven controls within arm’s reach — no walking around the kitchen.',
    'A developer tails Lambda logs and redeploys a function without leaving VS Code.',
    'Tip: toolkits use the same profiles as the CLI — set up SSO once, use it everywhere.', A7,
    'you write application code daily.', 'you need a repeatable deployment — use IaC + CI/CD, not IDE clicks.',
    'AWS tools inside your code editor.',
    [('Install', 'Extension.'), ('Profile', 'SSO.'), ('Explorer', 'Browse resources.'), ('Deploy', 'Lambda/SAM.'), ('Logs', 'Tail CloudWatch.')],
    [('AWS Toolkit', 'IDE extension'), ('SAM', 'Serverless Application Model'), ('Amazon Q Developer', 'AWS AI coding assistant')],
    table(['', 'IDE toolkit', 'CI/CD pipeline'], [['Who', 'one developer', 'team'], ['Use for', 'build and debug', 'releasing to prod']], minw=360),
    'Not a core CLF topic, but common in developer interviews.',
    'Review AI-suggested commands before running them — especially anything with delete, put-bucket-policy or IAM.')

SUMMARY = table(['#', 'Door', 'Best for', 'Credentials'], [
    ['1', 'Console', 'learning, visual checks', 'user + MFA'], ['2', 'Mobile app', 'on-call checks', 'user + MFA'], ['3', 'CloudShell', 'instant CLI', 'console session'],
    ['4', 'CLI v2', 'scripts, bulk, docs', 'SSO profile / role'], ['5', 'SDKs', 'application code', 'role (on AWS) / SSO (dev)'], ['6', 'IaC', 'whole environments', 'pipeline role'], ['7', 'IDE toolkits', 'developer workflow', 'SSO profile']], minw=560)

TYPES = ('  <p>Seven ways to work with AWS, each in the same pattern: definition, plain words, analogy, internal steps, animation, differences, real-world example and an expert tip.</p>\n'
         + challenge(['In what order does the CLI look for credentials?', 'Which door needs no installation and no keys?', 'Which output format is best for a shell loop?'], 'types 4, 3 and 4') + MAP
         + jump(['Console', 'Mobile', 'CloudShell', 'CLI', 'SDKs', 'IaC', 'IDE']) + T1 + T2 + T3 + T4 + T5 + T6 + T7
         + '\n  <h3 style="margin-top:34px">All seven side by side</h3>\n' + SUMMARY)

parts = wwu([
    ('Command structure', 'aws &lt;service&gt; &lt;operation&gt; [options].', 'Predictable everywhere.', '<code>aws ec2 describe-instances</code>.'),
    ('Credentials', 'provider chain, profiles, SSO.', 'Who you are.', '<code>aws configure sso</code>.'),
    ('Configuration', 'Region, output, retries.', 'Where and how.', '<code>~/.aws/config</code>.'),
    ('Output shaping', '--query, --output.', 'Only what you need.', '<code>--query "Buckets[].Name"</code>.'),
    ('Pagination and waiters', 'big lists, async resources.', 'Correct and complete scripts.', '<code>--max-items</code>, <code>aws ec2 wait</code>.'),
    ('Safety', '--dry-run, help, profiles per account.', 'Avoid mistakes.', '<code>--dry-run</code>.')])

DEEP = ('  <h3>The two config files</h3>\n' + code('ini', '~/.aws/config (settings and SSO profiles)', '[default]\nregion = ap-south-1\noutput = json\n\n[profile tiffingo-dev]\nsso_session = tiffingo\nsso_account_id = 111122223333\nsso_role_name = Developer\nregion = ap-south-1\n\n[sso-session tiffingo]\nsso_start_url = https://tiffingo.awsapps.com/start\nsso_region = ap-south-1\nsso_registration_scopes = sso:account:access') +
    code('ini', '~/.aws/credentials (long-term keys — avoid when you can)', '[legacy-user]\naws_access_key_id = AKIA…\naws_secret_access_key = …') +
    '  <p>Use a profile with <code>--profile tiffingo-dev</code> or <code>export AWS_PROFILE=tiffingo-dev</code>; sign in with <code>aws sso login --profile tiffingo-dev</code>.</p>\n'
    '  <h3>JMESPath in five patterns</h3>\n' + table(['Want', 'Query'], [
        ['one field from every item', '<code>Buckets[].Name</code>'], ['several fields', '<code>Reservations[].Instances[].[InstanceId,State.Name]</code>'],
        ['filter', '<code>Reservations[].Instances[?State.Name==\'running\'].InstanceId</code>'], ['count', '<code>length(Buckets)</code>'], ['rename keys', '<code>Buckets[].{name:Name,created:CreationDate}</code>']], minw=520) +
    '  <h3>Pagination: three switches</h3>\n  <ul><li>Default: the CLI fetches <b>all pages</b> for you.</li><li><code>--max-items N</code> stops after N items and prints a <code>NextToken</code>; continue with <code>--starting-token</code>.</li><li><code>--page-size N</code> asks AWS for smaller pages (fewer timeouts on huge lists); <code>--no-paginate</code> returns only the first page.</li></ul>')

clouds = vendor_tabs('<p><b>AWS:</b> Management Console, Console mobile app, CloudShell, AWS CLI v2, SDKs, CloudFormation/CDK, AWS Toolkits.</p>',
    '<p><b>Azure:</b> Azure portal, Azure mobile app, Cloud Shell (Bash/PowerShell), Azure CLI and PowerShell Az module, SDKs, ARM/Bicep.</p>',
    '<p><b>Google Cloud:</b> Google Cloud console, mobile app, Cloud Shell, gcloud/gsutil (gcloud storage), client libraries, Infrastructure Manager/Terraform.</p>') + \
    cloud3([['Web UI', 'Management Console', 'Azure portal', 'Cloud console'], ['Browser shell', 'CloudShell', 'Cloud Shell', 'Cloud Shell'], ['CLI', 'aws', 'az', 'gcloud'], ['Native IaC', 'CloudFormation / CDK', 'ARM / Bicep', 'Infrastructure Manager']])

MOCKA.extend([
 mock('aws', ['Console Home'], ['Recently visited', 'Favorites', 'Applications'], 'Favorites', [('Search', 'S3'), ('Region', '▾ Asia Pacific (Mumbai)'), ('Multi-session', '[x] Enable multi-session support')], 'Open S3'),
 mock('aws', ['CloudShell', 'ap-south-1'], ['Terminal', 'Actions'], 'Terminal', [('Command', 'aws ec2 describe-regions --output table'), ('Actions', '▾ Upload file · Download file · Restart')], 'Run'),
 mock('aws', ['S3', 'Buckets', 'cli-lab-…'], ['Objects', 'Properties', 'Permissions'], 'Objects', [('Object', 'hello.txt'), ('Share', 'Generate presigned URL (5 min)')], 'Delete'),
])

STEP1 = astep('1 · Know your CLI and where it gets credentials',
    ['Console: search box → type <i>S3</i> → star it as a favourite; check the Region is Mumbai.', 'Open [[CloudShell]] from the toolbar.'],
    'aws --version\naws configure list\naws sts get-caller-identity --query Arn --output text\nls -la ~ && df -h ~',
    '<code>aws-cli/2.x</code>, credentials of type <code>container-role</code> (CloudShell), your user ARN, and your 1 GB home directory.',
    'On a laptop you would instead run <code>aws configure sso</code> once and <code>aws sso login</code> each day — temporary credentials, nothing to leak.')

STEP2 = astep('2 · Shape output with --query and --output',
    ['No console equivalent — this is the CLI’s superpower. Compare the console’s EC2 → Global View with the commands.'],
    "aws ec2 describe-regions --output json | head -20\naws ec2 describe-regions --query 'Regions[].RegionName' --output text\naws ec2 describe-regions --query 'Regions[?starts_with(RegionName, `ap-`)].[RegionName,Endpoint]' --output table\naws ec2 describe-availability-zones --query 'length(AvailabilityZones)'\naws ssm get-parameters-by-path --path /aws/service/global-infrastructure/services --max-items 5 --query 'Parameters[].Value'",
    'raw JSON, then a single tab-separated line of Region names, a neat table of only Asia-Pacific Regions, the number 3, and five service names plus a <code>NextToken</code> for the next page.',
    '<code>--query</code> runs on your machine after the response arrives; it saves screen space, not API calls.')

STEP3 = astep('3 · A full create → use → share → delete cycle from the CLI',
    ['Console equivalent: [[S3]] → [[Create bucket]] → upload <code>hello.txt</code> → [[Actions]] → [[Share with a presigned URL]] → empty and delete the bucket.'],
    "B=cli-lab-$(date +%s); echo $B\naws s3 mb s3://$B --region ap-south-1\necho \"Hello from $(aws sts get-caller-identity --query Arn --output text)\" > hello.txt\naws s3 cp hello.txt s3://$B/\naws s3 ls s3://$B/\nURL=$(aws s3 presign s3://$B/hello.txt --expires-in 300); curl -s \"$URL\"\naws ec2 run-instances --dry-run --image-id resolve:ssm:/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 --instance-type t3.micro\naws s3 rb s3://$B --force",
    '<code>make_bucket</code>, <code>upload</code>, the object listed, your text printed via the presigned URL, then <code>An error occurred (DryRunOperation) … Request would have succeeded, but DryRun flag is set.</code> (permission check without launching) and <code>remove_bucket</code>.',
    'Eight lines did what takes about twenty console clicks — and you can paste them into a file and run them again tomorrow.')

prac = practical(AWS_INTRO + ' Everything is created and deleted inside the lab. Cost: zero (a few S3 requests are within the Free Tier).', [AWS_SETUP, STEP1, STEP2, STEP3],
    cleanup='Step 3 already deleted the bucket (<code>aws s3 rb --force</code>). Check: <code>aws s3 ls | grep cli-lab</code> prints nothing. Remove <code>hello.txt</code> from CloudShell with <code>rm hello.txt</code>.')

mist = mistakes([
    ['Creating resources in the wrong Region.', 'Region menu not checked.', 'Check top-right; set <code>region</code> in your profile.'],
    ['Pasting access keys on laptops and in scripts.', 'Old tutorials.', 'CloudShell or <code>aws configure sso</code>.'],
    ['Parsing JSON with grep.', 'Habit.', 'Use <code>--query</code> or <code>jq</code>.'],
    ['Scripts that read only the first page.', '<code>--no-paginate</code> or SDK list without paginator.', 'Let the CLI paginate; use SDK paginators.'],
    ['Using the CLI v1 from old images.', 'Pre-installed packages.', 'Install CLI v2; check <code>aws --version</code>.'],
    ['Running a copied delete command without reading it.', 'Speed.', 'Read every command; use <code>--dry-run</code> where available.']])

cert = table(['Exam / syllabus', 'What is asked'], [['AWS CLF-C02', 'Ways to access AWS: console, CLI, SDKs, IaC; programmatic vs console access (Domain 3).'], ['Developer Associate', 'Credential provider chain, profiles, --query, pagination, SDK retries.'], ['C-DAC PGCP-BDA', 'Cloud labs using CLI and console.']], minw=560) + \
    '\n  <h3>Try exam-style questions</h3>\n' + qx('Which lets you run AWS CLI commands in the browser without installing anything?', ['AWS CloudShell', 'AWS Cloud9 only', 'Amazon WorkSpaces', 'AWS Config'], 0, 'CloudShell.') + \
    qx('Which is infrastructure as code on AWS?', ['CloudTrail', 'CloudFormation', 'CloudWatch', 'CloudFront'], 1, 'CloudFormation.') + \
    qx('An application on EC2 needs to call S3. How should the SDK get credentials?', ['access keys in code', 'an IAM role attached to the instance', 'root keys', 'environment file in Git'], 1, 'Provider chain → instance role.')

from deep_v3 import HOOD, ROLES, DOMAINS, PRO, PROJ, SIM, NEWBIE, LADDER

assemble_v2(HERE, story_h2='A Saturday of clicking vs 40 seconds of script', hook_html=hk,
    narration='Kabir created 60 student folders and permissions by hand in the console over a whole Saturday; half had typos. Riya’s 12-line CLI loop did the same in 40 seconds and could be run again for the next batch.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='AWS Management Console and CLI',
    formal='The <b>AWS Management Console</b> is AWS’s web-based interface for managing services; the <b>AWS Command Line Interface (CLI)</b> is a unified tool for calling AWS service APIs from a terminal. Both — like CloudShell, the SDKs, infrastructure-as-code tools and IDE toolkits — send authenticated API requests that IAM authorises and CloudTrail records.',
    simple='The console is the AWS website you click through; the CLI is the same power as typed commands you can save and repeat.',
    interview=['“I use the console to explore and verify, the CLI for repeatable tasks and scripts, SDKs inside applications, and CloudFormation or Terraform for whole environments — they all call the same APIs.”', '“On laptops I use aws configure sso for short-lived credentials; on AWS compute the SDK picks up the role automatically, so no keys are stored anywhere.”'],
    terms_rows=[('Console', 'AWS web interface.'), ('CloudShell', 'Browser terminal, pre-authenticated.'), ('CLI v2', 'aws command-line tool.'), ('Profile', 'Named settings/credentials.'), ('Provider chain', 'Order in which credentials are found.'), ('JMESPath', 'Query language for --query.'), ('Pagination', 'Results returned in pages.'), ('Dry run', 'Permission check without acting.')],
    exam='CLF-C02 asks which access method fits a scenario; Developer Associate tests profiles, credentials and --query.',
    picture_h2='Seven doors, one set of APIs', picture_html=NEWBIE + picture,
    after_picture=[('types', 'Types, one by one', 'Seven ways to work with AWS, one by one', TYPES)],
    how_h2='What happens when you run an AWS CLI command', how_intro='From keyboard to table.', how_anim=SOLVE,
    parts_h2='Six parts of using the CLI well', parts_html=parts, lv='',
    myth_rows=[('The CLI can do things the console cannot (and vice versa).', 'Both call the same APIs; coverage is near-identical.', 'Big picture.'), ('--query reduces API calls.', 'It filters locally after the response.', 'Animation step 6.'), ('Access keys are needed for the CLI.', 'CloudShell and SSO need no long-term keys.', 'Type 3.')],
    extra_secs=[('ladder', 'Learn at your level', 'From curious beginner to expert — pick your level', LADDER), ('deep', 'Deep dive', 'Config files, profiles, JMESPath patterns, pagination', DEEP), ('hood', 'Under the hood', 'Provider chain, SSO token flow, retries, CloudShell internals, --debug', HOOD), ('roles', 'By role', 'How developers, data, ML, DevOps and security people use it', ROLES), ('domains', 'By domain', 'Access patterns by industry', DOMAINS), ('pro', 'For working professionals', 'Scripts, errors, cheat sheet, checklist', PRO)],
    clouds_html=clouds, practical_html=prac + '\n  <h3 id="simulator">Practice without an account: simulator</h3>\n  <p>Type the real commands — the simulator answers like CloudShell and shows what each one touches.</p>\n' + SIM, mistakes_html=mist, cert_html=cert, project_html=PROJ,
    can_now=['Choose the right way to access AWS for a task.', 'Explain how the CLI finds credentials and Region.', 'Shape output with --query and --output; handle pagination.', 'Run a full create–use–delete cycle from the CLI.', 'Set up SSO profiles instead of access keys.'],
    next_html='Module 1 complete. Next: <a href="../../02-security/01-iam-users-groups-roles-and-policies/">2.1 IAM: users, groups, roles and policies</a>.',
    pre='<b>Before you start:</b> Lessons 1.1–1.3 and an admin user (Lesson 1.2).')
