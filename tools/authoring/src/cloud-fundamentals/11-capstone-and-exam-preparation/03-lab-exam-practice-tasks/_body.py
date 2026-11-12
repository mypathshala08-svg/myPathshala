import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
def cap(frames, steps, title, intro, panel, aria, hid, delay=5500):
    return anim_one('Animated', title, intro, panel, aria, cap_frames(frames, steps), [s[0] + '.' for s in steps], delay=delay, hid=hid)
def row3(k, items, tones, cap_):
    o = ''
    for i, l in enumerate(items):
        on = i <= k
        o += box(20 + i * 112, 34, 100, 74, tones[i] if on else 'card', rx=8)
        for j, w in enumerate(l.split('|')): o += t(70 + i * 112, 60 + j * 14, w, 7.2 if j == 0 else 6.6, 'ink', bold=(j == 0))
        if i < 2: o += arrow(120 + i * 112, 71, 132 + i * 112, 71)
    return o + t(180, 132, cap_, 7.2, 'ink', bold=True)
def mk(t3, items, tones, caps, steps, ttl, intro, panel, aria, hid):
    return cap([t(180, 12, t3[k], 9, 'ink', bold=True) + row3(k, items, tones, caps[k]) for k in range(3)], steps, ttl, intro, panel, aria, hid)
def vt(n, name, tone, d, an, sc, ex, gd, anim, use, avoid, plain, how, words, diff, where, rw, pro):
    return vtype(n, name, tone, d, an, sc, ex, gd, anim, use, avoid, plain=plain, how=how, words=words, diff=diff, where=where, realworld=rw, pro=pro)


hk = hook('Arjun finished every task in the lab exam — and lost a third of the marks. The examiner opened his web page and got a timeout.',
    'His VM was running, nginx was installed, but port 80 was never opened. He had not <b>verified</b> from outside. Lab exams mark <b>working results</b>, not effort. This lesson gives you the <b>seven kinds of lab tasks</b> that cloud practical exams use, a <b>plan–build–verify–evidence</b> routine, twelve timed practice tasks with marking rubrics, and a full mock lab on <b>your own</b> account in AWS, Azure or Google Cloud.',
    ['Build only what the task asks — then prove it works from outside.', 'Keep evidence: command output, URLs, screenshots.', 'Clean up and stay inside free-tier limits.'])

def story_scene():
    o = t(180, 12, 'Built vs verified', 9, 'ink', bold=True)
    o += box(8, 28, 160, 74, 'red', rx=8) + t(88, 48, 'VM running, nginx up', 8.2, 'ink', bold=True) + t(88, 64, 'port 80 closed', 7, 'ink2') + t(88, 78, 'never tested from outside', 7, 'ink2') + t(88, 92, 'examiner: timeout', 7.4, 'ink', bold=True)
    o += box(192, 28, 160, 74, 'green', rx=8) + t(272, 48, 'Same build + verify', 8.2, 'ink', bold=True) + t(272, 64, 'curl from laptop', 7, 'ink2') + t(272, 78, 'output saved as evidence', 7, 'ink2') + t(272, 92, 'full marks', 7.4, 'ink', bold=True)
    o += t(180, 122, 'A task is done only when you have seen it work', 7.6, 'ink', bold=True)
    return o
scene_svg = scene('Left: VM running with nginx but port 80 closed and never tested — examiner gets a timeout. Right: the same build plus a curl test and saved output — full marks.', story_scene(), 'Verify from <tspan font-weight="700" class="s-acc">outside</tspan>, then move on.', h=132)
dialogue = '''A> Ma’am, everything was created. Why did I lose marks?
M> The examiner checks the result. Your page did not load from outside — the firewall rule was missing.
K> How do we avoid that in a timed exam?
M> After every task: verify the way the examiner will, save the output, then go to the next task.
A> And if I get stuck?
M> Skip, finish the others, come back. Partial marks come from working pieces, not half-built everything.'''

def methodfig():
    o = t(320, 16, 'Lab exam routine: P-B-V-E-C', 11, 'ink', bold=True)
    S = [('P', 'Plan', 'read all tasks, order by marks', 'blue'), ('B', 'Build', 'CLI or console, minimum needed', 'amber'), ('V', 'Verify', 'test like the examiner', 'green'), ('E', 'Evidence', 'output, URL, screenshot', 'violet'), ('C', 'Clean up', 'only after marking', 'red')]
    for i, (n, a, b, tn) in enumerate(S):
        x = 12 + i * 126
        o += box(x, 36, 118, 80, tn, rx=8) + pin(x + 14, 50, n) + t(x + 59, 74, a, 8.6, 'ink', bold=True) + t(x + 59, 94, b, 6.6, 'ink2')
        if i < 4: o += arrow(x + 118, 76, x + 126, 76)
    o += t(320, 140, 'Repeat B-V-E for each task; spend the first 5 minutes on P and the last 10 on a final check.', 7.4, 'ink2')
    return o
METHOD = bigfig('Five-step lab routine: plan (read all tasks, order by marks), build (minimum needed), verify (test like the examiner), evidence (output, URL, screenshot), clean up (only after marking).', methodfig(), h=150)

picture = ('  <p>A lab exam gives you a set of tasks, a time limit and an account. Marks come from <b>working results</b> the examiner can check. One routine covers every task:</p>\n' + METHOD +
           '\n  <h3>What examiners usually check</h3>\n' + table(['Check', 'Example', 'How you prove it'], [
               ['Resource exists with the right settings', 'VM size, Region, tags', '<code>describe</code>/<code>show</code> output'], ['It works from outside', 'web page loads', '<code>curl</code> from your laptop or Cloud Shell'],
               ['Security is right', 'only port 80/22 open, bucket not public unless asked', 'firewall/policy listing'], ['Naming and tagging', 'names and tags as given', 'tag query'], ['Nothing extra or wasteful', 'no oversized VMs, no leftovers', 'resource list']], minw=600))

RN = {'read': (4, 54, 50, 50, 'app', 'Tasks', 'read all'), 'plan': (66, 4, 62, 46, 'meter', 'Plan', 'order'), 'build': (66, 104, 62, 46, 'gear', 'Build', 'CLI'),
      'ver': (142, 54, 60, 50, 'shield', 'Verify', 'curl'), 'evi': (216, 4, 62, 46, 'chart', 'Evidence', 'save'), 'next': (216, 104, 62, 46, 'cloud', 'Next task', 'repeat'), 'done': (292, 54, 64, 50, 'user', 'Submit', 'final check')}
