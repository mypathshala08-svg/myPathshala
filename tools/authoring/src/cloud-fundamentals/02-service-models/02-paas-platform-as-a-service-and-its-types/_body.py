import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
def cap(frames, steps, title, intro, panel, aria, hid, delay=5500):
    return anim_one('Animated', title, intro, panel, aria, cap_frames(frames, steps), [s[0] + '.' for s in steps], delay=delay, hid=hid)


hk = hook('TiffinGo’s developer spent three days setting up a server — OS, Python, Nginx, SSL certificate, firewall, monitoring — before writing a single line of the new feedback app. Could those three days have been three minutes?',
    'Yes, with <b>Platform as a Service (PaaS)</b>: you bring the code, the platform brings the operating system, runtime, web server, load balancer, HTTPS, scaling and patching. PaaS is not one product but a family — app platforms, container platforms, managed databases (DBaaS), integration platforms (iPaaS), mobile back ends, data and AI platforms, and private PaaS you run yourself. This lesson explains each type, shows what happens between <code>git push</code> and a live URL, and you deploy a web app, read its logs and create a managed database on <b>your own</b> AWS, Azure or Google Cloud account.',
    ['Seven kinds of PaaS — and which one you are already using without knowing.', 'What a platform does in the 60 seconds after you push code.', 'Where PaaS stops: the shared responsibility line.'])

def story_scene():
    o = t(180, 12, 'Three days vs three minutes', 9, 'ink', bold=True)
    o += box(14, 26, 150, 84, 'red', rx=8) + t(89, 44, 'IaaS: you set up', 8, 'ink', bold=True)
    for i, n in enumerate(['OS + patches', 'Python + Nginx', 'SSL + firewall', 'scaling + logs']): o += t(89, 60 + i * 12, n, 6.8, 'ink')
    o += box(196, 26, 150, 84, 'green', rx=8) + t(271, 44, 'PaaS: you push', 8, 'ink', bold=True) + t(271, 66, 'git push / az webapp up', 6.8, 'ink', mono=True) + t(271, 86, '→ https://… live', 7.4, 'ink', bold=True)
    o += t(180, 128, 'Same app. The platform does the undifferentiated work.', 7.6, 'ink', bold=True)
    return o
scene_svg = scene('Left: IaaS where you set up OS, runtime, SSL, scaling and logs; right: PaaS where one push gives a live HTTPS URL.', story_scene(), 'Spend time on the <tspan font-weight="700" class="s-acc">app</tspan>, not the server.', h=144)
dialogue = '''R> Sir, Arjun took three days to set up the feedback server. Is that normal?
A> On IaaS, yes — he owns the OS, the runtime, the web server, certificates, patching. On PaaS he would push the code and get a URL.
K> But then we lose control?
A> Some. You cannot SSH into App Engine standard or install a random kernel module. In return you never patch an OS again.
R> And the database?
A> That is also PaaS — a managed database. So is Firebase for mobile, and Logic Apps for connecting apps. Let’s see the whole family.'''

# ------------------------------------------------------------------ picture
def stackfig():
    o = t(320, 16, 'Who manages what: on-premises vs IaaS vs PaaS vs SaaS', 11, 'ink', bold=True)
    layers = ['Data', 'Application', 'Runtime', 'Middleware', 'Operating system', 'Virtualization', 'Servers', 'Storage', 'Networking']
    models = ['On-premises', 'IaaS', 'PaaS', 'SaaS']
    you = [9, 5, 2, 0]
    for j, m in enumerate(models):
        x = 150 + j * 120
        o += t(x + 52, 36, m, 8.4, 'ink', bold=True)
        for i, l in enumerate(layers):
            mine = i < you[j]
            o += box(x, 44 + i * 21, 104, 18, 'blue' if mine else 'green', rx=3) + t(x + 52, 57 + i * 21, l, 6.6, 'ink')
    for i, l in enumerate(layers): pass
    o += box(150, 240, 14, 10, 'blue', rx=2) + t(168, 249, 'you manage', 7.2, 'ink', anchor='start') + box(260, 240, 14, 10, 'green', rx=2) + t(278, 249, 'provider manages', 7.2, 'ink', anchor='start')
    o += t(80, 140, 'In PaaS you', 7.6, 'ink', bold=True) + t(80, 154, 'keep only', 7.6, 'ink', bold=True) + t(80, 168, 'app + data', 7.6, 'ink', bold=True)
    return o
STACK = bigfig('Four stacks of nine layers — data, application, runtime, middleware, operating system, virtualization, servers, storage, networking. On-premises: you manage all. IaaS: you manage data to operating system. PaaS: you manage only data and application. SaaS: provider manages all.', stackfig(), h=262)

def famfig():
    o = t(320, 16, 'The PaaS family: seven kinds of platform', 11, 'ink', bold=True)
    o += box(250, 104, 140, 50, 'green', rx=25) + t(320, 126, 'PaaS', 11, 'ink', bold=True) + t(320, 142, 'you bring code / data', 7, 'ink2')
    items = [('App platform', 'App Service · Beanstalk · App Engine', 40, 40), ('Container platform', 'Cloud Run · Container Apps', 250, 30), ('Database (DBaaS)', 'RDS · Azure SQL · Cloud SQL', 460, 40),
             ('Integration (iPaaS)', 'Logic Apps · AppFlow · App Integration', 470, 170), ('Mobile back end', 'Firebase · Amplify', 40, 170), ('Data & AI platform', 'BigQuery · Fabric · Vertex AI', 250, 200), ('Private PaaS', 'OpenShift · Cloud Foundry', 40, 105)]
    for n, d, x, y in items:
        o += box(x, y, 150 if x != 40 or y != 105 else 150, 46, 'card', rx=8) + t(x + 75, y + 19, n, 7.8, 'ink', bold=True) + t(x + 75, y + 35, d, 6.2, 'ink2')
    return o
FAM = bigfig('A central PaaS circle surrounded by seven kinds: app platform, container platform, database as a service, integration platform, mobile back end, data and AI platform, private PaaS.', famfig(), h=256)

picture = ('  <p>PaaS moves the line of responsibility up the stack — you keep only your application and data:</p>\n' + STACK + '\n  <p>And “PaaS” is a family of platforms, not one product:</p>\n' + FAM)

# ------------------------------------------------------------------ how: push to production
RN = {'dev': (4, 54, 54, 50, 'laptop', 'Developer', 'git push'), 'up': (66, 4, 60, 46, 'cloud', 'Upload', 'source zip'), 'build': (66, 104, 60, 46, 'gear', 'Build', 'buildpack'),
      'img': (138, 54, 62, 50, 'disk', 'Artifact', 'image/package'), 'run': (212, 4, 64, 46, 'server', 'Instances', 'managed VMs'), 'lb': (212, 104, 64, 46, 'lb', 'Front end', 'LB + TLS'), 'live': (290, 54, 66, 50, 'globe', 'Live URL', 'https://…')}
