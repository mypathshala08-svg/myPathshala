import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
def cap(frames, steps, title, intro, panel, aria, hid, delay=5500):
    return anim_one('Animated', title, intro, panel, aria, cap_frames(frames, steps), [s[0] + '.' for s in steps], delay=delay, hid=hid)


hk = hook('TiffinGo’s first version was one PHP server with the database on the same machine. It was cheap and simple — until Diwali, when the database ate all the memory and the website died with it. Why did splitting it into “tiers” fix this?',
    'Because <b>tiers</b> separate jobs that grow, fail and are secured differently: the <b>presentation tier</b> (what users see), the <b>application tier</b> (business logic) and the <b>data tier</b> (storage). Each tier can scale on its own, sit in its own network zone and be replaced without touching the others. This lesson explains 1-, 2-, 3- and n-tier designs, how they look in the cloud (including serverless and static front ends), how a request passes through the tiers — and you build a small three-tier app on <b>your own</b> account.',
    ['1-tier, 2-tier, 3-tier, n-tier — and when each is right.', 'One request through the three tiers of a cloud app.', 'Why the database tier must never be reachable from the internet.'])

def story_scene():
    o = t(180, 12, 'From one box to three tiers', 9, 'ink', bold=True)
    o += box(14, 28, 110, 80, 'red', rx=8) + t(69, 50, 'one server', 8, 'ink', bold=True) + t(69, 68, 'web + app + DB', 7, 'ink') + t(69, 92, 'Diwali: down ✘', 7, 'ink', bold=True)
    o += arrow(128, 68, 150, 68)
    for i, (n, tn) in enumerate([('Presentation', 'green'), ('Application', 'blue'), ('Data', 'violet')]):
        o += box(156 + i * 66, 28, 60, 80, tn, rx=8) + t(186 + i * 66, 62, n[:6], 7.2, 'ink', bold=True) + t(186 + i * 66, 76, n[6:] or ' ', 7.2, 'ink', bold=True)
    o += t(180, 126, 'Each tier scales, fails and is secured separately.', 7.6, 'ink', bold=True)
    return o
scene_svg = scene('One server running web, app and database fails at Diwali; it is split into presentation, application and data tiers.', story_scene(), 'Separate the <tspan font-weight="700" class="s-acc">jobs</tspan>, not just the servers.', h=140)
dialogue = '''R> Sir, can’t we just buy a bigger server? Splitting into tiers sounds like more work.
A> A bigger server still has one memory pool. When the database needs more, it starves the web server — and one crash takes everything down.
K> And with tiers?
A> The website can be a static site on a CDN, the API can scale out on many small servers or functions, and the database gets its own managed service with backups — in a private subnet nobody on the internet can reach.
R> So tiers are about scaling and security both.
A> And about teams: the front-end team can release without touching the database. Let’s see the patterns.'''

# ------------------------------------------------------------------ picture
def tiersfig():
    o = t(320, 16, 'A classic three-tier web application in the cloud', 11, 'ink', bold=True)
    o += box(10, 104, 70, 50, 'green', rx=8) + t(45, 126, 'users', 7.6, 'ink', bold=True) + t(45, 140, 'browser/app', 6.6, 'ink2')
    tiers = [('PRESENTATION TIER', 'public subnet / edge', ['CDN + static site', 'web servers or SPA', 'load balancer'], 'green'), ('APPLICATION TIER', 'private subnet', ['API servers / containers', 'functions', 'business rules'], 'blue'), ('DATA TIER', 'isolated private subnet', ['managed database', 'cache', 'object storage'], 'violet')]
    for i, (n, s, ls, tn) in enumerate(tiers):
        x = 100 + i * 180
        o += box(x, 34, 168, 190, tn, rx=10) + t(x + 84, 52, n, 8, 'ink', bold=True) + t(x + 84, 66, s, 6.8, 'ink2')
        for j, l in enumerate(ls): o += box(x + 14, 80 + j * 44, 140, 34, 'card', rx=5) + t(x + 84, 101 + j * 44, l, 7.2, 'ink')
        if i < 2: o += arrow(x + 170, 129, x + 178, 129)
    o += arrow(82, 129, 98, 129)
    o += t(320, 244, 'Rules: users talk only to the presentation tier; each tier talks only to the next one; the data tier has no internet path.', 7.4, 'ink2')
    return o
TIERS = bigfig('Three-tier architecture: users reach the presentation tier (CDN, static site, web servers, load balancer) in public subnets; it calls the application tier (API servers, containers, functions) in private subnets; which calls the data tier (database, cache, object storage) in isolated subnets.', tiersfig(), h=254)