RS = [dict(on=['read'], hot='read', move=None, head='Step 1 · Read every task first (5 min)', text='Three tasks: web VM (10 marks), static site (6), budget + tags (4). Note exact names,', text2='Region, size and tags.', svc='Underline every value you must type'),
      dict(on=['read', 'plan'], hot='plan', move=(54, 79, 72, 30, 'order'), head='Step 2 · Plan the order', text='Highest marks and longest waits first: start the VM (it boots while you do other work),', text2='then the static site, then budget and tags.', svc='Overlap waiting time with other tasks'),
      dict(on=['plan', 'build'], hot='build', move=(97, 50, 97, 104, 'build'), head='Step 3 · Build the minimum', text='Launch the VM with a startup script and open only port 80. Do not add load balancers', text2='or extra disks the task did not ask for.', svc='Extra resources can lose marks and money'),
      dict(on=['build', 'ver'], hot='ver', move=(128, 127, 150, 100, 'test'), head='Step 4 · Verify like the examiner', text='curl http://PUBLIC_IP from outside the VM. Timeout? → firewall. 404/default page? →', text2='startup script. Fix now, while you still remember the context.', svc='The examiner will run the same test'),
      dict(on=['ver', 'evi'], hot='evi', move=(165, 54, 216, 20, 'save'), head='Step 5 · Save evidence', text='Copy the curl output, the instance ID and the public IP into your answer sheet; take', text2='a screenshot if the exam asks for one.', svc='Evidence protects marks if something changes later'),
      dict(on=list(RN), hot='done', move=(278, 127, 298, 100, 'submit'), head='Step 6 · Next task, then a final check', text='Repeat build–verify–evidence for each task. Last 10 minutes: re-run every verification.', text2='Clean up only after the examiner has marked (or when told).', svc='Never delete before marking')]
SOLVE = flow_anim('Running a lab exam, step by step', 'The routine applied to a three-task lab.', 'Lab routine', 'Animation: read all tasks; plan the order; build the minimum; verify from outside; save evidence; next task and final check.', RN, RS, hid='labflow')