RS = [dict(on=['dev', 'up'], hot='up', move=(58, 70, 70, 40, 'push'), head='Step 1 · You hand over source code', text='az webapp up / gcloud app deploy / an EB bundle or a git push sends your code', text2='(plus requirements.txt) to the platform. No OS, no server chosen.', svc='The only thing you provide: code + config'),
      dict(on=['dev', 'up', 'build'], hot='build', move=(96, 50, 96, 104, 'detect'), head='Step 2 · The platform builds it', text='A buildpack detects Python, installs dependencies and creates a runnable', text2='package or container image — reproducible every time.', svc='Oryx (App Service) · Google buildpacks · EB platform hooks'),
      dict(on=['dev', 'up', 'build', 'img'], hot='img', move=(126, 127, 150, 90, 'store'), head='Step 3 · A versioned artifact', text='Each deployment becomes a version you can roll back to (App Engine versions,', text2='EB application versions, App Service deployment history/slots).', svc='Rollback = switch to the previous version'),
      dict(on=['dev', 'up', 'build', 'img', 'run'], hot='run', move=(200, 70, 222, 40, 'start'), head='Step 4 · Instances start on managed infrastructure', text='The platform starts instances on patched OS images in its (or your) account,', text2='with health checks and auto scaling rules.', svc='You set instance size/count or scaling rules — not the OS'),
      dict(on=list(RN), hot='live', move=(276, 127, 298, 90, 'serve'), head='Step 5 · Load balancer, HTTPS, logs — done', text='A managed front end gives an HTTPS URL; logs and metrics are wired up; the', text2='provider keeps patching the OS and runtime underneath.', svc='https://APP.azurewebsites.net · APP.appspot.com · *.elasticbeanstalk.com')]
PUSH = flow_anim('From code to a live URL on PaaS', 'What the platform does after you push.', 'PaaS deployment', 'Animation: developer pushes code; platform builds it with a buildpack; versioned artifact; managed instances start; load balancer with HTTPS gives a live URL.', RN, RS, hid='paasflow')