def evofig():
    o = t(320, 16, 'From one tier to n tiers', 11, 'ink', bold=True)
    stages = [('1-tier', ['all in one']), ('2-tier', ['client', 'DB server']), ('3-tier', ['web', 'app', 'data']), ('n-tier', ['CDN', 'web', 'API', 'queue', 'workers', 'cache', 'DB'])]
    for i, (n, parts) in enumerate(stages):
        x = 14 + i * 156
        o += t(x + 72, 40, n, 9, 'ink', bold=True)
        h = min(24, 150 // len(parts))
        for j, p in enumerate(parts): o += box(x + 20, 50 + j * (h + 4), 104, h, ['red', 'amber', 'blue', 'violet'][i], rx=4) + t(x + 72, 50 + j * (h + 4) + h / 2 + 3, p, 6.8, 'ink')
    o += t(320, 232, 'More tiers = more independent scaling, security and teams — but more network hops, latency and things to operate.', 7.6, 'ink2')
    return o
EVO = bigfig('Evolution from one tier (everything in one) to two tiers (client and database server), three tiers (web, app, data) and n tiers (CDN, web, API, queue, workers, cache, database).', evofig(), h=244)

picture = ('  <p>The shape you will see in almost every cloud architecture diagram:</p>\n' + TIERS + '\n  <p>And how architectures grew into it:</p>\n' + EVO)

# ------------------------------------------------------------------ how: one request through tiers
RN = {'u': (4, 54, 54, 50, 'phone', 'Customer', 'menu page'), 'cdn': (66, 4, 60, 46, 'globe', 'CDN', 'static files'), 'lb': (66, 104, 60, 46, 'lb', 'Load bal.', 'public'),
      'app': (138, 54, 62, 50, 'server', 'App tier', 'private'), 'cache': (212, 4, 64, 46, 'chip', 'Cache', 'Redis'), 'db': (212, 104, 64, 46, 'db', 'Database', 'isolated'), 'resp': (290, 54, 66, 50, 'chart', 'JSON', '→ page')}
RS = [dict(on=['u', 'cdn'], hot='cdn', move=(58, 70, 70, 40, 'GET /'), head='Step 1 · Presentation: page and assets', text='HTML, JavaScript, CSS and photos come from the CDN edge (static site in a bucket).', text2='No server of ours is touched for these.', svc='S3/Blob/GCS static site + CloudFront/Front Door/Cloud CDN'),
      dict(on=['u', 'cdn', 'lb'], hot='lb', move=(28, 104, 66, 128, 'API'), head='Step 2 · The page calls the API', text='JavaScript calls GET /api/menu; the load balancer (or API gateway) in the public', text2='subnet receives it and checks health of the app tier.', svc='ALB / API Gateway · Application Gateway / APIM · Cloud LB / API Gateway'),
      dict(on=['u', 'cdn', 'lb', 'app'], hot='app', move=(126, 127, 150, 90, 'forward'), head='Step 3 · Application tier applies the rules', text='An app server in a private subnet checks the city, today’s menu, offers and', text2='stock — business logic lives only here.', svc='EC2/ECS/Lambda · App Service/Container Apps/Functions · Cloud Run/GKE'),
      dict(on=['u', 'cdn', 'lb', 'app', 'cache'], hot='cache', move=(200, 70, 222, 40, 'GET'), head='Step 4 · Cache first', text='The app asks Redis for “menu:pune:today”. A hit returns in under a millisecond', text2='and the database is not touched at all.', svc='ElastiCache / Azure Managed Redis / Memorystore'),
      dict(on=['u', 'cdn', 'lb', 'app', 'cache', 'db'], hot='db', move=(200, 90, 222, 120, 'SQL'), head='Step 5 · On a miss, the data tier', text='The app queries the database in an isolated subnet; only the app tier’s security', text2='group may connect. The result is cached for next time.', svc='RDS / Azure SQL / Cloud SQL'),
      dict(on=list(RN), hot='resp', move=(276, 127, 298, 90, 'JSON'), head='Step 6 · Back through the tiers', text='The app returns JSON; the browser renders the menu. Each tier could have scaled', text2='separately — e.g. 10 app servers but one database.', svc='Tiers scale, fail and deploy independently')]
FLOW = flow_anim('One request through three tiers', 'From a tap on “Menu” to the database and back.', 'Three tiers', 'Animation: static files from the CDN; API call to the load balancer; app tier logic; cache lookup; database query on miss; JSON response.', RN, RS, hid='tierflow')

# ------------------------------------------------------------------ types
def mapfig():
    o = t(320, 16, 'Seven tiered architectures', 11, 'ink', bold=True)
    items = [('1', 'Single-tier', 'all on one machine', 'red'), ('2', 'Two-tier', 'client + database', 'amber'), ('3', 'Three-tier', 'web · app · data', 'blue'),
             ('4', 'N-tier', '+ cache, queue, workers', 'violet'), ('5', 'Serverless three-tier', 'CDN · functions · NoSQL', 'green'), ('6', 'Static front end + API', 'SPA / JAMstack', 'green'), ('7', 'Tier isolation', 'subnets, SGs, roles', 'red')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 12 + (i % 4) * 156; y = 32 + (i // 4) * 84
        o += box(x, y, 148, 70, tn, rx=8) + pin(x + 16, y + 16, n) + t(x + 80, y + 34, a, 7.8, 'ink', bold=True) + t(x + 78, y + 54, b, 6.8, 'ink2')
    o += t(320, 210, '1–4 are the classic evolution · 5–6 are cloud-native forms · 7 is how tiers are protected.', 7.6, 'ink2')
    return o
MAP = bigfig('Map of seven tiered architectures: single-tier, two-tier, three-tier, n-tier, serverless three-tier, static front end plus API, tier isolation.', mapfig(), h=222)

def tbox(items, tones, k, cap_):
    o = ''
    n = len(items)
    w = (320 - (n - 1) * 10) / n
    for i, it in enumerate(items):
        x = 20 + i * (w + 10)
        on = i <= k if isinstance(k, int) else True
        o += box(x, 34, w, 70, tones[i] if on else 'card', rx=8)
        for j, l in enumerate(it.split('|')): o += t(x + w / 2, 60 + j * 14, l, 7.2 if j == 0 else 6.6, 'ink', bold=(j == 0))
        if i < n - 1: o += arrow(x + w, 69, x + w + 10, 69)
    return o + t(180, 128, cap_, 7.2, 'ink', bold=True)

def a1(k):
    o = t(180, 12, ['Everything together', 'Simple and fast', 'One failure = all down'][k], 9, 'ink', bold=True)
    o += box(100, 30, 160, 80, 'red' if k == 2 else 'amber', rx=8) + t(180, 50, 'one VM / one PC', 8, 'ink', bold=True)
    for j, n in enumerate(['UI', 'logic', 'database']): o += box(116 + j * 46, 62, 40, 34, 'card', rx=3) + t(136 + j * 46, 83, n, 6.6, 'ink')
    o += t(180, 132, ['UI, business logic and data in one process or machine', 'no network calls — fine for a prototype or desktop tool', 'cannot scale parts separately; a crash stops everything'][k], 7.2, 'ink', bold=True)
    return o
A1 = cap([a1(k) for k in range(3)], [('Together', 'All layers run in one application on one machine.', ''), ('Simple', 'Easy to build and run; no network between layers.', ''), ('Limits', 'One crash or overload stops everything; scaling means a bigger machine.', '')],
    'Single-tier in action', 'Everything in one place.', 'Single-tier', 'Animation: user interface, logic and database inside one machine; simple; one failure stops everything.', 't1anim')
T1 = vtype(1, 'Single-tier (one-tier) architecture', 'red',
    'A <b>single-tier architecture</b> places the user interface, business logic and data storage in one application on one machine or process, with no network separation between them.',
    'A roadside tea stall run by one person: takes the order, makes the tea and keeps the stock under the counter — perfect until 200 customers arrive.',
    'TiffinGo’s first prototype was one PHP app with MySQL on the same small VM. It was right for 20 orders a day — and wrong for Diwali.',
    'A single VM (EC2, Azure VM, Compute Engine) or Lightsail instance with a LAMP stack; desktop apps with SQLite.',
    '', A1,
    'prototypes, personal tools, learning — or tiny internal apps.',
    'anything customer-facing that must grow, stay up or be secured properly.',
    plain='One computer does everything: shows the screens, does the work and stores the data.',
    how=[('Install', 'Web server, app and database on one machine.'), ('Call locally', 'Code calls the database on localhost.'), ('Scale', 'Only vertically (bigger machine).'), ('Back up', 'The whole machine.'), ('Fail', 'Everything together.')],
    words=[('tier', 'a separately run part of an app'), ('localhost', 'the same machine'), ('LAMP', 'Linux, Apache, MySQL, PHP — a classic one-box stack')],
    diff=table(['', 'Single-tier', 'Three-tier'], [['Scale', 'bigger machine only', 'each tier separately'], ['Failure', 'all at once', 'contained per tier'], ['Security zones', 'one', 'separate subnets']], minw=420),
    where=['Prototypes and demos', 'Small internal tools', 'Desktop and mobile apps with local data'],
    realworld='Most start-ups begin single-tier — and many popular “one-click” WordPress images (Lightsail, marketplace VMs) are single-tier: web server and database on the same instance.',
    pro='A single-tier app can still be cloud-friendly: keep the database on a separate disk, take snapshots, and design the code so the database connection string can later point to a managed service — the first step to a two-tier split.')

def a2(k):
    o = t(180, 12, ['Client does UI + logic', 'Shared database server', 'Many clients, one DB'][k], 9, 'ink', bold=True)
    for i in range(3 if k == 2 else 1): o += box(20, 30 + i * 32, 110, 26, 'amber', rx=4) + t(75, 47 + i * 32, 'desktop app', 7, 'ink')
    if k >= 1: o += box(230, 50, 110, 50, 'violet', rx=8) + t(285, 72, 'database server', 7.4, 'ink', bold=True) + t(285, 88, 'SQL', 6.6, 'ink2') + arrow(132, 64, 228, 74)
    o += t(180, 132, ['the client program holds screens and business rules', 'it connects straight to a database over the network', 'every client needs DB credentials and an update when rules change'][k], 7.2, 'ink', bold=True)
    return o
A2 = cap([a2(k) for k in range(3)], [('Client', 'The client application contains the UI and the business logic.', ''), ('Database', 'It talks directly to a shared database server.', ''), ('Limits', 'Many clients hold DB connections and credentials; logic changes mean updating every client.', '')],
    'Two-tier in action', 'Client and database.', 'Two-tier', 'Animation: a desktop client with UI and logic; a shared database server; many clients connecting directly to it.', 't2anim')
T2 = vtype(2, 'Two-tier (client–server) architecture', 'amber',
    'A <b>two-tier architecture</b> splits an application into a <b>client</b> that contains the user interface (and often the business logic) and a <b>server</b> — usually a database — that the client connects to directly over the network.',
    'A grocery shop where every customer walks into the godown and picks items themselves: fine for a few regulars, chaos with hundreds — and every customer needs the godown key.',
    'TiffinGo’s kitchen used a desktop billing app connected straight to a MySQL server in the office. Moving the database to Amazon RDS made it managed — but every kitchen PC still held the database password.',
    'Desktop apps with a managed database (RDS, Azure SQL, Cloud SQL); Microsoft Access/Excel front ends; mobile apps using a backend-as-a-service database directly (with strict rules).',
    '', A2,
    'small internal apps with a few trusted users on a private network.',
    'clients run on the internet or untrusted devices — never expose a database directly to them.',
    plain='Each user’s computer runs the program, and all of them talk straight to one shared database.',
    how=[('Client', 'UI + business logic, installed on each machine.'), ('Connect', 'Direct database connection (SQL over TCP).'), ('Store', 'The database server keeps shared data.'), ('Update', 'New rules = new client version everywhere.'), ('Secure', 'Credentials live on every client — the weak point.')],
    words=[('client', 'the program the user runs'), ('server', 'the shared machine/service that answers clients'), ('connection pool', 'reused database connections')],
    diff=table(['', 'Two-tier', 'Three-tier'], [['Business logic', 'in each client', 'in the app tier (one place)'], ['DB exposed to clients', 'yes', 'no'], ['Rule change', 'update all clients', 'deploy once']], minw=440),
    where=['Legacy desktop business apps', 'Small office systems', 'Reporting tools connecting to warehouses'],
    realworld='Many Indian small-business accounting and billing systems were classic two-tier desktop apps; moving them to the cloud usually means adding an API tier rather than exposing the database to the internet.',
    pro='Backend-as-a-service databases (Firestore, Supabase, DynamoDB with Cognito) let mobile apps talk “directly” to a database safely only because security rules act as a thin application tier — the logic moved, it did not disappear.')

def a3(k):
    o = t(180, 12, ['Presentation tier', 'Application tier', 'Data tier'][k], 9, 'ink', bold=True)
    return o + tbox(['Presentation|web/CDN|public', 'Application|API, rules|private', 'Data|DB, cache|isolated'], ['green', 'blue', 'violet'], k,
                    ['shows pages; no business rules, no data', 'all business logic; stateless, scales out', 'stores data; only the app tier may connect'][k])
A3 = cap([a3(k) for k in range(3)], [('Presentation', 'Web pages, static files and the load balancer face users.', ''), ('Application', 'Business logic runs in a separate, private tier that can scale out.', ''), ('Data', 'Databases and storage sit in an isolated tier reachable only from the app tier.', '')],
    'Three-tier in action', 'Presentation, application, data.', 'Three-tier', 'Animation: presentation tier, application tier and data tier lighting up in turn with their responsibilities.', 't3anim')
T3 = vtype(3, 'Three-tier architecture', 'blue',
    'A <b>three-tier architecture</b> separates an application into a <b>presentation tier</b> (user interface), an <b>application (logic) tier</b> (business rules and processing) and a <b>data tier</b> (databases and storage), each running on its own infrastructure, communicating only with the adjacent tier, and scaled, secured and deployed independently.',
    'A restaurant: the dining hall and waiters (presentation), the kitchen (application) and the store room (data). Customers never walk into the store room.',
    'TiffinGo today: a React website on S3 + CloudFront, an order API on two app servers behind an ALB in private subnets, and PostgreSQL on RDS Multi-AZ in isolated subnets. At Diwali the app tier grows to 10 servers; the database just gets a read replica.',
    'AWS: CloudFront/S3 + ALB → EC2/ECS/Lambda → RDS/DynamoDB; Azure: Front Door/Static Web Apps → App Service/Container Apps → Azure SQL/Cosmos DB; Google: Cloud CDN/Cloud Storage → Cloud Run/GKE → Cloud SQL/Firestore.',
    '', A3,
    'almost any web or mobile application — it is the default cloud design.',
    'you put business rules in the front end or let the presentation tier query the database directly.',
    plain='Three separate layers: the screens users see, the brain that does the work, and the store where data is kept — each on its own machines.',
    how=[('Presentation', 'Static content via CDN; dynamic pages via web servers or a SPA.'), ('Application', 'Stateless API servers or functions; sessions in a cache/DB.'), ('Data', 'Managed database, cache and object storage.'), ('Connect', 'Each tier calls only the next one (LB, private DNS).'), ('Scale/secure per tier', 'Different subnets, firewall rules, scaling policies and teams.')],
    words=[('presentation tier', 'the part users see'), ('application tier', 'where business rules run'), ('data tier', 'where data is stored'), ('stateless', 'keeps no user data between requests')],
    diff=table(['', 'Three-tier', 'N-tier'], [['Tiers', 'web, app, data', 'adds cache, queues, workers, search, CDN…'], ['Complexity', 'moderate', 'higher'], ['Typical size', 'most apps', 'large platforms']], minw=420),
    where=['E-commerce and food-ordering apps', 'Banking portals', 'Most SaaS products'],
    realworld='The AWS “three-tier web architecture” reference (ALB, Auto Scaling app tier, Multi-AZ RDS across public, private and isolated subnets) is one of the most common designs in AWS whitepapers and the Solutions Architect exam.',
    pro='Keep the app tier <b>stateless</b>: store sessions in Redis/DynamoDB, not in server memory. Otherwise the load balancer needs sticky sessions, scale-in logs users out and an instance failure loses carts.')

def a4(k):
    o = t(180, 12, ['Add a cache tier', 'Add a queue + workers', 'Add search, CDN, analytics'][k], 9, 'ink', bold=True)
    items = ['web', 'API', 'cache', 'DB'] if k == 0 else (['API', 'queue', 'workers', 'DB'] if k == 1 else ['CDN', 'API', 'search', 'analytics'])
    return o + tbox(items, ['green', 'blue', 'amber', 'violet'], 3, ['frequent reads served from memory', 'slow jobs (SMS, invoices) run in the background', 'each specialised need gets its own tier'][k])
A4 = cap([a4(k) for k in range(3)], [('Cache', 'A cache tier absorbs repeated reads.', ''), ('Async', 'A queue and worker tier handle slow work outside the request.', ''), ('Specialise', 'Search, CDN and analytics tiers each do one job well.', '')],
    'N-tier in action', 'More tiers for more needs.', 'N-tier', 'Animation: adding a cache tier; a queue and worker tier; search, CDN and analytics tiers.', 't4anim')
T4 = vtype(4, 'N-tier architecture', 'violet',
    'An <b>n-tier architecture</b> extends the three-tier model with additional specialised tiers — such as caching, messaging/queues with background workers, search, content delivery and analytics — each running and scaling independently.',
    'A big hotel: reception, kitchen and store room — plus a laundry, a bakery and a delivery desk, each with its own staff.',
    'TiffinGo added a Redis cache (menus), an SQS queue with worker containers (SMS and invoice PDFs), OpenSearch (search dishes) and a nightly analytics pipeline — the order API stays fast because slow work happens elsewhere.',
    'ElastiCache, SQS/SNS + ECS workers, OpenSearch, CloudFront, Kinesis; Azure Managed Redis, Service Bus + Functions, AI Search, Front Door, Event Hubs; Memorystore, Pub/Sub + Cloud Run jobs, Vertex AI Search, Cloud CDN, BigQuery.',
    '', A4,
    'one tier is doing work it is bad at (search in SQL, slow jobs in requests, repeated reads).',
    'you add tiers before you need them — each one adds latency, cost and operations.',
    plain='The three-tier design plus extra specialist layers — like a fast memory store, a to-do queue for slow jobs, and a search engine.',
    how=[('Identify the bottleneck', 'Repeated reads? slow jobs? full-text search?'), ('Add a tier', 'Cache, queue+workers, search, CDN.'), ('Define contracts', 'APIs or messages between tiers.'), ('Scale separately', 'Each tier with its own metrics.'), ('Observe', 'Distributed tracing across tiers.')],
    words=[('cache', 'fast memory copy of frequently read data'), ('worker', 'a process that takes jobs from a queue'), ('asynchronous', 'done later, not while the user waits'), ('distributed tracing', 'following one request across many services')],
    diff=table(['', 'N-tier', 'Microservices (7.4)'], [['Split by', 'technical layer', 'business capability'], ['Each tier', 'shared by the whole app', 'each service has its own layers'], ['Deployment', 'often one app', 'independent services']], minw=440),
    where=['Large e-commerce sites', 'Media and news portals', 'SaaS platforms'],
    realworld='Stack Overflow famously served a huge site with a small n-tier setup (web servers, Redis, Elasticsearch, SQL Server) — proof that well-chosen tiers can scale far before microservices are needed.',
    pro='A cache tier changes failure behaviour: if Redis empties (restart, eviction), every request suddenly hits the database — a “cache stampede”. Request coalescing, staggered TTLs and warm-up scripts are part of the design.')

def a5(k):
    o = t(180, 12, ['Presentation: CDN + bucket', 'Logic: functions', 'Data: serverless DB'][k], 9, 'ink', bold=True)
    return o + tbox(['S3 + CloudFront|static SPA', 'API Gateway|+ Lambda', 'DynamoDB|on-demand'], ['green', 'blue', 'violet'], k,
                    ['no web servers; pay per GB served', 'code runs per request; scales to zero', 'pay per read/write; no servers to patch'][k])
A5 = cap([a5(k) for k in range(3)], [('Presentation', 'A static front end in object storage behind a CDN.', ''), ('Logic', 'API gateway + functions or serverless containers.', ''), ('Data', 'Serverless databases billed per request.', '')],
    'Serverless three-tier in action', 'Three tiers, no servers.', 'Serverless 3-tier', 'Animation: static front end in a bucket with CDN; API gateway and functions; serverless NoSQL database.', 't5anim')
T5 = vtype(5, 'Serverless three-tier', 'green',
    'A <b>serverless three-tier architecture</b> implements the same three tiers with fully managed, per-request services: a static front end in object storage behind a CDN, an application tier of API gateway plus functions or serverless containers, and a serverless or autoscaling data tier — with no servers to provision or patch.',
    'A cloud kitchen on an aggregator app: no dining hall, no permanent kitchen staff — space and cooks are paid per order.',
    'TiffinGo’s new “corporate lunch” portal: React app on S3 + CloudFront, API Gateway + Lambda for orders, DynamoDB on-demand for data. At night it costs almost nothing; on Monday 12:30 p.m. it scales with the rush.',
    'AWS: S3/CloudFront, API Gateway, Lambda, DynamoDB, Aurora Serverless v2; Azure: Static Web Apps, Functions, Cosmos DB serverless; Google: Firebase Hosting/Cloud Storage, Cloud Run/Cloud Run functions, Firestore.',
    '', A5,
    'spiky or unpredictable traffic, small teams, new products.',
    'steady very high load (VMs/containers with commitments may be cheaper) or long-running connections.',
    plain='The same three layers, but every layer is rented per use from the cloud — no servers to manage at all.',
    how=[('Build front end', 'SPA files uploaded to a bucket; CDN in front.'), ('Expose API', 'API Gateway routes to functions.'), ('Store data', 'Serverless DB with on-demand capacity.'), ('Authenticate', 'Cognito / Entra External ID / Identity Platform tokens.'), ('Scale', 'Each tier scales per request automatically.')],
    words=[('SPA', 'single-page application — the browser runs the UI'), ('API gateway', 'a managed front door for APIs'), ('on-demand capacity', 'pay per request, no sizing')],
    diff=table(['', 'Serverless 3-tier', 'VM-based 3-tier'], [['Idle cost', '≈ 0', 'servers running'], ['Ops work', 'minimal', 'patching, scaling'], ['Limits', 'timeouts, cold starts', 'few']], minw=420),
    where=['Start-up MVPs', 'Event and campaign sites', 'Internal tools with spiky use'],
    realworld='AWS’s Serverless Application Lens of the Well-Architected Framework uses exactly this pattern (S3/CloudFront + API Gateway + Lambda + DynamoDB) as its reference web application.',
    pro='The weakest link in serverless three-tier is often the database connection: hundreds of concurrent functions can exhaust a relational database’s connections — use RDS Proxy / connection pooling or a serverless-native database.')

def a6(k):
    o = t(180, 12, ['Build once, serve from the edge', 'Browser runs the UI', 'Calls APIs for data'][k], 9, 'ink', bold=True)
    return o + tbox(['build|HTML/JS/CSS', 'CDN edge|cached', 'browser|+ API calls'], ['amber', 'green', 'blue'], k,
                    ['pages are pre-built at deploy time', 'served like photos — fast and cheap everywhere', 'dynamic data comes from APIs (tier 2)'][k])
A6 = cap([a6(k) for k in range(3)], [('Build', 'The site is pre-built into static files at deploy time.', ''), ('Serve', 'Files are served from a CDN — no web servers.', ''), ('Fetch', 'The browser calls APIs for dynamic data.', '')],
    'Static front end + API in action', 'Pre-built pages, live data.', 'Static + API', 'Animation: build static files; serve them from a CDN; browser calls APIs for data.', 't6anim')
T6 = vtype(6, 'Static front end + API (SPA / JAMstack)', 'green',
    'A <b>static front end with APIs</b> (single-page application or JAMstack) delivers the presentation tier as pre-built static files — HTML, JavaScript, CSS — from object storage and a CDN, while all dynamic behaviour comes from the browser calling back-end APIs; there are no web servers in the presentation tier.',
    'A printed menu card handed out everywhere (static), with a phone number to call for today’s specials (API).',
    'TiffinGo’s marketing site and menu pages are built by the CI pipeline and deployed to a bucket behind CloudFront; the “Order now” button calls the order API. A traffic spike from a TV ad hit only the CDN.',
    'S3 static website + CloudFront, AWS Amplify Hosting; Azure Static Web Apps, Blob static website + Front Door; Firebase Hosting, Cloud Storage + Cloud CDN.',
    '', A6,
    'marketing sites, documentation, dashboards and app front ends.',
    'pages need server-side rendering for every request with secret data — use server-side frameworks or edge functions.',
    plain='The website is a set of ready-made files delivered by a fast worldwide network; anything live (like today’s menu or your cart) is fetched separately from the server.',
    how=[('Build', 'A framework (React, Next.js export, Hugo) creates static files.'), ('Upload', 'To a bucket/static host in the pipeline.'), ('Cache', 'CDN caches files worldwide; versioned file names.'), ('Call APIs', 'Browser JavaScript calls the API tier with tokens.'), ('Invalidate', 'New deploy → CDN cache invalidation or new file names.')],
    words=[('static file', 'a file that is the same for every visitor'), ('JAMstack', 'JavaScript, APIs and Markup — pre-built front ends'), ('cache invalidation', 'telling the CDN to fetch a new version')],
    diff=table(['', 'Static front end', 'Server-rendered pages'], [['Web servers', 'none', 'needed'], ['Cost at spikes', 'CDN only', 'servers must scale'], ['Personalised HTML', 'via APIs in browser', 'built per request']], minw=440),
    where=['Marketing and documentation sites', 'Single-page web apps', 'Dashboards'],
    realworld='This very site, MyPhatshala, is a static site: lessons are pre-built HTML pages — the same pattern that lets static sites survive traffic spikes cheaply.',
    pro='S3’s “static website hosting” endpoint is HTTP-only and needs a public bucket; the recommended production setup is a private bucket served only through CloudFront with Origin Access Control (OAC) and HTTPS.')

def a7(k):
    o = t(180, 12, ['Separate subnets per tier', 'Firewall rules chain tiers', 'Separate identities'][k], 9, 'ink', bold=True)
    labels = [['public|LB only', 'private|app', 'isolated|DB'], ['443 from internet', '8080 from LB SG', '5432 from app SG'], ['web role|read static', 'app role|DB read/write', 'DB|no internet']][k]
    return o + tbox(labels, ['green', 'blue', 'violet'], 2, ['the data subnet has no route to the internet', 'each tier accepts traffic only from the tier before it', 'each tier’s code gets only the permissions it needs'][k])
A7 = cap([a7(k) for k in range(3)], [('Subnets', 'Public, private and isolated subnets per tier (Lesson 6.3).', ''), ('Rules', 'Security groups reference the previous tier’s group.', ''), ('Identities', 'Least-privilege roles per tier.', '')],
    'Tier isolation in action', 'Defence in depth between tiers.', 'Tier isolation', 'Animation: public, private and isolated subnets; firewall rules allowing only the previous tier; separate least-privilege roles.', 't7anim')
T7 = vtype(7, 'Tier isolation (network and identity)', 'red',
    '<b>Tier isolation</b> enforces the separation between tiers with infrastructure: separate subnets (public, private, isolated), firewall rules that allow each tier to be reached only from the previous tier, separate least-privilege identities per tier, and no direct internet path to the data tier.',
    'A bank branch: customers stay in the banking hall, cashiers work behind glass, and the vault opens only for the manager with two keys.',
    'TiffinGo’s ALB security group allows 443 from anywhere; the app security group allows 8080 only from the ALB group; the DB group allows 5432 only from the app group. The app’s IAM role can read/write the orders table but cannot delete it.',
    'VPC subnets, security groups, NACLs, IAM roles, VPC endpoints; Azure subnets, NSGs/ASGs, managed identities, private endpoints; Google subnets, firewall rules with service accounts, Private Service Connect.',
    'Lesson 6.3 covers the network building blocks.', A7,
    'always — tiers without isolation are only boxes on a diagram.',
    'you open the database to 0.0.0.0/0 “temporarily” for a migration — those rules are rarely closed.',
    plain='Putting walls between the layers: each layer may only talk to the one next to it, and the data layer is completely hidden from the internet.',
    how=[('Subnets', 'Public (LB), private (app), isolated (DB, no NAT route).'), ('Firewall chain', 'SG/NSG rules reference the previous tier’s group or service account.'), ('Identity', 'Separate roles; data access only from the app role.'), ('Private access', 'Endpoints for S3/KMS so the app tier needs no internet.'), ('Monitor', 'Flow logs show any unexpected cross-tier traffic.')],
    words=[('isolated subnet', 'a subnet with no route to or from the internet'), ('defence in depth', 'several protective layers'), ('managed identity', 'an automatic identity for an Azure resource')],
    diff=table(['', 'Logical tiers only', 'Isolated tiers'], [['Database reachable from internet', 'possibly', 'never'], ['Breach of web tier exposes', 'everything', 'only what the next rule allows']], minw=440),
    where=['Every production multi-tier app', 'PCI DSS and banking workloads', 'Healthcare data'],
    realworld='PCI DSS, the card-payment security standard, requires network segmentation that separates the cardholder-data environment — in the cloud this is implemented with exactly these subnet, firewall and identity boundaries.',
    pro='Security-group chaining also documents the architecture: reading the rules (“app accepts from alb-sg”) tells an auditor the real data flow — keep them precise and you get a living diagram.')

SUMMARY = table(['#', 'Architecture', 'Tiers', 'Scales by', 'Best for'], [
    ['1', 'Single-tier', '1', 'bigger machine', 'prototypes'], ['2', 'Two-tier', 'client + DB', 'bigger DB', 'small internal apps'], ['3', 'Three-tier', 'web · app · data', 'each tier', 'most apps'],
    ['4', 'N-tier', '3 + cache, queue, search…', 'each tier', 'large apps'], ['5', 'Serverless three-tier', 'CDN · functions · NoSQL', 'per request', 'spiky / new apps'], ['6', 'Static front end + API', 'CDN + API', 'CDN + API tier', 'sites, SPAs'], ['7', 'Tier isolation', '(how tiers are walled)', '—', 'every production app']], minw=620)
CHECK = ('  <h3>Check yourself: which architecture?</h3>\n' +
    qx('A. A hackathon demo used by 5 people for two days.', ['Single-tier', 'N-tier', 'Active/active', 'Microservices'], 0, 'Simplest.') +
    qx('B. A food-ordering app expecting Diwali spikes and needing a private database.', ['Two-tier', 'Three-tier with isolated data tier', 'Single-tier', 'Static only'], 1, 'Default cloud design.') +
    qx('C. Sending order SMS slows the checkout API.', ['Bigger DB', 'Add a queue + worker tier', 'Single-tier', 'Remove the CDN'], 1, 'N-tier async.') +
    qx('D. A marketing site that must survive a TV-ad traffic spike cheaply.', ['VM web servers', 'Static front end on a CDN', 'Two-tier', 'Bare metal'], 1, 'Static + CDN.'))

TYPES = ('  <p>Seven tiered architectures, each in the same pattern: definition, plain words, analogy, internal steps, animation, differences, where used, real-world example, TiffinGo scenario and an expert note.</p>\n'
         + challenge(['Why do sticky sessions make scaling in painful?', 'What is a cache stampede and why does a cache tier cause it?', 'Why can serverless functions exhaust a relational database?'], 'types 3, 4 and 5') + MAP
         + jump(['1-tier', '2-tier', '3-tier', 'N-tier', 'Serverless', 'Static + API', 'Isolation']) + T1 + T2 + T3 + T4 + T5 + T6 + T7
         + '\n  <h3 style="margin-top:34px">All seven side by side</h3>\n' + SUMMARY + '\n' + CHECK)

parts = wwu([
    ('Layer vs tier', 'Layer = logical code organisation; tier = separately deployed physical/runtime unit.', 'Interview favourite: a 3-layer app can still be 1-tier.', 'MVC layers inside one server vs three tiers on three subnets.'),
    ('Load balancer', 'Front door of the presentation or app tier.', 'Spreads load, checks health.', 'ALB, Application Gateway, Cloud LB.'),
    ('Session store', 'Where user sessions live outside servers.', 'Keeps the app tier stateless.', 'Redis, DynamoDB, Cosmos DB, Firestore.'),
    ('Connection pool / proxy', 'Reuses database connections.', 'Protects the data tier from connection storms.', 'RDS Proxy, PgBouncer, Cloud SQL connector.'),
    ('API contract', 'The agreed request/response format between tiers.', 'Lets tiers change independently.', 'OpenAPI specs, versioned APIs.'),
    ('Isolated subnet', 'Subnet with no internet route.', 'Home of the data tier.', 'DB subnets in every VPC design.')])

DEEP = ('  <h3>Layers vs tiers (often confused)</h3>\n  <p><b>Layers</b> are how code is organised (presentation layer, business layer, data-access layer — e.g. MVC). <b>Tiers</b> are where parts run. A Django app with three layers on one VM is <i>three-layer, one-tier</i>. Splitting the database onto RDS makes it two-tier; adding a separate API service makes it three-tier.</p>\n'
    '  <h3>Latency budget across tiers</h3>\n' + table(['Hop', 'Typical time'], [['Browser → CDN edge (India)', '10–30 ms'], ['Edge → load balancer (same Region)', '5–20 ms'], ['LB → app (same AZ)', '< 1 ms'], ['App → cache', '≈ 0.5 ms'], ['App → database query', '2–20 ms'], ['App → another Region', '20–60 ms']], minw=420) +
    '\n  <p>Every tier adds hops; keep chatty calls inside one AZ, cache aggressively and avoid cross-Region calls in the request path.</p>\n'
    '  <h3>The 12-factor app</h3>\n  <p>The <b>12-factor</b> principles (config in environment, stateless processes, backing services as attached resources, disposable processes…) describe how to write app-tier code that scales cleanly in any cloud tier design.</p>')

clouds = vendor_tabs('<p><b>AWS:</b> CloudFront + S3 (presentation), ALB + EC2 Auto Scaling / ECS / Lambda (application), RDS/Aurora, DynamoDB, ElastiCache (data); public/private/isolated subnets; RDS Proxy.</p>',
    '<p><b>Azure:</b> Front Door + Static Web Apps / Blob (presentation), Application Gateway + App Service / Container Apps / Functions (application), Azure SQL, Cosmos DB, Azure Managed Redis (data); subnets, NSGs, private endpoints.</p>',
    '<p><b>Google Cloud:</b> Cloud CDN + Cloud Storage / Firebase Hosting (presentation), Cloud Load Balancing + Cloud Run / GKE / Cloud Run functions (application), Cloud SQL, Firestore, Memorystore (data); subnets, firewall rules, Private Service Connect.</p>') + \
    cloud3([['Static front end', 'S3 + CloudFront / Amplify', 'Static Web Apps', 'Firebase Hosting / Cloud Storage + CDN'], ['App tier', 'EC2 ASG, ECS, Lambda', 'App Service, Container Apps, Functions', 'Cloud Run, GKE, Cloud Run functions'], ['Relational data tier', 'RDS / Aurora', 'Azure SQL', 'Cloud SQL / AlloyDB'], ['NoSQL data tier', 'DynamoDB', 'Cosmos DB', 'Firestore'], ['Cache tier', 'ElastiCache', 'Azure Managed Redis', 'Memorystore']])

# ------------------------------------------------------------------ practical
INDEX = '<!doctype html><title>TiffinGo</title><h1>TiffinGo menu</h1><p>Today: thali ₹249</p>'
LAMBDA = "import json, boto3\ntable = boto3.resource('dynamodb').Table('tiffingo-menu')\ndef lambda_handler(event, context):\n    items = table.scan()['Items']\n    return {'statusCode': 200, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps(items, default=str)}"
MAIN_PY = "import functions_framework, json\n@functions_framework.http\ndef menu(request):\n    return (json.dumps([{'dish': 'thali', 'price': 249}]), 200, {'Content-Type': 'application/json'})"

MOCKQ.extend([
 (mock('aws', ['Amazon S3', 'tiffingo-web-…', 'Properties'], ['Objects', 'Properties', 'Permissions', 'Management'], 'Properties',
       [('Static website hosting', '( ) Enable'), ('Hosting type', '( ) Host a static website'), ('Index document', 'index.html'), ('Then Permissions →', 'Block public access: Off · bucket policy: s3:GetObject for *')], 'Save changes'),
  mock('az', ['Home', 'tiffingo…', 'Static website'], ['Overview', 'Containers', 'Static website', 'Data protection'], 'Static website',
       [('Static website', '( ) Enabled'), ('Index document name', 'index.html'), ('Primary endpoint', 'https://tiffingo….z29.web.core.windows.net/')], 'Save'),
  mock('gcp', ['Cloud Storage', 'tiffingo-web-…', 'Edit website configuration'], ['Objects', 'Configuration', 'Permissions'], 'Configuration',
       [('Index (main) page suffix', 'index.html'), ('Permissions', 'allUsers → Storage Object Viewer')], 'Save')),
 (mock('aws', ['DynamoDB', 'Tables', 'Create table'], ['Dashboard', 'Tables', 'Explore items', 'PartiQL editor'], 'Tables',
       [('Table name', 'tiffingo-menu'), ('Partition key', 'dish (String)'), ('Table settings', '( ) Customize — Capacity mode: On-demand')], 'Create table'),
  mock('az', ['Home', 'tiffingo…', 'Storage browser', 'Tables'], ['Blob containers', 'File shares', 'Queues', 'Tables'], 'Tables',
       [('Table name', 'menu'), ('Add entity', 'PartitionKey=pune · RowKey=thali · price=249')], 'Insert'),
  mock('gcp', ['Firestore', 'Databases', 'Create database'], ['Databases', 'Data', 'Indexes', 'Rules'], 'Databases',
       [('Database ID', '(default)'), ('Edition · Mode', 'Standard · Native mode'), ('Location', '▾ asia-south1 (Mumbai)')], 'Create database')),
 (mock('aws', ['Lambda', 'Functions', 'tiffingo-menu-api'], ['Code', 'Test', 'Monitor', 'Configuration', 'Aliases'], 'Configuration',
       [('Function URL', '( ) Create function URL'), ('Auth type', '( ) NONE'), ('Permissions → Execution role', 'add AmazonDynamoDBReadOnlyAccess')], 'Save'),
  mock('az', ['Home', 'Function App', 'Create'], ['Basics', 'Storage', 'Networking', 'Monitoring', 'Deployment', 'Review + create'], 'Basics',
       [('Hosting plan', '( ) Flex Consumption'), ('Function App name', 'tiffingo-api-1234'), ('Runtime stack · Version', '▾ Python · 3.12'), ('Region', '▾ Central India')], 'Review + create'),
  mock('gcp', ['Cloud Run', 'Write a function'], ['Services', 'Jobs', 'Functions'], 'Services',
       [('Service name', 'tiffingo-menu-api'), ('Region · Runtime', 'asia-south1 · Python 3.12'), ('Authentication', '( ) Allow public access'), ('Entry point', 'menu')], 'Create')),
])

STEP1 = ('1 · Presentation tier: a static website', tri(
    (['[[S3]] → [[Create bucket]] <code>tiffingo-web-&lt;yourname&gt;</code> (Mumbai). Untick [[Block all public access]] for <i>this lab bucket only</i> and acknowledge.', 'Upload an <code>index.html</code>. [[Properties]] → [[Static website hosting]] → [[Enable]], index document index.html → [[Save changes]].', '[[Permissions]] → [[Bucket policy]]: allow <code>s3:GetObject</code> on <code>arn:aws:s3:::BUCKET/*</code> for Principal <code>*</code> → open the [[Bucket website endpoint]].'],
     f"W=tiffingo-web-$RANDOM$RANDOM\necho '{INDEX}' > index.html\naws s3 mb s3://$W --region ap-south-1\naws s3api put-public-access-block --bucket $W --public-access-block-configuration BlockPublicPolicy=false,RestrictPublicBuckets=false,BlockPublicAcls=true,IgnorePublicAcls=true\naws s3api put-bucket-policy --bucket $W --policy \"{{\\\"Version\\\":\\\"2012-10-17\\\",\\\"Statement\\\":[{{\\\"Effect\\\":\\\"Allow\\\",\\\"Principal\\\":\\\"*\\\",\\\"Action\\\":\\\"s3:GetObject\\\",\\\"Resource\\\":\\\"arn:aws:s3:::$W/*\\\"}}]}}\"\naws s3 website s3://$W --index-document index.html\naws s3 cp index.html s3://$W/ --content-type text/html\ncurl http://$W.s3-website.ap-south-1.amazonaws.com",
     'your HTML from the <code>s3-website</code> endpoint. In production keep the bucket private and serve it through CloudFront with Origin Access Control instead (HTTPS).'),
    (['Use the storage account from Lesson 6.2 (or create one) → [[Data management]] → [[Static website]] → [[Enabled]], index <code>index.html</code> → [[Save]].', 'A container named <code>$web</code> appears → upload index.html into it → open the [[Primary endpoint]].'],
     f"echo '{INDEX}' > index.html\naz storage blob service-properties update --account-name $SA --static-website --index-document index.html --auth-mode key\naz storage blob upload --account-name $SA --container-name '$web' --name index.html --file index.html --content-type text/html --overwrite --auth-mode key\naz storage account show --name $SA --query primaryEndpoints.web --output tsv",
     'an HTTPS URL like <code>https://tiffingo1234.z29.web.core.windows.net/</code> showing your page.'),
    (['[[Cloud Storage]] → [[Create bucket]] <code>tiffingo-web-&lt;yourname&gt;</code>, asia-south1, untick [[Enforce public access prevention]], uniform access.', 'Upload index.html. [[Permissions]] → [[Grant access]] → principal <code>allUsers</code>, role [[Storage Object Viewer]].', 'Open <code>https://storage.googleapis.com/BUCKET/index.html</code>.'],
     f"W=tiffingo-web-$RANDOM$RANDOM\necho '{INDEX}' > index.html\ngcloud storage buckets create gs://$W --location=asia-south1 --uniform-bucket-level-access\ngcloud storage cp index.html gs://$W/\ngcloud storage buckets add-iam-policy-binding gs://$W --member=allUsers --role=roles/storage.objectViewer\ngcloud storage buckets update gs://$W --web-main-page-suffix=index.html\ncurl https://storage.googleapis.com/$W/index.html",
     'your HTML over HTTPS. If public access is blocked by an organisation policy, ask the admin or keep the bucket private and use a load balancer + Cloud CDN.')),
    'The presentation tier has no servers at all — just files on a CDN-ready store.')

STEP2 = ('2 · Data tier: a serverless table', tri(
    (['[[DynamoDB]] → [[Create table]] → name <code>tiffingo-menu</code>, partition key <code>dish</code> (String), [[On-demand]] capacity → [[Create table]].', '[[Explore items]] → [[Create item]] → dish = thali, add attribute price (Number) = 249 → [[Create item]].'],
     "aws dynamodb create-table --table-name tiffingo-menu --attribute-definitions AttributeName=dish,AttributeType=S \\\n  --key-schema AttributeName=dish,KeyType=HASH --billing-mode PAY_PER_REQUEST\naws dynamodb wait table-exists --table-name tiffingo-menu\naws dynamodb put-item --table-name tiffingo-menu --item '{\"dish\":{\"S\":\"thali\"},\"price\":{\"N\":\"249\"}}'\naws dynamodb scan --table-name tiffingo-menu --query 'Items'",
     'one item with dish thali and price 249. On-demand tables cost nothing when idle (pay per request; 25 GB storage free tier).'),
    (['Storage account → [[Storage browser]] → [[Tables]] → [[Add table]] <code>menu</code>.', 'Open it → [[Add entity]] → PartitionKey <code>pune</code>, RowKey <code>thali</code>, add property price (Int32) 249 → [[Insert]]. (Cosmos DB is the bigger NoSQL option; Table storage is enough here.)'],
     "az storage table create --account-name $SA --name menu --auth-mode key\naz storage entity insert --account-name $SA --table-name menu --auth-mode key \\\n  --entity PartitionKey=pune RowKey=thali price=249 price@odata.type=Edm.Int32\naz storage entity query --account-name $SA --table-name menu --auth-mode key --output table",
     'one entity with PartitionKey pune, RowKey thali, price 249.'),
    (['[[Firestore]] → [[Create database]] → (default), Native mode, location asia-south1 → [[Create database]].', '[[Data]] → [[Start collection]] <code>menu</code> → document ID <code>thali</code> → field price (number) 249 → [[Save]].', 'gcloud has no command to write documents — use the console or a client library.'],
     'gcloud services enable firestore.googleapis.com\ngcloud firestore databases create --location=asia-south1 --type=firestore-native\ngcloud firestore databases list --format="table(name,locationId,type)"',
     'the (default) database in asia-south1, then your document in the console.')),
    'The data tier is a managed service — no server, no OS, nothing reachable except through its API and permissions.')

STEP3 = ('3 · Application tier: an HTTPS API', tri(
    (['[[Lambda]] → [[Create function]] → [[Author from scratch]] → name <code>tiffingo-menu-api</code>, runtime Python 3.12 → [[Create function]].', 'Paste the code on the right into <code>lambda_function.py</code> → [[Deploy]]. [[Configuration]] → [[Permissions]] → open the role → [[Add permissions]] → AmazonDynamoDBReadOnlyAccess.', '[[Configuration]] → [[Function URL]] → [[Create function URL]] → auth type [[NONE]] → [[Save]] → open the URL.'],
     f"cat > lambda_function.py <<'EOF'\n{LAMBDA}\nEOF\nzip fn.zip lambda_function.py\naws iam create-role --role-name tiffingo-menu-role --assume-role-policy-document \\\n  '{{\"Version\":\"2012-10-17\",\"Statement\":[{{\"Effect\":\"Allow\",\"Principal\":{{\"Service\":\"lambda.amazonaws.com\"}},\"Action\":\"sts:AssumeRole\"}}]}}'\naws iam attach-role-policy --role-name tiffingo-menu-role --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole\naws iam attach-role-policy --role-name tiffingo-menu-role --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBReadOnlyAccess\nsleep 15\nACCT=$(aws sts get-caller-identity --query Account --output text)\naws lambda create-function --function-name tiffingo-menu-api --runtime python3.12 --handler lambda_function.lambda_handler \\\n  --zip-file fileb://fn.zip --role arn:aws:iam::$ACCT:role/tiffingo-menu-role\naws lambda wait function-active --function-name tiffingo-menu-api\nURL=$(aws lambda create-function-url-config --function-name tiffingo-menu-api --auth-type NONE --query FunctionUrl --output text)\naws lambda add-permission --function-name tiffingo-menu-api --statement-id url --action lambda:InvokeFunctionUrl \\\n  --principal '*' --function-url-auth-type NONE\naws lambda add-permission --function-name tiffingo-menu-api --statement-id invoke --action lambda:InvokeFunction --principal '*'\ncurl $URL",
     '<code>[{\"dish\": \"thali\", \"price\": \"249\"}]</code> — read live from the data tier. A complete three-tier app: S3 site → Lambda API → DynamoDB.'),
    (['[[Function App]] → [[Create]] → [[Flex Consumption]] → name <code>tiffingo-api-&lt;n&gt;</code>, Python 3.12, Central India, storage account from step 1 → [[Review + create]].', 'In Cloud Shell create the code with Core Tools (commands on the right) and publish.', 'Open <code>https://APP.azurewebsites.net/api/menu</code>.'],
     'APP=tiffingo-api-$RANDOM\naz functionapp create --resource-group rg-tiffingo --name $APP --storage-account $SA \\\n  --flexconsumption-location centralindia --runtime python --runtime-version 3.12\nfunc init tiffingo-api --python && cd tiffingo-api\nfunc new --name menu --template "HTTP trigger" --authlevel anonymous\nfunc azure functionapp publish $APP\ncurl "https://$APP.azurewebsites.net/api/menu?name=TiffinGo"',
     '“Hello, TiffinGo. This HTTP triggered function executed successfully.” Reading the table needs the <code>azure-data-tables</code> library and an app setting — the same idea as the AWS code.'),
    (['[[Cloud Run]] → [[Write a function]] → name <code>tiffingo-menu-api</code>, asia-south1, Python 3.12, [[Allow public access]].', 'Replace <code>main.py</code> with the code on the right, entry point <code>menu</code> → [[Save and redeploy]] → open the URL.'],
     f"mkdir menu && cd menu\ncat > main.py <<'EOF'\n{MAIN_PY}\nEOF\necho 'functions-framework==3.*' > requirements.txt\ngcloud functions deploy tiffingo-menu-api --gen2 --region=asia-south1 --runtime=python312 \\\n  --source=. --entry-point=menu --trigger-http --allow-unauthenticated\ncurl $(gcloud functions describe tiffingo-menu-api --region=asia-south1 --format='value(url)')",
     '<code>[{\"dish\": \"thali\", \"price\": 249}]</code>. Reading Firestore needs the <code>google-cloud-firestore</code> library — same pattern.')),
    'Three tiers, three services, zero servers to patch: static site → function → serverless table.')

prac = practical(OWN_INTRO + ' Everything here is serverless and idle-free; with clean-up the cost is zero or a few paise.', [SETUP_STEP, STEP1, STEP2, STEP3],
    cleanup='<b>AWS:</b> <code>aws lambda delete-function --function-name tiffingo-menu-api; aws iam detach-role-policy --role-name tiffingo-menu-role --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole; aws iam detach-role-policy --role-name tiffingo-menu-role --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBReadOnlyAccess; aws iam delete-role --role-name tiffingo-menu-role; aws dynamodb delete-table --table-name tiffingo-menu; aws s3 rb s3://$W --force</code>.<br>'
            '<b>Azure:</b> <code>az group delete --name rg-tiffingo --yes --no-wait</code>.<br>'
            '<b>Google Cloud:</b> <code>gcloud functions delete tiffingo-menu-api --region=asia-south1 --quiet; gcloud storage rm --recursive gs://$W; gcloud firestore databases delete --database="(default)" --quiet</code> (or keep the free-tier Firestore database).')

mist = mistakes([
    ['Database reachable from the internet.', 'Easier to connect from a laptop.', 'Isolated subnet; connect via bastion/Session Manager or VPN.'],
    ['Business logic in the front end.', 'Faster to build.', 'Rules in the app tier; the browser is untrusted.'],
    ['Sessions stored in app server memory.', 'Framework default.', 'External session store; stateless app tier.'],
    ['Public S3 website buckets in production.', 'Tutorial shortcut.', 'Private bucket + CloudFront OAC + HTTPS.'],
    ['Too many tiers too early.', 'Copying big companies.', 'Add tiers when a bottleneck appears.'],
    ['Functions opening a new DB connection per request.', 'Simple code.', 'Connection reuse, RDS Proxy, or serverless databases.']])

cert = table(['Exam / syllabus', 'What is asked'], [['C-DAC PGCP-BDA', 'Multi-tier architecture of cloud applications.'], ['AWS CLF-C02', 'Services for each tier (CloudFront/S3, ELB/EC2/Lambda, RDS/DynamoDB), public vs private subnets, decoupling.'], ['AZ-900', 'App Service, Functions, Static Web Apps, Azure SQL/Cosmos DB, VNets and NSGs.'], ['Google Cloud Digital Leader', 'Modernising apps: Cloud Run, Firestore, Cloud SQL, managed services by tier.']], minw=560) + \
    qx('1. In a three-tier architecture, business rules belong in the…', ['presentation tier', 'application tier', 'data tier', 'CDN'], 1, 'Logic tier.') + \
    qx('2. Where should the database of a three-tier app be placed?', ['public subnet', 'private/isolated subnet', 'CDN', 'the browser'], 1, 'No internet path.') + \
    qx('3. Which AWS services form a serverless three-tier app?', ['EC2 + RDS + ALB', 'S3/CloudFront + API Gateway/Lambda + DynamoDB', 'EBS + EFS + FSx', 'VPN + Direct Connect'], 1, 'Serverless tiers.') + \
    qx('4. Which Azure service hosts static web front ends with integrated APIs?', ['Azure Static Web Apps', 'Azure Batch', 'Azure Arc', 'ExpressRoute'], 0, 'Static Web Apps.') + \
    qx('5. A three-layer app running on one server is…', ['three-tier', 'single-tier', 'n-tier', 'serverless'], 1, 'Layers ≠ tiers.') + \
    qx('6. Which tier is usually added to absorb repeated reads?', ['cache', 'CDN for writes', 'VPN', 'queue'], 0, 'Cache tier.')

proj = miniproject('Mini project: TiffinGo three-tier, end to end',
    'Build and document a real three-tier app.',
    ['<b>Draw</b> the three tiers with subnets/services for your chosen cloud.',
     '<b>Build</b> the static site, the table and the API on your own account (steps 1–3).',
     '<b>Connect</b> the page to the API: add a small JavaScript <code>fetch()</code> that shows the menu from the API (enable CORS on the function URL / function).',
     '<b>Secure</b> it: list what would change for production (private bucket + CDN, auth on the API, least-privilege role).',
     '<b>Scale story:</b> write how each tier scales at Diwali.',
     '<b>Clean up</b>.'],
    'A working page that shows data from your database through your API — and a production hardening list.', 'This lesson + 6.1–6.3.')

assemble_v2(HERE, story_h2='The server that did everything', hook_html=hk,
    narration='TiffinGo’s first server did everything — web, logic and database. On Diwali the database took all the memory and the whole site went down. Splitting the jobs into tiers fixed it.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Multi-tier architecture',
    formal='A <b>multi-tier (n-tier) architecture</b> divides an application into physically separate tiers — typically a <b>presentation tier</b>, an <b>application (business logic) tier</b> and a <b>data tier</b> — each running on its own infrastructure, communicating through defined interfaces with only adjacent tiers, so that each can be developed, scaled, secured and maintained independently.',
    simple='Split the app into layers that run separately: the screens, the brain and the storage — so each can grow and be protected on its own.',
    interview=['“A three-tier app has presentation, application and data tiers. In AWS: CloudFront/S3 or an ALB in public subnets, app servers or Lambda in private subnets, and RDS or DynamoDB in isolated subnets reachable only from the app tier.”', '“Tiers scale independently, contain failures and allow defence in depth; n-tier adds caches, queues and workers.”'],
    terms_rows=[('Tier', 'Separately run part.'), ('Layer', 'Logical code part.'), ('Presentation tier', 'UI, static files, LB.'), ('Application tier', 'Business logic.'), ('Data tier', 'Databases, storage.'), ('Stateless', 'No local user state.'), ('Session store', 'External session data.'), ('SPA', 'Browser-run front end.'), ('Isolated subnet', 'No internet path.'), ('Connection pooling', 'Reuse DB connections.')],
    exam='Expect “which service for which tier”, public vs private subnets, and serverless equivalents in all three clouds.',
    picture_h2='The three tiers, and how architectures grew into them', picture_html=picture,
    after_picture=[('types', 'Types, one by one', 'Seven tiered architectures, one by one', TYPES)],
    how_h2='One request through three tiers', how_intro='Watch a menu request flow through each tier.', how_anim=FLOW,
    parts_h2='Six ideas that make tiers work', parts_html=parts, lv='',
    myth_rows=[('Layers and tiers are the same.', 'Layers are code; tiers are deployment.', 'Deep dive.'), ('More tiers is always better.', 'Each tier adds latency and operations.', 'Type 4.'), ('Serverless has no tiers.', 'It has the same three tiers, managed.', 'Type 5.')],
    extra_secs=[('deep', 'Deep dive', 'Layers vs tiers, latency budget, 12-factor apps', DEEP)],
    clouds_html=clouds, practical_html=prac, mistakes_html=mist, cert_html=cert, project_html=proj,
    can_now=['Explain 1-, 2-, 3- and n-tier architectures and when to use each.', 'Place cloud services into presentation, application and data tiers.', 'Isolate tiers with subnets, firewall rules and roles.', 'Explain serverless and static-front-end variants.', 'Build a three-tier serverless app on your own account.'],
    next_html='<a href="../04-monolith-vs-microservices-vs-serverless/">7.4 Monolith vs microservices vs serverless</a>.',
    pre='<b>Before you start:</b> <a href="../../06-cloud-building-blocks/03-cloud-networking/">6.3 Networking</a> and <a href="../02-scalability-availability-and-fault-tolerance/">7.2</a>.')