def mapfig():
    o = t(320, 16, 'Seven kinds of lab tasks', 11, 'ink', bold=True)
    items = [('1', 'Identity', 'user, group, role, MFA', 'red'), ('2', 'Compute', 'VM + web server', 'amber'), ('3', 'Storage', 'bucket, static site', 'blue'), ('4', 'Network', 'VPC, subnet, firewall', 'violet'),
             ('5', 'Database', 'managed SQL / NoSQL', 'green'), ('6', 'Serverless', 'function + trigger', 'amber'), ('7', 'Monitor & cost', 'alarm, budget, tags', 'card')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 12 + (i % 4) * 156; y = 32 + (i // 4) * 84
        o += box(x, y, 148, 70, tn, rx=8) + pin(x + 16, y + 16, n) + t(x + 80, y + 34, a, 8.4, 'ink', bold=True) + t(x + 78, y + 54, b, 6.8, 'ink2')
    o += t(320, 210, 'Most lab papers mix three or four of these — practise each until you can do it from memory.', 7.4, 'ink2')
    return o
MAP = bigfig('Map of seven lab task kinds: identity, compute, storage, network, database, serverless, monitoring and cost.', mapfig(), h=222)

def lt(n, name, tone, d, an, ex, tip, A, use, plain, how, words, diff, rw, pro):
    return vt(n, name, tone, d, an, ex, tip, '', A, use, 'you build it without checking it from outside.', plain, how, words, diff, ['C-DAC lab exam', 'AWS Cloud Quest / labs', 'Microsoft Learn sandbox', 'Google Skills Boost labs'], rw, pro)

A1 = mk(['Who needs access', 'Least privilege', 'Prove it'], ['who|person or app|group', 'grant|policy / role|scoped', 'prove|allowed works|denied fails'], ['blue', 'amber', 'green'],
        ['identify who needs access: a person, a group or an application', 'grant only the permissions the task names', 'prove: the allowed action works and a forbidden one fails'],
        [('Who', 'Person, group or app?', ''), ('Grant', 'Smallest policy or role.', ''), ('Prove', 'Allowed works; denied fails.', '')],
        'Identity tasks', 'Show both allow and deny.', 'Identity', 'Animation: who needs access; least privilege; prove it.', 'l1anim')
T1 = lt(1, 'Identity tasks', 'red',
    '<b>Identity tasks</b> ask you to create users, groups or roles and give them exactly the permissions described — e.g. “create group <i>auditors</i> with read-only access”, “give the VM a role to read one bucket”, “enforce MFA” — and are marked by testing what the identity can and cannot do.',
    'Giving a guest a room key that opens only their room, then checking it does not open the next door.',
    'Example: “Create user <i>intern1</i> in group <i>readers</i> with ReadOnlyAccess.”',
    'Tip: test the deny case too (e.g. try to delete something with the read-only identity) — examiners love it.', A1,
    'the task names users, groups, roles, policies or MFA.',
    'Tasks about who can do what in the account.',
    [('Read', 'Exact names and permissions.'), ('Create', 'User/group/role.'), ('Attach', 'Managed policy or role.'), ('Test', 'Allowed + denied action.'), ('Evidence', 'Policy listing + test output.')],
    [('managed policy', 'provider-written permission set'), ('role assignment', 'Azure/GCP binding of role to identity at a scope'), ('AccessDenied', 'the error that proves a deny')],
    table(['', 'AWS', 'Azure', 'Google Cloud'], [['Group', 'IAM group', 'Entra ID group', 'Google group'], ['App identity', 'IAM role', 'managed identity', 'service account'], ['Read-only', 'ReadOnlyAccess', 'Reader', 'roles/viewer']], minw=480),
    'Lab papers often begin with an identity task because every other task depends on it.',
    'Never use the root/owner identity for the tasks themselves — some labs check CloudTrail/Activity Log for that.')

A2 = mk(['Launch', 'Install', 'Open + test'], ['launch|size, image|Region, key', 'install|startup script|nginx/Apache', 'open|port 80|curl from outside'], ['amber', 'blue', 'green'],
        ['launch the VM with the exact size, image and Region', 'install software with a startup script (user data / cloud-init)', 'open only the needed port and test from outside'],
        [('Launch', 'Exact size, image, Region, tags.', ''), ('Install', 'Startup script: no manual SSH needed.', ''), ('Test', 'Open port; curl from outside.', '')],
        'Compute tasks', 'Startup script + firewall + curl.', 'Compute', 'Animation: launch; install; open port and test.', 'l2anim')
T2 = lt(2, 'Compute tasks', 'amber',
    '<b>Compute tasks</b> ask you to launch a virtual machine with given settings and make it serve something — usually a web page — which tests image and size selection, startup scripts, key pairs, firewall rules and public IPs.',
    'Hiring a stall at a fair: right size, right place, stock it, then open the shutter so customers can see it.',
    'Example: “Launch a t3.micro / B1s / e2-micro in Mumbai that shows ‘Hello from <i>yourname</i>’ on port 80.”',
    'Tip: a startup script makes the build repeatable — if it fails, terminate and relaunch rather than debugging by hand under time pressure.', A2,
    'the task asks for a VM, a web server or SSH access.',
    'Tasks where you start a server and make it serve a web page.',
    [('Size/image', 'Free-tier eligible.'), ('Script', 'User data / custom data / startup-script.'), ('Firewall', 'Port 80 (and 22 only if asked).'), ('Test', 'curl public IP.'), ('Evidence', 'ID, IP, output.')],
    [('user data', 'AWS startup script'), ('cloud-init', 'Linux first-boot configuration, used by Azure custom data'), ('startup-script', 'Google metadata key for boot scripts')],
    table(['', 'AWS', 'Azure', 'Google Cloud'], [['Startup script', '--user-data', '--custom-data', '--metadata startup-script'], ['Open port', 'security group rule', 'az vm open-port (NSG)', 'firewall rule + tag'], ['Free-tier size', 't3.micro / t2.micro', 'B1s', 'e2-micro (us regions)']], minw=480),
    'The “web page on a VM” task is the single most common cloud lab task.',
    'Wait 1–2 minutes after launch before testing — the script needs time; a timeout is usually the firewall, a default page usually the script.')

A3 = mk(['Create bucket', 'Upload + configure', 'Access test'], ['bucket|unique name|Region', 'configure|website, lifecycle|versioning', 'test|URL loads|or is denied'], ['blue', 'amber', 'green'],
        ['create the bucket or storage account with a unique name in the right Region', 'upload files and configure the feature asked: website, versioning, lifecycle', 'test access: the URL loads if public was asked, or is denied if private'],
        [('Create', 'Unique name, Region.', ''), ('Configure', 'Website, versioning, lifecycle, access.', ''), ('Test', 'URL loads or is denied, as required.', '')],
        'Storage tasks', 'Public only when asked.', 'Storage', 'Animation: create bucket; upload and configure; access test.', 'l3anim')
T3 = lt(3, 'Storage tasks', 'blue',
    '<b>Storage tasks</b> ask you to create object storage and configure a feature — host a static website, enable versioning, add a lifecycle rule, share a file securely with a time-limited link — and are marked by testing the URL, the configuration and whether access is open or closed as required.',
    'A locker room: get a locker with your number, put things inside, and either hand out a time-limited key or put a display window on it.',
    'Example: “Host index.html as a static website and give the URL.”',
    'Tip: buckets are private by default; making one public needs two changes (public-access settings + policy) — do it only when the task says so.', A3,
    'the task names buckets, blobs, static sites, versioning or lifecycle.',
    'Tasks about storing files and sharing or publishing them.',
    [('Name', 'Globally unique.'), ('Upload', 'cp / upload.'), ('Feature', 'Website, versioning, lifecycle.'), ('Access', 'Policy / signed URL.'), ('Test', 'curl URL.')],
    [('static website', 'HTML served directly from storage'), ('pre-signed / SAS / signed URL', 'time-limited link to one object'), ('lifecycle rule', 'automatic tiering or deletion')],
    table(['', 'AWS', 'Azure', 'Google Cloud'], [['Static site', 's3 website + policy', '$web container', 'web-main-page-suffix + allUsers viewer'], ['Temporary link', 'presign', 'SAS token', 'signed URL'], ['Versioning', 'put-bucket-versioning', 'blob versioning', '--versioning']], minw=480),
    'Static-site and secure-sharing tasks are short, quick marks — do them well.',
    'Organisation or account settings can block public access; read the error, and mention it in your answer if you cannot change it.')

A4 = mk(['Address plan', 'Subnets + routes', 'Firewall + test'], ['plan|10.0.0.0/16|no overlap', 'subnets|public/private|route to internet', 'rules|only needed ports|test reachability'], ['violet', 'amber', 'green'],
        ['plan the address range so nothing overlaps', 'create subnets and routes: public subnets route to the internet', 'add firewall rules for only the needed ports and test'],
        [('Plan', 'CIDR ranges without overlap.', ''), ('Build', 'Subnets, routes, gateway.', ''), ('Secure', 'Minimal firewall rules; test.', '')],
        'Network tasks', 'CIDR → subnets → rules.', 'Network', 'Animation: address plan; subnets and routes; firewall and test.', 'l4anim')
T4 = lt(4, 'Network tasks', 'violet',
    '<b>Network tasks</b> ask you to create a virtual network with subnets, routing and firewall rules — e.g. “VPC 10.0.0.0/16 with a public subnet and a private subnet; only HTTP from the internet” — and are marked by inspecting the configuration and testing reachability.',
    'Planning a housing colony: plot numbers (CIDR), lanes (subnets), the main gate (internet gateway) and guards at each house (firewall rules).',
    'Example: “Create VPC lab-vpc with subnet 10.0.1.0/24 and allow only port 80 from anywhere.”',
    'Tip: AWS subnets are zonal, Azure and Google subnets are regional — read which the task expects.', A4,
    'the task names VPC/VNet, subnets, routes, NAT or firewall rules.',
    'Tasks about building a private network with controlled entry points.',
    [('CIDR', 'Plan ranges.'), ('Network', 'VPC/VNet.'), ('Subnets', 'Public/private.'), ('Routes', 'IGW/NAT.'), ('Rules', 'SG/NSG/firewall.')],
    [('CIDR', 'address range notation, e.g. /24 = 256 addresses'), ('internet gateway', 'AWS route to the internet'), ('NSG', 'Azure network security group')],
    table(['', 'AWS', 'Azure', 'Google Cloud'], [['Network', 'VPC (regional)', 'VNet (regional)', 'VPC (global)'], ['Subnet scope', 'one AZ', 'regional', 'regional'], ['Firewall', 'SG + NACL', 'NSG', 'VPC firewall rules']], minw=480),
    'Network tasks reward careful reading more than speed — one wrong CIDR fails the task.',
    'Reserve addresses: AWS keeps 5 per subnet, Azure 5, Google 4 — a /28 has fewer usable addresses than you think.')

A5 = mk(['Choose engine', 'Create small', 'Connect + query'], ['engine|MySQL/Postgres|or NoSQL', 'create|smallest tier|private', 'connect|client|run a query'], ['green', 'amber', 'blue'],
        ['choose the database engine named in the task', 'create it at the smallest tier, not publicly reachable unless asked', 'connect with a client and run a query as proof'],
        [('Engine', 'SQL or NoSQL as named.', ''), ('Create', 'Smallest tier; private.', ''), ('Prove', 'Connect and query.', '')],
        'Database tasks', 'Small, private, proven.', 'Database', 'Animation: choose engine; create small; connect and query.', 'l5anim')
T5 = lt(5, 'Database tasks', 'green',
    '<b>Database tasks</b> ask you to create a managed database (relational or NoSQL), create a table, insert data and query it — testing engine choice, tier selection, network access and connection strings.',
    'Opening a ledger at a bank: pick the account type, open it, write the first entry, read it back.',
    'Example: “Create a DynamoDB table / Cosmos DB container / Firestore collection <i>students</i> and add three items.”',
    'Tip: managed relational databases take 5–15 minutes to create — start them early and do other tasks while waiting.', A5,
    'the task names RDS, Azure SQL, Cloud SQL, DynamoDB, Cosmos DB or Firestore.',
    'Tasks where you create a database and prove data goes in and comes out.',
    [('Engine', 'As named.'), ('Tier', 'Smallest / free.'), ('Access', 'Private or your IP only.'), ('Data', 'Create table, insert.'), ('Query', 'Read back.')],
    [('endpoint', 'database host name'), ('free tier', 'limited free usage'), ('provisioned vs on-demand', 'fixed capacity vs pay per request')],
    table(['', 'AWS', 'Azure', 'Google Cloud'], [['Relational', 'RDS / Aurora', 'Azure SQL / MySQL flexible', 'Cloud SQL'], ['NoSQL quick task', 'DynamoDB', 'Cosmos DB (free tier)', 'Firestore'], ['Create time', 'minutes', 'minutes', 'minutes']], minw=480),
    'NoSQL tasks are faster in a timed exam because there is no server to wait for.',
    'Never open 0.0.0.0/0 to a database port — restrict to your IP and say so in the answer.')

A6 = mk(['Write function', 'Add trigger', 'Invoke + log'], ['code|small handler|runtime', 'trigger|HTTP / upload|schedule', 'prove|invoke|see the log line'], ['amber', 'blue', 'green'],
        ['write a small function in the runtime named', 'connect the trigger: HTTP, file upload or schedule', 'invoke it and show the output and the log line'],
        [('Code', 'Small handler in the named runtime.', ''), ('Trigger', 'HTTP, upload or schedule.', ''), ('Prove', 'Invoke; show output and logs.', '')],
        'Serverless tasks', 'Code + trigger + log.', 'Serverless', 'Animation: write function; add trigger; invoke and log.', 'l6anim')
T6 = lt(6, 'Serverless tasks', 'amber',
    '<b>Serverless tasks</b> ask you to deploy a function and connect it to a trigger — an HTTP endpoint, a storage upload or a schedule — and are marked by invoking it and checking its output and logs.',
    'A doorbell: wire the button (trigger) to the bell (function), press it, and hear it ring (log).',
    'Example: “Deploy a function that returns ‘Hello Lab’ over HTTP and give the URL.”',
    'Tip: use the console’s inline editor for tiny functions in an exam; CLI zip-deploys cost time if you are not practised.', A6,
    'the task names Lambda, Azure Functions, Cloud Run functions or a trigger.',
    'Tasks where code runs automatically when something happens.',
    [('Runtime', 'As named.'), ('Code', 'Minimal handler.'), ('Trigger', 'HTTP/upload/schedule.'), ('Permissions', 'Execution role / identity.'), ('Logs', 'Show the line.')],
    [('handler', 'entry function'), ('execution role', 'identity the function uses'), ('cold start', 'first-invocation delay')],
    table(['', 'AWS', 'Azure', 'Google Cloud'], [['Function', 'Lambda', 'Azure Functions', 'Cloud Run functions'], ['HTTP endpoint', 'function URL / API Gateway', 'HTTP trigger', 'HTTPS trigger'], ['Logs', 'CloudWatch Logs', 'App Insights', 'Cloud Logging']], minw=480),
    'Serverless tasks are popular in newer lab papers because they are cheap and quick to mark.',
    'If the URL returns 403, check auth settings: public invocation must be enabled explicitly on all three.')

A7 = mk(['Alarm / budget', 'Notify', 'Tag + check'], ['set|metric alarm|or budget', 'notify|email / action|group', 'tags|on every resource|query'], ['card', 'amber', 'green'],
        ['create the alarm or budget with the threshold given', 'connect a notification: email, topic or action group', 'tag resources and run a query to show the tags'],
        [('Set', 'Alarm or budget threshold.', ''), ('Notify', 'Email or action group.', ''), ('Tag', 'Tag and query.', '')],
        'Monitoring and cost tasks', 'Threshold + notification + tags.', 'Monitor & cost', 'Animation: alarm or budget; notify; tag and check.', 'l7anim')
T7 = lt(7, 'Monitoring and cost tasks', 'card',
    '<b>Monitoring and cost tasks</b> ask you to set an alarm on a metric (e.g. CPU above 70%), create a budget with an alert, tag resources for cost allocation, or find something in logs — and are marked by inspecting the configuration and sometimes triggering the alarm.',
    'A smoke alarm and a monthly household budget: both only help if someone is notified.',
    'Example: “Create a monthly budget of ₹500 with an email alert at 80%; tag all resources project=lab.”',
    'Tip: budget alerts are evaluated a few times a day — the configuration is what is marked, not an actual email during the exam.', A7,
    'the task names alarms, budgets, logs, tags or labels.',
    'Tasks about watching health and spending.',
    [('Metric', 'Which one?'), ('Threshold', 'Value + period.'), ('Notify', 'Email/topic/action group.'), ('Budget', 'Amount + %.'), ('Tags', 'Apply + query.')],
    [('alarm', 'rule on a metric'), ('budget', 'spending threshold with alerts'), ('tag / label', 'key=value on resources')],
    table(['', 'AWS', 'Azure', 'Google Cloud'], [['Alarm', 'CloudWatch alarm', 'Azure Monitor alert', 'Cloud Monitoring alert policy'], ['Budget', 'AWS Budgets', 'Cost Management budget', 'Billing budget'], ['Tag query', 'Resource Groups Tagging API', 'az resource list --tag', '--filter=labels.x=y']], minw=480),
    'Cost tasks are quick marks and show the examiner you think about money — a theme in every cloud exam.',
    'Mention in your answer that you will delete resources after marking — it shows operational maturity.')

SUMMARY = table(['#', 'Task kind', 'Typical ask', 'How it is checked'], [
    ['1', 'Identity', 'group + read-only', 'allowed and denied actions'], ['2', 'Compute', 'VM serving a page', 'curl public IP'], ['3', 'Storage', 'static site, versioning', 'URL / settings'],
    ['4', 'Network', 'VPC + subnet + rules', 'configuration + reachability'], ['5', 'Database', 'table + 3 items', 'query output'], ['6', 'Serverless', 'HTTP function', 'invoke + logs'], ['7', 'Monitor & cost', 'alarm, budget, tags', 'configuration + tag query']], minw=600)

TYPES = ('  <p>Seven kinds of lab tasks, each in the same pattern: definition, plain words, analogy, internal steps, animation, differences, real-world example, an exam-style task and an expert tip.</p>\n'
         + challenge(['Your VM page times out from outside — what do you check first?', 'Why start the database task early?', 'How do you prove a read-only permission works?'], 'types 2, 5 and 1') + MAP
         + jump(['Identity', 'Compute', 'Storage', 'Network', 'Database', 'Serverless', 'Monitor & cost']) + T1 + T2 + T3 + T4 + T5 + T6 + T7
         + '\n  <h3 style="margin-top:34px">All seven side by side</h3>\n' + SUMMARY)

# ------------------------------------------------------------------ practice tasks
def task(code, title, marks, mins, ask, criteria, hint):
    li = ''.join(f'<li>{c}</li>' for c in criteria)
    return (f'  <details class="faq"><summary><b>{code}</b> · {title} <span style="opacity:.75">({marks} marks · {mins} min)</span></summary>'
            f'<p><b>Task:</b> {ask}</p><p><b>Marking checks:</b></p><ul>{li}</ul><p><b>Hint:</b> {hint}</p></details>\n')

TASKS = ('  <p>Twelve timed tasks in the style of cloud lab exams. Do them in <b>one</b> cloud of your choice. Set a timer for each; mark yourself with the checks; delete everything at the end. Combine any three for a 60-minute mock.</p>\n'
    '  <h3>Set 1 · Foundations</h3>\n'
    + task('T1', 'Read-only group', 4, 8, 'Create group <i>auditors</i> with read-only access and user <i>intern1</i> in it.', ['group exists with read-only policy/role', 'user is a member', 'user can list resources but a delete/create fails'], 'Use the provider’s built-in read-only role; do not write a custom policy.')
    + task('T2', 'Web VM', 10, 15, 'Launch the smallest VM in Mumbai/Central India/asia-south1 that serves “Lab exam: hostname” on port 80. Tag/label it lab=exam.', ['correct size and Region', 'page loads from outside', 'only ports 80 (and 22 if needed) open', 'tag/label present'], 'Startup script + firewall; wait 60–90 s before testing.')
    + task('T3', 'Static website', 6, 10, 'Host an index.html with your name as a static website and submit the URL.', ['URL loads from a browser', 'only the site objects are public', 'Region correct'], 'S3 website + bucket policy / $web container / bucket web config + allUsers viewer.')
    + task('T4', 'Budget and tags', 4, 8, 'Create a monthly budget of ₹500 (or $5) with an 80% alert and list all resources tagged lab=exam.', ['budget amount and threshold correct', 'notification configured', 'tag query output shows your VM'], 'Budgets live at billing/account scope; tag queries use the tagging API or filters.')
    + '  <h3>Set 2 · Core services</h3>\n'
    + task('T5', 'Versioned bucket', 4, 8, 'Create a bucket with versioning; upload notes.txt twice with different content; show both versions.', ['versioning enabled', 'two versions listed', 'bucket private'], 'list-object-versions / blob versions / --all-versions.')
    + task('T6', 'Time-limited share', 4, 6, 'Share one private file with a link that expires in 10 minutes.', ['object still private', 'link works now', 'expiry 10 minutes'], 'presign / SAS / signed URL.')
    + task('T7', 'NoSQL table', 6, 10, 'Create a NoSQL table <i>students</i> (key: roll) and insert three items; query one by key.', ['table/container exists', 'three items', 'query returns the right item'], 'DynamoDB / Cosmos DB / Firestore; on-demand or free tier.')
    + task('T8', 'HTTP function', 6, 12, 'Deploy a function returning “Hello Lab” over HTTP; give the URL and a log line.', ['URL returns the text', 'function logs show the invocation', 'public access only if asked'], 'Console inline editor is fastest under time pressure.')
    + '  <h3>Set 3 · Network and operations</h3>\n'
    + task('T9', 'Custom network', 8, 15, 'Create network lab-vpc 10.20.0.0/16 with subnet 10.20.1.0/24; allow inbound 80 from anywhere and 22 only from your IP.', ['CIDRs exact', 'rules exactly as asked', 'no extra open ports'], 'Find your IP with <code>curl -s ifconfig.me</code>.')
    + task('T10', 'CPU alarm', 4, 8, 'Create an alarm when the VM’s CPU is above 70% for 5 minutes, notifying your email.', ['metric, threshold and period correct', 'notification target set', 'alarm attached to the right VM'], 'CloudWatch alarm + SNS / metric alert + action group / alert policy + channel.')
    + task('T11', 'Stop, resize, start', 4, 8, 'Stop the web VM, change it to the next size up, start it and verify the page still loads.', ['new size shown', 'page loads after start', 'note whether the public IP changed'], 'Public IPs often change after stop/start unless static.')
    + task('T12', 'Clean teardown', 4, 6, 'Delete everything you created and prove nothing tagged lab=exam remains.', ['tag query returns nothing', 'no running VMs', 'buckets/budget removed as instructed'], 'Delete in reverse order of dependencies; Azure: delete the resource group.'))

parts = wwu([
    ('Task sheet', 'The list of tasks and marks.', 'Read fully before starting.', 'Underline names, sizes, Regions.'),
    ('Account / sandbox', 'Where you build.', 'Limits and policies may apply.', 'Lab account, free tier or sandbox.'),
    ('CLI + console', 'Two ways to build.', 'CLI is faster and repeatable.', 'Cloud Shell has CLIs ready.'),
    ('Verification commands', 'curl, describe, list.', 'Prove each result.', 'Same test the examiner uses.'),
    ('Evidence sheet', 'Outputs, IDs, URLs.', 'Protects your marks.', 'Copy as you go.'),
    ('Cleanup plan', 'Reverse-order deletion.', 'No surprise bills.', 'Tags make it easy.')])

DEEP = ('  <h3>First-aid table: symptom → likely cause</h3>\n' + table(['Symptom', 'Likely cause', 'Fix'], [
        ['curl times out', 'port not open, or no public IP', 'add firewall/SG/NSG rule; check public IP'], ['default nginx/Apache page', 'startup script did not write the file', 'check the script path and logs; relaunch'],
        ['AccessDenied / 403 on bucket URL', 'public-access block or missing policy', 'only fix if the task asks for public'], ['function URL 403', 'auth not set to public', 'enable public invocation / anonymous'],
        ['VM create fails: capacity/quota', 'size unavailable or quota', 'try another size/zone in the same Region; state it in the answer'], ['budget command errors', 'wrong scope or date format', 'use account/billing scope; first day of month']], minw=600) +
    '\n  <h3>Where to look for logs during an exam</h3>\n  <ul><li>VM boot scripts: <code>/var/log/cloud-init-output.log</code> (AWS, Azure) or <code>sudo journalctl -u google-startup-scripts</code> (Google Cloud).</li><li>Functions: CloudWatch Logs, Application Insights, Cloud Logging.</li><li>Who changed what: CloudTrail, Activity Log, Audit Logs.</li></ul>\n'
    '  <h3>Time plan for a 60-minute, three-task lab</h3>\n' + table(['Minutes', 'Do'], [['0–5', 'read everything, plan order'], ['5–20', 'start long-running task (VM/DB), then quick tasks while it boots'], ['20–50', 'finish, verify, record evidence'], ['50–60', 're-run every verification; no new work']], minw=380))

clouds = vendor_tabs('<p><b>AWS:</b> Cloud Shell in the console has the CLI ready; Skill Builder labs and AWS Cloud Quest give guided practice; free tier for EC2 (t3.micro/t2.micro), S3, Lambda and DynamoDB within limits.</p>',
    '<p><b>Azure:</b> Cloud Shell (Bash) has <code>az</code>; Microsoft Learn sandboxes give temporary subscriptions for many modules; free account credit and always-free services.</p>',
    '<p><b>Google Cloud:</b> Cloud Shell has <code>gcloud</code>; Skills Boost labs give temporary projects; Free Tier includes e2-micro in some US regions and small Cloud Storage and functions quotas.</p>') + \
    cloud3([['Shell', 'CloudShell', 'Cloud Shell', 'Cloud Shell'], ['Guided labs', 'Skill Builder, Cloud Quest', 'Learn sandbox', 'Skills Boost'], ['Boot log', 'cloud-init-output.log', 'cloud-init-output.log', 'google-startup-scripts journal'], ['Tag query', 'tagging API', 'az resource list --tag', 'labels filter']])

MOCKQ.extend([
 (mock('aws', ['EC2', 'Instances', 'i-0abc…'], ['Details', 'Security', 'Networking'], 'Details', [('Instance type', 't3.micro'), ('Public IPv4', '13.x.x.x'), ('Tags', 'lab = exam')], 'Connect'),
  mock('az', ['Virtual machines', 'vm-lab'], ['Overview', 'Networking', 'Tags'], 'Overview', [('Size', 'Standard B1s'), ('Public IP', '20.x.x.x'), ('Inbound port', '80 allowed')], 'Connect'),
  mock('gcp', ['Compute Engine', 'VM instances', 'vm-lab'], ['Details', 'Observability'], 'Details', [('Machine type', 'e2-micro'), ('External IP', '34.x.x.x'), ('Labels', 'lab : exam')], 'SSH')),
 (mock('aws', ['S3', 'lab-site-…', 'Properties'], ['Objects', 'Properties', 'Permissions'], 'Properties', [('Static website hosting', 'Enabled'), ('Endpoint', 'http://…s3-website.ap-south-1…')], 'Edit'),
  mock('az', ['Storage account', 'Static website'], ['Overview', 'Static website'], 'Static website', [('Static website', 'Enabled'), ('Primary endpoint', 'https://…z29.web.core.windows.net/')], 'Save'),
  mock('gcp', ['Cloud Storage', 'lab-site-…'], ['Objects', 'Permissions', 'Configuration'], 'Permissions', [('allUsers', 'Storage Object Viewer'), ('Public access', 'Public to internet')], 'Grant access')),
 (mock('aws', ['Billing', 'Budgets', 'lab-exam'], ['Overview', 'Alerts'], 'Alerts', [('Budget', '$5.00 monthly'), ('Alert', 'Actual > 80%')], 'Edit'),
  mock('az', ['Cost Management', 'Budgets', 'lab-exam'], ['Overview', 'Alert conditions'], 'Overview', [('Amount', '500 monthly'), ('Scope', 'subscription')], 'Edit budget'),
  mock('gcp', ['Billing', 'Budgets & alerts', 'lab-exam'], ['Scope', 'Amount', 'Actions'], 'Actions', [('Amount', '₹500'), ('Threshold', '80% of actual')], 'Save')),
])

STEP1 = ('1 · Mock Task A: a web VM that the examiner can reach (10 marks)', tri(
    (['[[EC2]] → [[Launch instance]] → Amazon Linux 2023, t3.micro, tag lab=exam; [[Network settings]] → allow HTTP; [[Advanced details]] → User data = the script below → [[Launch]].', 'Open <code>http://PUBLIC_IP</code> in your browser.'],
     "AMI=$(aws ssm get-parameter --name /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 --query Parameter.Value --output text)\nSG=$(aws ec2 create-security-group --group-name lab-web --description \"lab web\" --query GroupId --output text)\naws ec2 authorize-security-group-ingress --group-id $SG --protocol tcp --port 80 --cidr 0.0.0.0/0 >/dev/null\ncat > web.sh <<'EOF'\n#!/bin/bash\ndnf install -y nginx\necho \"Lab exam: $(hostname)\" > /usr/share/nginx/html/index.html\nsystemctl enable --now nginx\nEOF\nID=$(aws ec2 run-instances --image-id $AMI --instance-type t3.micro --security-group-ids $SG --user-data file://web.sh \\\n  --tag-specifications 'ResourceType=instance,Tags=[{Key=lab,Value=exam}]' --query 'Instances[0].InstanceId' --output text)\naws ec2 wait instance-running --instance-ids $ID\nIP=$(aws ec2 describe-instances --instance-ids $ID --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)\nsleep 90; curl -s http://$IP",
     '<code>Lab exam: ip-172-31-…</code> — the page, reached from outside. Save the instance ID, IP and this output as evidence.'),
    (['[[Virtual machines]] → [[Create]] → Ubuntu 24.04, B1s, Central India; [[Inbound ports]] HTTP 80; [[Advanced]] → Custom data = the cloud-init below; tag lab=exam → [[Create]].', 'Open <code>http://PUBLIC_IP</code>.'],
     "az group create -n rg-lab -l centralindia --tags lab=exam >/dev/null\ncat > web.yaml <<'EOF'\n#cloud-config\npackages: [nginx]\nruncmd:\n  - echo \"Lab exam: $(hostname)\" > /var/www/html/index.html\nEOF\naz vm create -g rg-lab -n vm-lab --image Ubuntu2404 --size Standard_B1s --admin-username azureuser \\\n  --generate-ssh-keys --custom-data web.yaml --tags lab=exam --query publicIpAddress -o tsv\naz vm open-port -g rg-lab -n vm-lab --port 80 >/dev/null\nIP=$(az vm show -d -g rg-lab -n vm-lab --query publicIps -o tsv)\nsleep 90; curl -s http://$IP",
     '<code>Lab exam: vm-lab</code>. If B1s is unavailable, pick another small size in the same Region and note it in your answer.'),
    (['[[Compute Engine]] → [[Create instance]] → e2-micro, asia-south1-a, Debian 12; [[Firewall]] allow HTTP; [[Advanced]] → Automation → Startup script; label lab=exam → [[Create]].', 'Open <code>http://EXTERNAL_IP</code>.'],
     "gcloud compute instances create vm-lab --zone=asia-south1-a --machine-type=e2-micro \\\n  --image-family=debian-12 --image-project=debian-cloud --tags=http-server --labels=lab=exam \\\n  --metadata=startup-script='#! /bin/bash\napt-get update && apt-get install -y nginx\necho \"Lab exam: $(hostname)\" > /var/www/html/index.html'\ngcloud compute firewall-rules create allow-http-lab --allow=tcp:80 --target-tags=http-server\nIP=$(gcloud compute instances describe vm-lab --zone=asia-south1-a --format='get(networkInterfaces[0].accessConfigs[0].natIP)')\nsleep 90; curl -s http://$IP",
     '<code>Lab exam: vm-lab</code>. Timeout → check the firewall rule and network tag; default page → check the startup-script journal.')),
    'This is the “verify from outside” habit from the story. Do not move on until curl shows your text.')

STEP2 = ('2 · Mock Task B: a static website (6 marks)', tri(
    (['[[S3]] → [[Create bucket]] (Mumbai) → upload index.html → [[Properties]] → Static website hosting → Enable; [[Permissions]] → turn off Block Public Access for this bucket and add a GetObject policy.', 'Open the website endpoint shown under Properties.'],
     "B=lab-site-$RANDOM; aws s3 mb s3://$B --region ap-south-1\necho '<h1>Lab exam site</h1>' > index.html\naws s3 cp index.html s3://$B/\naws s3 website s3://$B --index-document index.html\naws s3api delete-public-access-block --bucket $B\naws s3api put-bucket-policy --bucket $B --policy \"{\\\"Version\\\":\\\"2012-10-17\\\",\\\"Statement\\\":[{\\\"Effect\\\":\\\"Allow\\\",\\\"Principal\\\":\\\"*\\\",\\\"Action\\\":\\\"s3:GetObject\\\",\\\"Resource\\\":\\\"arn:aws:s3:::$B/*\\\"}]}\"\ncurl -s http://$B.s3-website.ap-south-1.amazonaws.com",
     'your <code>&lt;h1&gt;Lab exam site&lt;/h1&gt;</code>. If the policy call fails with AccessDenied, account-level Block Public Access is on — say so in your answer.'),
    (['Storage account → [[Static website]] → Enabled, index document index.html → upload index.html to the <code>$web</code> container.', 'Open the Primary endpoint.'],
     "SA=labsite$RANDOM; az storage account create -n $SA -g rg-lab -l centralindia --sku Standard_LRS --kind StorageV2 --tags lab=exam >/dev/null\necho '<h1>Lab exam site</h1>' > index.html\naz storage blob service-properties update --account-name $SA --static-website --index-document index.html >/dev/null\naz storage blob upload --account-name $SA -c '$web' -f index.html -n index.html >/dev/null\nURL=$(az storage account show -n $SA -g rg-lab --query primaryEndpoints.web -o tsv); echo $URL; curl -s $URL",
     'the URL (<code>https://labsite….z29.web.core.windows.net/</code>) and your heading. The CLI may warn that it used the account key — fine for a lab.'),
    (['[[Cloud Storage]] → [[Create]] bucket in asia-south1 → upload index.html → [[Permissions]] → [[Grant access]] → allUsers = Storage Object Viewer; bucket menu → Edit website configuration → index.html.', 'Open the object’s public URL.'],
     "B=lab-site-$RANDOM; gcloud storage buckets create gs://$B --location=asia-south1 --uniform-bucket-level-access --quiet\necho '<h1>Lab exam site</h1>' > index.html\ngcloud storage cp index.html gs://$B\ngcloud storage buckets update gs://$B --web-main-page-suffix=index.html\ngcloud storage buckets add-iam-policy-binding gs://$B --member=allUsers --role=roles/storage.objectViewer >/dev/null\ncurl -s https://storage.googleapis.com/$B/index.html",
     'your heading. If the binding is refused, an organisation policy blocks public access — note it in your answer.')),
    'Public access is correct here only because the task asked for a public website.')

STEP3 = ('3 · Mock Task C: budget guard-rail and a final self-check (4 marks)', tri(
    (['[[Billing]] → [[Budgets]] → [[Create budget]] → Cost budget, $5 monthly, alert at 80% actual to your email.', '[[Resource Groups &amp; Tag Editor]] → Tag Editor → search tag lab=exam.'],
     "ACC=$(aws sts get-caller-identity --query Account --output text)\naws budgets create-budget --account-id $ACC \\\n  --budget '{\"BudgetName\":\"lab-exam\",\"BudgetLimit\":{\"Amount\":\"5\",\"Unit\":\"USD\"},\"TimeUnit\":\"MONTHLY\",\"BudgetType\":\"COST\"}' \\\n  --notifications-with-subscribers '[{\"Notification\":{\"NotificationType\":\"ACTUAL\",\"ComparisonOperator\":\"GREATER_THAN\",\"Threshold\":80,\"ThresholdType\":\"PERCENTAGE\"},\"Subscribers\":[{\"SubscriptionType\":\"EMAIL\",\"Address\":\"you@example.com\"}]}]'\naws budgets describe-budget --account-id $ACC --budget-name lab-exam --query 'Budget.[BudgetName,BudgetLimit.Amount,TimeUnit]' --output text\naws resourcegroupstaggingapi get-resources --tag-filters Key=lab,Values=exam --query 'ResourceTagMappingList[].ResourceARN' --output text",
     '<code>lab-exam 5.0 MONTHLY</code> and the ARN of your tagged instance — configuration and tagging proven. Replace the email with yours.'),
    (['[[Cost Management]] → [[Budgets]] → [[Add]] → 500 monthly; alert condition 80% actual to your email.', '[[All resources]] → filter tag lab=exam.'],
     "az consumption budget create --budget-name lab-exam --amount 500 --category cost --time-grain monthly \\\n  --start-date $(date +%Y-%m-01) --end-date $(date -d '+1 year' +%Y-%m-01) >/dev/null\naz consumption budget show --budget-name lab-exam --query \"{name:name,amount:amount,grain:timeGrain}\"\naz resource list --tag lab=exam --query \"[].{name:name,type:type}\" -o table",
     'the budget (amount 500, Monthly) and a table with vm-lab, its disk, NIC, public IP, NSG and the storage account. Add the 80% email alert in the portal — the CLI command does not set notifications.'),
    (['[[Billing]] → [[Budgets &amp; alerts]] → [[Create budget]] → this project, ₹500, threshold 80% actual, email billing admins.', '[[Compute Engine]] → filter label lab:exam.'],
     "BA=$(gcloud billing projects describe $(gcloud config get-value project) --format='value(billingAccountName)' | cut -d/ -f2)\ngcloud billing budgets create --billing-account=$BA --display-name=lab-exam \\\n  --budget-amount=500INR --threshold-rule=percent=0.8\ngcloud billing budgets list --billing-account=$BA --format='table(displayName,amount.specifiedAmount.units)'\ngcloud compute instances list --filter='labels.lab=exam' --format='table(name,zone,status)'",
     'the budget row <code>lab-exam 500</code> and your vm-lab RUNNING. The budget currency must match the billing account’s currency.')),
    'Final self-check: re-run the curl commands from Tasks A and B — both must still work before you “submit”.')

prac = practical(OWN_INTRO + ' A full 30-minute mock lab with three marked tasks. Set a timer, do it in one cloud, and keep an evidence file (copy every output into <code>evidence.txt</code>). Costs: a few rupees if deleted the same day; free-tier VMs may be free.', [SETUP_STEP, STEP1, STEP2, STEP3],
    cleanup="<b>AWS:</b> <code>aws ec2 terminate-instances --instance-ids $ID; aws ec2 wait instance-terminated --instance-ids $ID; aws ec2 delete-security-group --group-id $SG; aws s3 rb s3://$B --force; aws budgets delete-budget --account-id $ACC --budget-name lab-exam</code>. <b>Azure:</b> <code>az group delete -n rg-lab --yes --no-wait; az consumption budget delete --budget-name lab-exam</code>. <b>Google Cloud:</b> <code>gcloud compute instances delete vm-lab --zone=asia-south1-a --quiet; gcloud compute firewall-rules delete allow-http-lab --quiet; gcloud storage rm -r gs://$B; gcloud billing budgets list --billing-account=$BA</code> then delete the budget by its ID with <code>gcloud billing budgets delete</code>.")

mist = mistakes([
    ['Not verifying from outside.', 'Assuming “created” means “working”.', 'curl after every task.'],
    ['Opening every port “to be safe”.', 'Panic.', 'Only the ports the task names; extra rules can lose marks.'],
    ['Debugging a broken VM by hand for 20 minutes.', 'Sunk cost.', 'Fix the script, terminate, relaunch.'],
    ['Wrong Region or name.', 'Not underlining values.', 'Copy names from the task sheet; check the Region selector.'],
    ['Deleting before marking.', 'Tidiness habit.', 'Clean up only when told.'],
    ['No evidence.', 'Rushing.', 'Paste outputs into evidence.txt as you go.']])

cert = table(['Exam / syllabus', 'How to use this lesson'], [['C-DAC PGCP-BDA', 'Lab exam practice: VM, storage, serverless, monitoring tasks under time.'], ['AWS CLF-C02', 'Hands-on understanding behind service questions (no lab in the exam).'], ['AZ-900 / Cloud Digital Leader', 'Concrete experience makes scenario questions easier.'], ['Associate exams (SAA, AZ-104, ACE)', 'AZ-104 and Associate Cloud Engineer test exactly these skills; some exams include labs.']], minw=560)

proj = miniproject('Mini project: your personal lab-exam kit',
    'Build reusable, tested snippets for the twelve tasks.',
    ['<b>Scripts:</b> one file per task (T1–T12) with the CLI commands for your chosen cloud.',
     '<b>Verification:</b> each file ends with the command that proves the result.',
     '<b>Timing:</b> run each against a timer; record your time.',
     '<b>Mock:</b> pick three random tasks and do them in 60 minutes.',
     '<b>Teardown:</b> a single cleanup script based on tags/resource group.',
     '<b>Second cloud:</b> port three tasks to a second provider.'],
    'A folder of 12 tested scripts with times, and a passed 60-minute mock.', 'Modules 4–8, 11.1.')

assemble_v2(HERE, story_h2='Everything built, a third of the marks lost', hook_html=hk,
    narration='Arjun’s lab exam had three tasks. He built all of them, but the web page timed out when the examiner tried it — port 80 had never been opened. He lost the biggest task’s marks.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Lab exam practice tasks',
    formal='A <b>cloud lab exam</b> is a time-limited practical assessment in which candidates build and configure resources — identities, compute, storage, networks, databases, functions, monitoring and budgets — in a cloud account to meet written requirements, and are marked on verifiable outcomes such as configuration, reachability, security and absence of unnecessary resources.',
    simple='You are given tasks and a cloud account; you build what each task asks and the examiner checks that it works.',
    interview=['“In lab tasks I plan first, build the minimum, then verify from outside exactly as the user would — and I keep the commands so the work is repeatable.”', '“If a VM build fails I fix the startup script and relaunch rather than debugging by hand — infrastructure should be reproducible.”'],
    terms_rows=[('Task sheet', 'List of tasks and marks.'), ('Verification', 'A test proving the result.'), ('Evidence', 'Output kept as proof.'), ('Startup script', 'Commands run at first boot.'), ('Cloud Shell', 'Browser shell with CLIs.'), ('Sandbox', 'Temporary practice account.'), ('Tag / label', 'key=value on resources.'), ('Teardown', 'Deleting everything you created.')],
    exam='The C-DAC PGCP-BDA cloud module has a lab component; associate-level exams (AZ-104, Associate Cloud Engineer) test the same hands-on skills.',
    picture_h2='One routine for every lab task', picture_html=picture,
    after_picture=[('types', 'Types, one by one', 'Seven kinds of lab tasks, one by one', TYPES)],
    how_h2='Running a lab exam, step by step', how_intro='The routine applied to a three-task lab.', how_anim=SOLVE,
    parts_h2='Six parts of a lab exam', parts_html=parts, lv='',
    myth_rows=[('Created means done.', 'Working from outside means done.', 'Story.'), ('More resources = more marks.', 'Extra resources can cost marks and money.', 'Type 2.'), ('Console is always faster.', 'CLI is faster once practised, and repeatable.', 'Parts.')],
    extra_secs=[('tasks', 'Practice tasks', 'Twelve timed lab tasks with marking checks', TASKS), ('deep', 'Deep dive', 'First-aid table, logs, time plan', DEEP)],
    clouds_html=clouds, practical_html=prac, mistakes_html=mist, cert_html=cert, project_html=proj,
    can_now=['Recognise seven kinds of lab tasks.', 'Apply plan–build–verify–evidence–clean up.', 'Complete a three-task mock lab on your own account.', 'Diagnose the common failures quickly.', 'Practise twelve timed tasks with marking checks.'],
    next_html='<a href="../04-cloud-interview-questions/">11.4 Cloud interview questions</a>.',
    pre='<b>Before you start:</b> Modules 4–8 and Lesson 11.1.')