# ------------------------------------------------------------------ types
def mapfig():
    o = t(320, 16, 'Seven types of PaaS', 11, 'ink', bold=True)
    items = [('1', 'Application PaaS', 'run web apps from code', 'green'), ('2', 'Container PaaS', 'run any container, no cluster', 'blue'), ('3', 'Database PaaS', 'managed databases', 'violet'),
             ('4', 'Integration PaaS', 'connect apps and data', 'amber'), ('5', 'Mobile back end', 'auth, data, push for apps', 'green'), ('6', 'Data & AI PaaS', 'analytics and ML platforms', 'violet'), ('7', 'Private / hybrid PaaS', 'your own platform', 'red')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 12 + (i % 4) * 156; y = 32 + (i // 4) * 84
        o += box(x, y, 148, 70, tn, rx=8) + pin(x + 16, y + 16, n) + t(x + 80, y + 34, a, 7.8, 'ink', bold=True) + t(x + 78, y + 54, b, 6.8, 'ink2')
    o += t(320, 210, '1–2 run your code · 3–6 run your data and integrations · 7 is PaaS you operate yourself.', 7.6, 'ink2')
    return o
MAP = bigfig('Map of seven PaaS types: application PaaS, container PaaS, database PaaS, integration PaaS, mobile back end, data and AI PaaS, private or hybrid PaaS.', mapfig(), h=222)

def row3(k, items, tones, cap_):
    o = ''
    for i, l in enumerate(items):
        on = i <= k
        o += box(20 + i * 112, 34, 100, 74, tones[i] if on else 'card', rx=8)
        for j, w in enumerate(l.split('|')): o += t(70 + i * 112, 60 + j * 14, w, 7.2 if j == 0 else 6.6, 'ink', bold=(j == 0))
        if i < 2: o += arrow(120 + i * 112, 71, 132 + i * 112, 71)
    return o + t(180, 132, cap_, 7.2, 'ink', bold=True)

def mk(title3, items, tones, caps, steps, ttl, intro, panel, aria, hid):
    frames = [t(180, 12, title3[k], 9, 'ink', bold=True) + row3(k, items, tones, caps[k]) for k in range(3)]
    return cap(frames, steps, ttl, intro, panel, aria, hid)

A_APP = mk(['Push code', 'Platform runs it', 'Scale and release'], ['code|Python/Java/.NET|Node/PHP', 'runtime|web server, TLS|patched OS', 'slots/versions|autoscale|rollback'], ['amber', 'green', 'blue'],
           ['you provide code and a config file', 'the platform owns the stack below your app', 'blue-green releases and scaling are settings'],
           [('Push', 'You deploy source code for a supported language.', ''), ('Run', 'The platform supplies runtime, web server, HTTPS and patching.', ''), ('Operate', 'Scale, version and roll back with settings.', '')],
           'Application PaaS in action', 'Code in, web app out.', 'App PaaS', 'Animation: code pushed; platform runtime runs it; versions and scaling handled.', 'p1anim')
T1 = vtype(1, 'Application PaaS (aPaaS)', 'green',
    '<b>Application PaaS (aPaaS)</b> runs web applications and APIs directly from source code in supported languages, with the provider managing the operating system, language runtime, web server, load balancing, TLS, scaling and patching; the customer manages the code, configuration and data.',
    'A furnished paying-guest room with meals: you bring your clothes (code) and live there; the owner handles the building, cooking and repairs.',
    'TiffinGo’s customer-feedback app (Flask) runs on Azure App Service: <code>az webapp up</code> created it in two minutes on the free F1 tier; later it moves to a Standard plan with a staging slot.',
    'Azure App Service, AWS Elastic Beanstalk, Google App Engine (standard/flexible); Heroku, Render and similar.',
    '', A_APP,
    'standard web apps and APIs in mainstream languages, where speed of delivery matters more than OS control.',
    'you need custom OS packages, special networking or long-lived background processes the platform does not support.',
    plain='You upload your website’s code; the cloud runs it for you, with everything underneath handled.',
    how=[('Pick runtime', 'e.g. Python 3.12.'), ('Deploy', 'Source zip, git, or pipeline.'), ('Build', 'Buildpack installs dependencies.'), ('Run', 'Instances behind a managed LB with HTTPS.'), ('Operate', 'Scaling rules, slots/versions, logs.')],
    words=[('runtime', 'the language engine, e.g. Python 3.12'), ('buildpack', 'a script that turns source code into a runnable app'), ('deployment slot', 'a second live copy for testing before swapping')],
    diff=table(['', 'aPaaS', 'IaaS VM'], [['You manage', 'code, config, data', 'OS, runtime, web server, code, data'], ['Time to first deploy', 'minutes', 'hours–days'], ['SSH/OS changes', 'limited or none', 'full']], minw=440),
    where=['Company websites and portals', 'REST APIs for mobile apps', 'Student and start-up projects'],
    realworld='Google App Engine (2008) was one of the first public PaaS offerings; Heroku popularised “git push to deploy” — and its 2022 removal of free plans pushed many students to Azure App Service F1, Render and similar free tiers.',
    pro='Elastic Beanstalk is the transparent kind of PaaS: it creates EC2, an Auto Scaling group and a load balancer <i>in your account</i>, so you still see — and pay for — every resource; App Engine standard and App Service hide them.')

A_CON = mk(['Bring any container', 'Platform runs it', 'Scale to zero'], ['image|any language|any library', 'service|HTTPS URL|revisions', 'autoscale|0 → N|per request'], ['blue', 'green', 'amber'],
           ['if it runs in a container, it runs here', 'no cluster, no nodes to manage', 'pay only while handling requests (Cloud Run, Container Apps)'],
           [('Image', 'Bring a container image with any language or OS libraries.', ''), ('Service', 'The platform runs it behind HTTPS with revisions.', ''), ('Scale', 'Autoscale by requests, down to zero.', '')],
           'Container PaaS in action', 'Containers without Kubernetes chores.', 'Container PaaS', 'Animation: any container image; platform runs it with an HTTPS URL; scales from zero to many.', 'p2anim')
T2 = vtype(2, 'Container-based PaaS', 'blue',
    '<b>Container-based PaaS</b> runs containerised applications without the customer operating a cluster: you supply a container image (or source the platform builds into one), and the platform provides scaling, revisions, HTTPS endpoints and managed infrastructure — combining PaaS simplicity with container flexibility.',
    'A food-truck park with power and water: bring any truck (container) with any kitchen inside; the park provides space, electricity and customers.',
    'TiffinGo’s route-optimisation API needs a geospatial C library that App Service does not have; it runs as a container on Cloud Run with <code>gcloud run deploy --source .</code> and scales to zero at night.',
    'Google Cloud Run, Azure Container Apps, AWS (ECS Express Mode / Fargate; App Runner closed to new customers in 2026); Red Hat OpenShift, Heroku container stack.',
    'Serverless containers are compared with other compute in Lesson 6.1.', A_CON,
    'you need custom dependencies or languages but still want “no servers”.',
    'you need deep Kubernetes features (operators, custom networking) — use managed Kubernetes.',
    plain='Like app PaaS, but you can bring any packed app (a container), so any language or library works.',
    how=[('Package', 'Dockerfile or buildpacks → image.'), ('Deploy', 'Service with CPU, memory, port, env vars.'), ('Revisions', 'Each deploy is a revision; split traffic between them.'), ('Scale', 'Requests/concurrency drive instances, often to zero.'), ('Integrate', 'Secrets, VPC access, custom domains.')],
    words=[('container image', 'a packaged app with its libraries'), ('revision', 'one deployed version of a service'), ('traffic splitting', 'sending a share of users to a new version')],
    diff=table(['', 'Container PaaS', 'Application PaaS'], [['Input', 'container image (or source)', 'source code'], ['Languages/libraries', 'anything', 'supported runtimes'], ['Portability', 'high (OCI images)', 'medium']], minw=440),
    where=['APIs with special dependencies', 'Microservices without Kubernetes', 'Background jobs (Cloud Run jobs, Container Apps jobs)'],
    realworld='Cloud Run is built on Knative-compatible APIs, so the same service definition can also run on Kubernetes with Knative — a deliberate portability choice by Google.',
    pro='Azure Container Apps runs on Kubernetes underneath and integrates <b>Dapr</b> and KEDA, so you get event-driven scaling (e.g. on Service Bus queue length) without touching Kubernetes yourself.')

A_DB = mk(['Choose engine + size', 'Provider operates it', 'You use SQL'], ['engine|PostgreSQL / MySQL|SQL Server', 'ops|backups, patches|HA, failover', 'app|connection string|tables + data'], ['violet', 'green', 'blue'],
          ['minutes to a production-grade database', 'no OS, no install, automatic backups and failover', 'you still own schema, queries, indexes and data'],
          [('Create', 'Pick an engine, version and size.', ''), ('Operate', 'The provider patches, backs up and fails over.', ''), ('Use', 'You manage schema, queries, access and data.', '')],
          'Database PaaS in action', 'A database without a DBA’s night shifts.', 'DBaaS', 'Animation: choose engine and size; provider handles backups, patching and failover; you use SQL.', 'p3anim')
T3 = vtype(3, 'Database PaaS (DBaaS)', 'violet',
    '<b>Database as a Service (DBaaS)</b> provides managed database engines — relational and NoSQL — where the provider handles provisioning, OS and engine patching, backups and point-in-time restore, replication and failover, and monitoring, while the customer manages schemas, queries, indexes, access and data.',
    'A bank locker: the bank guards the vault, cameras and backups; you decide what to keep inside and who gets a key.',
    'TiffinGo’s orders database is Amazon RDS for PostgreSQL with Multi-AZ; the team never installs PostgreSQL or patches Linux, but still tunes slow queries and adds indexes.',
    'Amazon RDS, Aurora, DynamoDB; Azure SQL Database, Azure Database for PostgreSQL/MySQL flexible server, Cosmos DB; Google Cloud SQL, AlloyDB, Spanner, Firestore.',
    'Database types are compared in Lesson 6.4.', A_DB,
    'almost always — unless you need an engine version, extension or OS-level access the service does not allow.',
    'you assume the provider tunes your queries or protects you from your own DELETE — that is still your job.',
    plain='A database the cloud company installs, backs up, updates and keeps running for you. You just create tables and store data.',
    how=[('Provision', 'Engine, version, size, storage, network.'), ('Secure', 'Private networking, IAM/SQL users, encryption.'), ('Protect', 'Automated backups, point-in-time restore, Multi-AZ/HA.'), ('Maintain', 'Patching in maintenance windows.'), ('Scale', 'Bigger instance, read replicas, serverless capacity.')],
    words=[('DBaaS', 'database as a service'), ('point-in-time restore', 'restore to any second within the backup window'), ('read replica', 'a read-only copy to share load'), ('maintenance window', 'the time slot for patches')],
    diff=table(['Task', 'Self-managed DB on a VM', 'DBaaS'], [['Install/patch engine and OS', 'you', 'provider'], ['Backups and HA', 'you build them', 'settings'], ['Schema, indexes, queries', 'you', 'you'], ['Superuser/OS access', 'yes', 'restricted']], minw=480),
    where=['Application databases', 'Reporting replicas', 'Start-ups without a DBA'],
    realworld='Azure SQL Database offers a free tier of a serverless database (a monthly allowance of vCore-seconds and storage per subscription) — handy for students learning SQL without a VM.',
    pro='DBaaS often hides the superuser: on RDS you get <code>rds_superuser</code>, not real <code>postgres</code> superuser, so some extensions and file-system functions are not available — check before migrating a database that depends on them.')

A_INT = mk(['Trigger in one app', 'Workflow transforms', 'Action in another app'], ['trigger|new order in|Shopify/Gmail', 'workflow|map fields|conditions', 'action|row in sheet|Slack/SAP'], ['amber', 'violet', 'green'],
           ['an event in a SaaS app or system starts the flow', 'drag-and-drop steps with 100s of connectors', 'results land in other apps — little or no code'],
           [('Trigger', 'An event in one system (new email, new order) starts the workflow.', ''), ('Transform', 'Steps map, filter and enrich data using connectors.', ''), ('Act', 'Data is written to other systems — CRM, ERP, chat, sheets.', '')],
           'Integration PaaS in action', 'Connect apps without writing glue servers.', 'iPaaS', 'Animation: a trigger in one app; a workflow transforms data; an action in another app.', 'p4anim')
T4 = vtype(4, 'Integration PaaS (iPaaS)', 'amber',
    '<b>Integration Platform as a Service (iPaaS)</b> is a cloud service for building and running integration flows between applications, data sources and APIs — on-premises and SaaS — using prebuilt connectors, visual workflow designers, data mapping and managed execution.',
    'A professional courier and translator in one: picks up a parcel from one office, repacks and labels it the way the next office wants, and delivers it.',
    'Every new corporate lunch order from TiffinGo’s Shopify store creates a row in Google Sheets for the kitchen and a message in the team’s Teams channel — an Azure Logic Apps workflow built in an afternoon.',
    'Azure Logic Apps, Power Automate; Amazon AppFlow, EventBridge Pipes, Step Functions; Google Application Integration, Workflows; MuleSoft, Boomi, Zapier (SaaS).',
    '', A_INT,
    'you must connect several SaaS and internal systems quickly and maintainably.',
    'flows become your core business logic with complex rules — then code (functions/services) is easier to test and version.',
    plain='A cloud tool that connects different apps and moves data between them automatically, mostly by drag and drop.',
    how=[('Trigger', 'Schedule, webhook, or event in a connected app.'), ('Connectors', 'Prebuilt authentication and operations for 100s of apps.'), ('Map and transform', 'Change formats and fields.'), ('Control flow', 'Conditions, loops, retries, error paths.'), ('Run and monitor', 'Managed execution with run history.')],
    words=[('connector', 'a ready-made link to an app’s API'), ('workflow', 'a series of automated steps'), ('webhook', 'a URL that receives event notifications')],
    diff=table(['', 'iPaaS', 'Custom integration code'], [['Build speed', 'hours', 'days'], ['Flexibility', 'connector limits', 'anything'], ['Who can build', 'developers and power users', 'developers']], minw=440),
    where=['SaaS-to-SaaS automation', 'ERP/CRM integration', 'File and data transfers between partners'],
    realworld='Gartner defined the iPaaS category in the early 2010s; today Microsoft Power Automate and Azure Logic Apps share the same connector ecosystem of over a thousand connectors.',
    pro='iPaaS flows are code too: export them (Logic Apps definitions as JSON/Bicep, Google Application Integration as JSON) into git and deploy through pipelines — otherwise production integrations live only in someone’s browser.')

A_MOB = mk(['Add the SDK', 'Use ready back-end features', 'Rules protect data'], ['app|Android/iOS/Web|SDK', 'back end|auth, DB, files|push, analytics', 'rules|per-user access|no server code'], ['green', 'blue', 'red'],
           ['the app talks to the back-end services directly', 'login, database, storage, notifications out of the box', 'security rules decide who may read/write what'],
           [('SDK', 'The mobile or web app includes the provider’s SDK.', ''), ('Features', 'Authentication, real-time database, file storage, push and analytics are ready-made.', ''), ('Rules', 'Declarative security rules protect each user’s data.', '')],
           'Mobile back end in action', 'A back end without writing a back end.', 'MBaaS', 'Animation: app with SDK; ready-made back-end features; security rules.', 'p5anim')
T5 = vtype(5, 'Mobile back end as a service (MBaaS)', 'green',
    '<b>Mobile Backend as a Service (MBaaS)</b> provides ready-made back-end capabilities for mobile and web apps — user authentication, databases with real-time sync, file storage, push notifications, analytics, hosting and serverless functions — consumed through client SDKs and protected by declarative security rules.',
    'A ready-made shop counter with billing machine, CCTV and storage: you just arrange your products and open the shutter.',
    'TiffinGo’s delivery-partner app uses Firebase: phone-number login, Firestore for live order status, Cloud Messaging for “new order nearby” notifications — built by one Android developer without a server.',
    'Google Firebase, AWS Amplify (with Cognito, AppSync, S3), Azure Static Web Apps + Functions/Entra External ID; Supabase (open source).',
    '', A_MOB,
    'mobile/web apps that need login, sync and notifications fast, with small teams.',
    'complex business logic and server-side secrets are needed — add functions or a proper API tier.',
    plain='A complete ready-made back end for apps — login, data, files and notifications — so app developers do not have to build servers.',
    how=[('Create project', 'Register Android/iOS/web apps.'), ('Add SDK', 'Client libraries in the app.'), ('Use services', 'Auth, database, storage, messaging.'), ('Write rules', 'Who can read/write each document or file.'), ('Extend', 'Functions for server-side logic.')],
    words=[('SDK', 'software development kit — libraries for an app'), ('real-time sync', 'data changes appear on all devices instantly'), ('push notification', 'a message sent to a phone even when the app is closed')],
    diff=table(['', 'MBaaS', 'Custom API + DB'], [['Back-end code needed', 'little', 'all of it'], ['Offline sync, push', 'built in', 'you build it'], ['Lock-in', 'higher', 'lower']], minw=440),
    where=['Consumer mobile apps', 'Chat and live-tracking apps', 'Hackathons and MVPs'],
    realworld='Firebase began as a real-time database start-up acquired by Google in 2014 and became Google’s mobile platform; many Indian start-up apps launched their first versions entirely on it.',
    pro='In MBaaS the security rules <i>are</i> your back end: a rule like “allow read, write: if true” in Firestore exposes the whole database to anyone with the app — one of the most common causes of app data leaks.')

A_DAI = mk(['Load data', 'Query / train', 'Serve insight'], ['data|warehouse|lake files', 'engine|SQL / Spark|AutoML/notebooks', 'output|dashboards|predictions API'], ['violet', 'blue', 'green'],
           ['no cluster to install', 'serverless SQL or managed ML training', 'dashboards and model endpoints as services'],
           [('Load', 'Data lands in a managed warehouse or lake.', ''), ('Process', 'Serverless SQL, Spark or ML training — no cluster setup.', ''), ('Serve', 'Dashboards and prediction endpoints as managed services.', '')],
           'Data & AI PaaS in action', 'Analytics and ML without infrastructure.', 'Data & AI PaaS', 'Animation: data loaded; serverless SQL or ML training; dashboards and predictions served.', 'p6anim')
T6 = vtype(6, 'Data and AI PaaS', 'violet',
    '<b>Data and AI platforms as a service</b> provide managed environments for analytics and machine learning — serverless data warehouses and SQL engines, managed Spark, notebooks, model training, AutoML, model hosting and foundation-model APIs — so teams work with data and models instead of clusters and GPUs.',
    'A fully equipped laboratory you rent by the hour: instruments, chemicals and safety are provided; you run the experiments.',
    'TiffinGo’s analyst queries two years of orders in BigQuery with plain SQL (no cluster), and the data scientist trains a delivery-time model in Vertex AI and deploys it as an endpoint the app calls.',
    'Google BigQuery, Vertex AI; Microsoft Fabric, Azure Databricks, Azure Machine Learning, Microsoft Foundry; Amazon Redshift Serverless, Athena, EMR Serverless, SageMaker AI, Bedrock.',
    'Lesson 6.4 maps these services across clouds.', A_DAI,
    'analytics or ML work where infrastructure would slow the team down.',
    'costs are not watched — pay-per-query and GPU hours can surprise.',
    plain='Ready-made cloud tools for analysing big data and building AI models, without setting up servers or clusters.',
    how=[('Ingest', 'Load or stream data into managed storage.'), ('Explore', 'SQL editors, notebooks.'), ('Process/train', 'Serverless SQL, Spark, ML training jobs.'), ('Deploy', 'Dashboards, scheduled queries, model endpoints.'), ('Govern', 'Catalogues, access policies, cost controls.')],
    words=[('data warehouse', 'database optimised for analysis'), ('notebook', 'an interactive document mixing code and results'), ('model endpoint', 'a URL that returns predictions')],
    diff=table(['', 'Data & AI PaaS', 'Self-managed Hadoop/Spark on VMs'], [['Setup', 'none', 'cluster install and tuning'], ['Billing', 'per query / per job', 'per VM hour'], ['Control', 'less', 'full']], minw=480),
    where=['BI dashboards', 'Data science and ML', 'Big data processing for courses like PGCP-BDA'],
    realworld='BigQuery’s free tier includes 1 TB of queries and 10 GB of storage per month, and its public datasets let students run SQL over large real datasets without loading any data.',
    pro='Serverless SQL bills by data scanned: <code>SELECT *</code> on a wide table can cost 50× more than selecting three columns. Columnar formats, partitioning and clustering are cost features as much as speed features.')

A_PRV = mk(['Install the platform', 'Developers push apps', 'Runs anywhere'], ['platform|OpenShift / CF|on your infra', 'self-service|git push / image|routes, TLS', 'hybrid|data centre +|any cloud'], ['red', 'green', 'blue'],
           ['your ops team installs and runs the PaaS', 'developers get the PaaS experience', 'same platform on-premises and in clouds'],
           [('Install', 'Your platform team runs a PaaS (e.g. OpenShift) on your own infrastructure.', ''), ('Self-service', 'Developers deploy apps as on public PaaS.', ''), ('Hybrid', 'The same platform runs in your data centre and in public clouds.', '')],
           'Private / hybrid PaaS in action', 'PaaS on your own terms.', 'Private PaaS', 'Animation: platform installed on own infrastructure; developers self-serve; same platform across data centre and clouds.', 'p7anim')
T7 = vtype(7, 'Private and hybrid PaaS', 'red',
    '<b>Private (or hybrid) PaaS</b> is platform software that an organisation installs and operates on its own infrastructure — on-premises or on IaaS in any cloud — to give its developers a PaaS experience (self-service deploys, routing, scaling) while keeping control over location, security and data.',
    'A company canteen run by your own staff: the same self-service counter experience as a restaurant, but inside your building and under your rules.',
    'A bank TiffinGo works with runs Red Hat OpenShift both in its Mumbai data centre and on AWS; its developers deploy the same way to both, and regulated data stays on-premises.',
    'Red Hat OpenShift (self-managed, or managed as ROSA on AWS / ARO on Azure), Cloud Foundry (incl. Tanzu Application Service), Azure Arc-enabled services, Google Distributed Cloud.',
    'Hybrid and private clouds are covered in Module 3.', A_PRV,
    'regulation, data residency or existing data centres require PaaS outside public clouds, or one platform across many clouds.',
    'you lack a platform team — running a PaaS is a product in itself.',
    plain='A company runs its own “PaaS” software on its own servers, so its developers get the easy deploy experience while data stays in-house.',
    how=[('Provide infrastructure', 'VMs or bare metal on-premises or in clouds.'), ('Install platform', 'Kubernetes-based or Cloud Foundry.'), ('Offer self-service', 'Templates, pipelines, catalogue.'), ('Operate', 'Upgrades, security, capacity by the platform team.'), ('Span locations', 'Same tooling everywhere.')],
    words=[('platform team', 'engineers who run the internal platform for other teams'), ('data residency', 'rules about where data must physically stay'), ('hybrid', 'combining on-premises and public cloud')],
    diff=table(['', 'Private PaaS', 'Public PaaS'], [['Who operates it', 'your team (or managed variant)', 'cloud provider'], ['Location', 'anywhere you choose', 'provider Regions'], ['Effort', 'high', 'low']], minw=440),
    where=['Banks and government', 'Telecom operators', 'Multi-cloud enterprises'],
    realworld='Many Indian banks and insurers run Red Hat OpenShift as their internal application platform; managed variants (ROSA on AWS, Azure Red Hat OpenShift) let them move parts to public cloud with the same developer experience.',
    pro='The industry term today is <b>internal developer platform</b> (platform engineering): a private PaaS is less about the product installed and more about the golden paths, templates and self-service your platform team offers.')

SUMMARY = table(['#', 'PaaS type', 'You bring', 'Examples', 'TiffinGo use'], [
    ['1', 'Application PaaS', 'source code', 'App Service, Beanstalk, App Engine', 'feedback app'], ['2', 'Container PaaS', 'container image', 'Cloud Run, Container Apps', 'route-optimiser API'], ['3', 'Database PaaS', 'schema + data', 'RDS, Azure SQL, Cloud SQL', 'orders DB'],
    ['4', 'Integration PaaS', 'workflow', 'Logic Apps, AppFlow, App Integration', 'Shopify → Sheets'], ['5', 'Mobile back end', 'app + rules', 'Firebase, Amplify', 'delivery-partner app'], ['6', 'Data & AI PaaS', 'data + models', 'BigQuery, Fabric, SageMaker AI', 'analytics, ML'], ['7', 'Private PaaS', 'your platform team', 'OpenShift, Cloud Foundry', 'bank partner']], minw=660)
CHECK = ('  <h3>Check yourself: which PaaS type?</h3>\n' +
    qx('A. Every new Google Form response should create a ticket in Jira automatically.', ['DBaaS', 'iPaaS', 'Container PaaS', 'IaaS'], 1, 'Integration.') +
    qx('B. A Flask app with standard libraries, deployed in minutes.', ['Application PaaS', 'Bare metal', 'Private PaaS', 'MBaaS'], 0, 'aPaaS.') +
    qx('C. An API needs a custom compiled library and should scale to zero.', ['App Service F1', 'Container PaaS (Cloud Run / Container Apps)', 'DBaaS', 'iPaaS'], 1, 'Container PaaS.') +
    qx('D. A regulated bank wants PaaS in its own data centre.', ['Public aPaaS only', 'Private PaaS (e.g. OpenShift)', 'MBaaS', 'SaaS'], 1, 'Private PaaS.'))

TYPES = ('  <p>Seven kinds of PaaS, each in the same pattern: definition, plain words, analogy, internal steps, animation, differences, where used, real-world example, TiffinGo scenario and an expert note.</p>\n'
         + challenge(['Why can’t you get the real postgres superuser on many DBaaS offerings?', 'Which single Firestore rule has leaked many apps’ data?', 'Why can SELECT * be 50× more expensive on serverless SQL?'], 'types 3, 5 and 6') + MAP
         + jump(['App PaaS', 'Container PaaS', 'DBaaS', 'iPaaS', 'MBaaS', 'Data & AI', 'Private PaaS']) + T1 + T2 + T3 + T4 + T5 + T6 + T7
         + '\n  <h3 style="margin-top:34px">All seven side by side</h3>\n' + SUMMARY + '\n' + CHECK)

parts = wwu([
    ('Runtime stack', 'Supported language versions.', 'Defines what code can run and when you must upgrade.', 'Python 3.12, Node 22, Java 21, .NET 8.'),
    ('Plan / tier', 'The size and features you pay for.', 'Free tiers lack scaling, slots, custom domains.', 'App Service F1/B1/S1/P1v3, EB instance types, App Engine instance classes.'),
    ('Deployment slots / versions', 'Parallel versions of an app.', 'Safe releases and instant rollback.', 'App Service slots, App Engine versions, EB environments.'),
    ('App settings / env vars', 'Configuration outside the code.', '12-factor apps; secrets via key vaults.', 'App settings, EB environment properties, app.yaml env_variables.'),
    ('Scale settings', 'Manual or automatic instance counts.', 'The platform scales; you set limits.', 'Autoscale rules, EB ASG, App Engine automatic scaling.'),
    ('Platform limits', 'Timeouts, file system, ports, background work.', 'Decide whether PaaS fits.', 'Request timeouts, read-only or ephemeral disks.')])

DEEP = ('  <h3>NIST definition of PaaS</h3>\n  <p>NIST SP 800-145: “The capability provided to the consumer is to deploy onto the cloud infrastructure consumer-created or acquired applications created using programming languages, libraries, services, and tools supported by the provider. The consumer does not manage or control the underlying cloud infrastructure including network, servers, operating systems, or storage, but has control over the deployed applications and possibly configuration settings for the application-hosting environment.”</p>\n'
    '  <h3>Shared responsibility in PaaS</h3>\n' + table(['Area', 'Provider', 'You'], [['Physical, network, hypervisor', '✔', ''], ['OS and runtime patching', '✔', 'choose supported versions'], ['Application code and dependencies', '', '✔ (including vulnerable libraries)'], ['Identity, access, secrets', 'tools', '✔'], ['Data and its classification', '', '✔'], ['Network exposure of the app', 'options', '✔ choose private endpoints, WAF']], minw=480) +
    '\n  <h3>Lock-in: real but manageable</h3>\n  <p>Code on PaaS is usually portable (plain Flask/Spring apps); lock-in comes from platform-specific services (proprietary queues, auth, config). Keep business logic framework-standard, wrap provider SDKs behind small interfaces, and prefer container PaaS when portability matters most.</p>')

clouds = vendor_tabs('<p><b>AWS:</b> Elastic Beanstalk (aPaaS), ECS Express Mode / Fargate (containers), RDS/Aurora/DynamoDB (DBaaS), AppFlow & Step Functions (integration), Amplify (mobile/web back end), Athena/Redshift Serverless/SageMaker AI/Bedrock (data & AI), ROSA (managed OpenShift).</p>',
    '<p><b>Azure:</b> App Service (aPaaS), Container Apps, Azure SQL/Database for PostgreSQL/Cosmos DB, Logic Apps & Power Automate, Static Web Apps + Functions, Fabric/Databricks/Azure ML/Microsoft Foundry, Azure Red Hat OpenShift, Azure Arc.</p>',
    '<p><b>Google Cloud:</b> App Engine (aPaaS), Cloud Run, Cloud SQL/AlloyDB/Spanner/Firestore, Application Integration & Workflows, Firebase, BigQuery/Vertex AI, Google Distributed Cloud.</p>') + \
    cloud3([['App PaaS', 'Elastic Beanstalk', 'App Service', 'App Engine'], ['Container PaaS', 'ECS Express Mode / Fargate', 'Container Apps', 'Cloud Run'], ['DBaaS (PostgreSQL)', 'RDS / Aurora', 'Database for PostgreSQL', 'Cloud SQL / AlloyDB'], ['iPaaS', 'AppFlow, Step Functions', 'Logic Apps', 'Application Integration'], ['Mobile back end', 'Amplify', 'Static Web Apps + Functions', 'Firebase'], ['Data warehouse', 'Redshift Serverless', 'Fabric', 'BigQuery']])

# ------------------------------------------------------------------ practical
APP_PY = "from flask import Flask\napp = Flask(__name__)\n\n@app.route('/')\ndef home():\n    return '<h1>TiffinGo feedback</h1><p>Running on PaaS</p>'"

MOCKQ.extend([
 (mock('aws', ['Elastic Beanstalk', 'Create environment'], ['Applications', 'Environments', 'Change history'], 'Environments',
       [('Environment tier', '( ) Web server environment'), ('Application name', 'tiffingo-feedback'), ('Platform', '▾ Python · Python 3.12 running on 64bit Amazon Linux 2023'), ('Application code', '( ) Sample application'), ('Presets', '( ) Single instance (free tier eligible)')], 'Next'),
  mock('az', ['Home', 'App Services', 'Create Web App'], ['Basics', 'Database', 'Deployment', 'Networking', 'Monitoring', 'Review + create'], 'Basics',
       [('Name', 'tiffingo-feedback-1234'), ('Publish · Runtime stack', 'Code · Python 3.12'), ('Region', '▾ Central India'), ('Pricing plan', '▾ Free F1 (Shared infrastructure)')], 'Review + create'),
  mock('gcp', ['App Engine', 'Dashboard'], ['Dashboard', 'Services', 'Versions', 'Instances', 'Settings'], 'Dashboard',
       [('Region (permanent)', '▾ asia-south1'), ('Deploy', 'gcloud app deploy (from Cloud Shell)'), ('Service · Version', 'default · v1 (100% traffic)')], 'Create application')),
 (mock('aws', ['Elastic Beanstalk', 'tiffingo-feedback-env'], ['Go to environment', 'Configuration', 'Events', 'Health', 'Logs', 'Monitoring'], 'Health',
       [('Health', 'OK'), ('Logs', '▾ Request logs → Last 100 lines')], 'Request logs'),
  mock('az', ['Home', 'tiffingo-feedback-1234', 'Log stream'], ['Overview', 'Deployment Center', 'Configuration', 'Log stream', 'App Service logs'], 'Log stream',
       [('App Service logs', 'Application logging (Filesystem): On'), ('Log stream', '… GET / 200 …')], 'Start'),
  mock('gcp', ['App Engine', 'Versions'], ['Dashboard', 'Services', 'Versions', 'Instances'], 'Versions',
       [('default · v1', 'Traffic 50%'), ('default · v2', 'Traffic 50% (split by IP)')], 'Split traffic')),
 (mock('aws', ['RDS', 'Databases', 'Create database'], ['Dashboard', 'Databases', 'Snapshots', 'Parameter groups'], 'Databases',
       [('Creation method · Engine', 'Easy create · PostgreSQL'), ('Templates', '( ) Free tier'), ('DB instance identifier', 'tiffingo-db'), ('Credentials', '[x] Manage master credentials in AWS Secrets Manager')], 'Create database'),
  mock('az', ['Home', 'Azure Database for PostgreSQL flexible servers', 'Create'], ['Basics', 'Networking', 'Security', 'Tags', 'Review + create'], 'Basics',
       [('Server name', 'tiffingo-pg-1234'), ('Region · Version', 'Central India · 16'), ('Workload type', '( ) Development (Burstable B1ms)'), ('Authentication', '▾ PostgreSQL authentication only')], 'Review + create'),
  mock('gcp', ['SQL', 'Create an instance', 'PostgreSQL'], ['Overview', 'Connections', 'Users', 'Databases', 'Backups'], 'Overview',
       [('Edition', '( ) Enterprise · preset Sandbox'), ('Instance ID · Password', 'tiffingo-db · (generate)'), ('Region · Zonal availability', 'asia-south1 · Single zone'), ('Machine', '▾ Shared core · 1 vCPU, 0.614 GB')], 'Create instance')),
])

STEP1 = ('1 · Deploy a web app from code', tri(
    (['[[Elastic Beanstalk]] → [[Create application]] → web server environment, name <code>tiffingo-feedback</code>, platform [[Python]], application code [[Sample application]], preset [[Single instance (free tier eligible)]].', 'Service access: [[Create and use new service role]]; EC2 instance profile: create <code>aws-elasticbeanstalk-ec2-role</code> if offered → [[Skip to review]] → [[Submit]].', 'After ~5 minutes open the environment [[Domain]] link.'],
     "aws iam create-role --role-name aws-elasticbeanstalk-ec2-role --assume-role-policy-document \\\n  '{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"ec2.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}'\naws iam attach-role-policy --role-name aws-elasticbeanstalk-ec2-role --policy-arn arn:aws:iam::aws:policy/AWSElasticBeanstalkWebTier\naws iam create-instance-profile --instance-profile-name aws-elasticbeanstalk-ec2-role\naws iam add-role-to-instance-profile --instance-profile-name aws-elasticbeanstalk-ec2-role --role-name aws-elasticbeanstalk-ec2-role\nSTACK=$(aws elasticbeanstalk list-available-solution-stacks --query \"SolutionStacks[?contains(@, 'running Python 3.12')] | [0]\" --output text)\naws elasticbeanstalk create-application --application-name tiffingo-feedback\nsleep 10\naws elasticbeanstalk create-environment --application-name tiffingo-feedback --environment-name tiffingo-feedback-env \\\n  --solution-stack-name \"$STACK\" --option-settings \\\n  Namespace=aws:autoscaling:launchconfiguration,OptionName=IamInstanceProfile,Value=aws-elasticbeanstalk-ec2-role \\\n  Namespace=aws:elasticbeanstalk:environment,OptionName=EnvironmentType,Value=SingleInstance\naws elasticbeanstalk wait environment-exists --environment-names tiffingo-feedback-env\naws elasticbeanstalk describe-environments --environment-names tiffingo-feedback-env --query 'Environments[0].[Status,Health,CNAME]' --output text",
     '<code>Ready Green tiffingo-feedback-env.….ap-south-1.elasticbeanstalk.com</code>; the URL shows the Beanstalk sample page. Look at [[EC2]]: Beanstalk created an instance in <i>your</i> account.'.replace('[[', '<b>').replace(']]', '</b>')),
    (['[[App Services]] → [[Create]] → [[Web App]] → rg-tiffingo, name <code>tiffingo-feedback-&lt;n&gt;</code>, publish [[Code]], runtime [[Python 3.12]], Central India, pricing [[Free F1]] → [[Review + create]].', 'Deploy code: in Cloud Shell create the two files on the right and run <code>az webapp up</code> (it zips, uploads and builds with Oryx).', 'Open <code>https://NAME.azurewebsites.net</code>.'],
     f"mkdir feedback && cd feedback\ncat > app.py <<'EOF'\n{APP_PY}\nEOF\necho flask > requirements.txt\nAPP=tiffingo-feedback-$RANDOM\naz webapp up --name $APP --resource-group rg-tiffingo --location centralindia --runtime PYTHON:3.12 --sku F1\ncurl https://$APP.azurewebsites.net",
     '“TiffinGo feedback — Running on PaaS” over HTTPS, with a certificate you never configured. F1 is free (60 CPU-minutes a day, no custom scaling).'),
    (['[[App Engine]] → [[Create application]] → Region [[asia-south1]] (permanent for the project) → language Python.', 'In Cloud Shell create the files on the right (main.py, requirements.txt, app.yaml) and run <code>gcloud app deploy</code>.', 'Open the URL printed (<code>https://PROJECT.el.r.appspot.com</code>).'],
     f"mkdir feedback && cd feedback\ncat > main.py <<'EOF'\n{APP_PY}\nEOF\necho flask > requirements.txt\necho 'runtime: python312' > app.yaml\ngcloud app create --region=asia-south1\ngcloud app deploy --quiet --version=v1\ngcloud app browse --no-launch-browser",
     'a deployed service <code>default</code> version v1 and its URL. App Engine standard has a daily free quota of instance hours.')),
    'Three platforms, one idea: code in, HTTPS URL out. Note how Beanstalk shows its EC2 instance while App Service and App Engine hide the servers.')

STEP2 = ('2 · Operate it: logs, health and versions', tri(
    (['Environment → [[Health]]: Green/OK with instance details.', '[[Logs]] → [[Request logs]] → [[Last 100 lines]] → download.', '[[Configuration]] → [[Instance traffic and scaling]]: change to load balanced, min 1 / max 2 (creates an ALB — optional, it costs money).'],
     "aws elasticbeanstalk describe-environment-health --environment-name tiffingo-feedback-env --attribute-names All \\\n  --query '[HealthStatus,Color]' --output text\naws elasticbeanstalk request-environment-info --environment-name tiffingo-feedback-env --info-type tail\nsleep 20\naws elasticbeanstalk retrieve-environment-info --environment-name tiffingo-feedback-env --info-type tail --query 'EnvironmentInfo[0].Message' --output text",
     '<code>Ok Green</code> and a pre-signed URL to the last 100 log lines (nginx and web.stdout logs).'),
    (['App → [[App Service logs]] → Application logging [[File System]] → [[Save]].', '[[Log stream]] → refresh the site in another tab and watch requests arrive.', '[[Deployment Center]] → [[Logs]] shows each deployment and its build output.'],
     'az webapp log config --name $APP --resource-group rg-tiffingo --application-logging filesystem --web-server-logging filesystem\naz webapp log tail --name $APP --resource-group rg-tiffingo     # Ctrl+C to stop\naz webapp deployment list-publishing-profiles --name $APP --resource-group rg-tiffingo --query "[].publishMethod" --output tsv',
     'live log lines with your requests, and the available publish methods (MSDeploy, FTP, ZipDeploy).'),
    (['Change the text in main.py and deploy as v2 without moving traffic: <code>gcloud app deploy --version=v2 --no-promote</code>.', '[[Versions]] → select both → [[Split traffic]] → 50/50 by IP → [[Save]].', '[[Logs Explorer]] → resource “GAE Application” for request logs.'],
     "sed -i 's/Running on PaaS/Version 2/' main.py\ngcloud app deploy --quiet --version=v2 --no-promote\ngcloud app services set-traffic default --splits=v1=0.5,v2=0.5 --split-by=ip --quiet\ngcloud app versions list\ngcloud app logs read --limit=10",
     'two versions each with TRAFFIC_SPLIT 0.5 — a canary release with one command.')),
    'Operating PaaS is about settings — logs, scaling, versions — not servers.')

STEP3 = ('3 · Create a managed database (DBaaS)', tri(
    (['[[RDS]] → [[Create database]] → [[Easy create]] → PostgreSQL → template [[Free tier]] → identifier <code>tiffingo-db</code> → [[Manage master credentials in AWS Secrets Manager]] → [[Create database]].', 'After ~5–10 minutes: note [[Endpoint]], [[Backups]] (automated, 1 day retention on free tier) and [[Maintenance]] window — the provider does these for you.'],
     'aws rds create-db-instance --db-instance-identifier tiffingo-db --engine postgres --db-instance-class db.t4g.micro \\\n  --allocated-storage 20 --master-username tiffingo --manage-master-user-password --no-publicly-accessible \\\n  --backup-retention-period 1\naws rds wait db-instance-available --db-instance-identifier tiffingo-db\naws rds describe-db-instances --db-instance-identifier tiffingo-db \\\n  --query \'DBInstances[0].[DBInstanceStatus,Engine,EngineVersion,Endpoint.Address,PreferredMaintenanceWindow]\' --output text',
     '<code>available postgres 17.x tiffingo-db.xxxx.ap-south-1.rds.amazonaws.com …</code>; the password is in Secrets Manager, not in your shell history.'),
    (['[[Azure Database for PostgreSQL flexible servers]] → [[Create]] → rg-tiffingo, name <code>tiffingo-pg-&lt;n&gt;</code>, Central India, version 16, workload [[Development]] (Burstable B1ms).', '[[Networking]]: [[Public access]] with no firewall rules (or private access) → [[Review + create]] (~5–10 minutes).', 'Open it → [[Backup and restore]], [[Server parameters]], [[Maintenance]].'],
     'PG=tiffingo-pg-$RANDOM\naz postgres flexible-server create --resource-group rg-tiffingo --name $PG --location centralindia \\\n  --tier Burstable --sku-name Standard_B1ms --storage-size 32 --version 16 --admin-user tiffingo --public-access None\naz postgres flexible-server show --resource-group rg-tiffingo --name $PG --query "[state,version,fullyQualifiedDomainName,backup.backupRetentionDays]" --output tsv',
     '<code>Ready 16 tiffingo-pg-1234.postgres.database.azure.com 7</code>; the CLI prints a generated admin password once — store it in Key Vault in real projects.'),
    (['[[SQL]] → [[Create instance]] → [[PostgreSQL]] → edition [[Enterprise]], preset [[Sandbox]], ID <code>tiffingo-db</code>, generate password, region asia-south1, single zone, smallest shared-core machine → [[Create instance]] (~5–10 minutes).', 'Open it → [[Backups]] (automated daily), [[Maintenance]].'],
     'gcloud services enable sqladmin.googleapis.com\ngcloud sql instances create tiffingo-db --database-version=POSTGRES_16 --edition=ENTERPRISE \\\n  --tier=db-f1-micro --region=asia-south1 --storage-size=10GB\ngcloud sql instances describe tiffingo-db --format="value(state,databaseVersion,settings.backupConfiguration.enabled)"',
     '<code>RUNNABLE POSTGRES_16 True</code>. Set the postgres password with <code>gcloud sql users set-password postgres --instance=tiffingo-db --prompt-for-password</code>.')),
    'You never installed PostgreSQL or patched an OS — that is DBaaS. A managed database costs money every hour it exists: delete it right after the lab.')

prac = practical(OWN_INTRO + ' Step 3’s database is the only part that costs real money per hour — delete it within the hour.', [SETUP_STEP, STEP1, STEP2, STEP3],
    cleanup='<b>AWS:</b> <code>aws rds delete-db-instance --db-instance-identifier tiffingo-db --skip-final-snapshot --delete-automated-backups; aws elasticbeanstalk delete-application --application-name tiffingo-feedback --terminate-env-by-force</code>; the IAM role/instance profile can stay (free) or be deleted.<br>'
            '<b>Azure:</b> <code>az group delete --name rg-tiffingo --yes --no-wait</code> (web app, plan and PostgreSQL server).<br>'
            '<b>Google Cloud:</b> <code>gcloud sql instances delete tiffingo-db --quiet; gcloud app versions delete v2 --quiet</code>. An App Engine application cannot be deleted — disable it under [[App Engine]] → [[Settings]] → [[Disable application]], or delete the whole lab project.'.replace('[[', '<b>').replace(']]', '</b>'))

mist = mistakes([
    ['Choosing PaaS, then fighting it for OS access.', 'Not checking platform limits.', 'Check runtimes, timeouts, file system and networking first; use container PaaS if needed.'],
    ['Secrets in code or app settings in plain text.', 'Convenience.', 'Key Vault / Secrets Manager / Secret Manager references.'],
    ['Assuming the provider secures your code.', 'Misreading shared responsibility.', 'You patch dependencies and fix app vulnerabilities.'],
    ['Free tier in production.', 'Cheap start.', 'Free tiers lack SLAs, scaling and custom domains with TLS.'],
    ['Forgetting App Engine’s region is permanent.', 'Quick setup.', 'Pick the region carefully; use a separate project for labs.'],
    ['Leaving DBaaS instances running after labs.', 'They look idle.', 'Delete or stop; check the bill next day.']])

cert = table(['Exam / syllabus', 'What is asked'], [['C-DAC PGCP-BDA', 'PaaS: definition, characteristics, types, examples, benefits and limitations.'], ['AWS CLF-C02', 'Elastic Beanstalk, managed databases (RDS, Aurora, DynamoDB), Amplify; shared responsibility for managed services.'], ['AZ-900', 'Describe PaaS, shared responsibility, App Service, Azure SQL, Container Apps; use cases for PaaS.'], ['Google Cloud Digital Leader', 'App Engine, Cloud Run, Cloud SQL, Firebase; choosing between IaaS, PaaS and SaaS.']], minw=560) + \
    qx('1. In PaaS, the customer manages…', ['the OS and patches', 'the application and data', 'the hypervisor', 'physical security'], 1, 'App + data.') + \
    qx('2. Which AWS service lets you upload code and automatically handles capacity provisioning, load balancing and health monitoring?', ['AWS Elastic Beanstalk', 'Amazon EC2', 'AWS Direct Connect', 'Amazon S3 Glacier'], 0, 'aPaaS.') + \
    qx('3. Azure SQL Database is an example of…', ['IaaS', 'PaaS', 'SaaS', 'on-premises'], 1, 'DBaaS = PaaS.') + \
    qx('4. Which Azure service builds automated workflows that integrate apps and data with connectors?', ['Azure Logic Apps', 'Azure Disk Storage', 'Azure Bastion', 'Azure DNS'], 0, 'iPaaS.') + \
    qx('5. Firebase is mainly…', ['a CDN', 'a mobile/web back-end platform', 'a hypervisor', 'a VPN'], 1, 'MBaaS.') + \
    qx('6. A limitation of PaaS compared with IaaS is…', ['no scaling', 'less control over the OS and runtime', 'no databases', 'no HTTPS'], 1, 'Control trade-off.')

proj = miniproject('Mini project: move TiffinGo’s feedback app from IaaS to PaaS',
    'Feel the difference between owning servers and owning code.',
    ['<b>List</b> everything Arjun did on the VM (OS, runtime, Nginx, TLS, firewall, logs, backups).',
     '<b>Deploy</b> the same Flask app on a PaaS of your choice (step 1).',
     '<b>Map</b> each task from the list to “platform does it” or “still mine”.',
     '<b>Release</b> v2 with a slot or traffic split (step 2).',
     '<b>Database:</b> create a DBaaS instance and connect the app with an environment variable (step 3).',
     '<b>Report</b> time spent, cost per month and what you lost in control.'],
    'A working PaaS app, a responsibility table and a short IaaS-vs-PaaS comparison.', 'This lesson + 2.1 (IaaS) + 6.1 (compute).')

assemble_v2(HERE, story_h2='Three days to set up a server', hook_html=hk,
    narration='Arjun spent three days preparing a server before writing the first line of the feedback app. TiffinGo’s founder asked: is there a way to skip straight to the code?',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='What is PaaS?',
    formal='<b>Platform as a Service (PaaS)</b> is a cloud service model in which the provider delivers a complete development and runtime platform — operating system, language runtimes, middleware, databases and supporting services on managed infrastructure — so that customers deploy and manage their own applications and data without managing the underlying servers, storage, network or OS (NIST SP 800-145).',
    simple='You bring the code and data; the cloud gives you a ready-made place to run them, and looks after everything underneath.',
    interview=['“PaaS gives a managed platform to deploy applications — the provider manages OS, runtime, scaling and patching; I manage code, configuration and data. Examples: Elastic Beanstalk, Azure App Service, App Engine, and managed databases like RDS.”', '“PaaS types include application platforms, container platforms, DBaaS, iPaaS, mobile back ends, data and AI platforms, and private PaaS like OpenShift.”'],
    terms_rows=[('PaaS', 'Managed platform for apps.'), ('aPaaS', 'Run web apps from code.'), ('DBaaS', 'Managed database.'), ('iPaaS', 'Integration platform.'), ('MBaaS', 'Mobile back end.'), ('Buildpack', 'Turns source into a runnable app.'), ('Runtime', 'Language engine version.'), ('Deployment slot', 'Parallel version for safe release.'), ('Private PaaS', 'Platform you operate.'), ('Lock-in', 'Dependence on platform features.')],
    exam='All three exams ask to classify services as IaaS/PaaS/SaaS and the shared responsibility for PaaS; CLF-C02 names Elastic Beanstalk, AZ-900 App Service and Azure SQL, Digital Leader App Engine/Cloud Run/Cloud SQL.',
    picture_h2='Who manages what, and the PaaS family', picture_html=picture,
    after_picture=[('types', 'Types, one by one', 'Seven types of PaaS, one by one', TYPES)],
    how_h2='From code to a live URL on PaaS', how_intro='The platform’s work, step by step.', how_anim=PUSH,
    parts_h2='Six settings you meet on every PaaS', parts_html=parts, lv='',
    myth_rows=[('PaaS means no security work.', 'You still own code, dependencies, identity and data.', 'Deep dive.'), ('PaaS is only for small apps.', 'Large banks and SaaS products run on PaaS and DBaaS.', 'Types 3, 7.'), ('PaaS = App Engine/Heroku only.', 'Databases, integration, mobile and AI platforms are PaaS too.', 'The family figure.')],
    extra_secs=[('deep', 'Deep dive', 'NIST definition, shared responsibility in PaaS, lock-in', DEEP)],
    clouds_html=clouds, practical_html=prac, mistakes_html=mist, cert_html=cert, project_html=proj,
    can_now=['Define PaaS and its responsibility split.', 'Explain seven PaaS types with examples in AWS, Azure and Google Cloud.', 'Describe what a platform does between push and a live URL.', 'Deploy, observe and version an app on PaaS on your own account.', 'Create a managed database and explain what the provider handles.'],
    next_html='<a href="../03-saas-software-as-a-service/">2.3 SaaS: Software as a Service</a>.',
    pre='<b>Before you start:</b> <a href="../01-iaas-infrastructure-as-a-service/">2.1 IaaS</a>.')
