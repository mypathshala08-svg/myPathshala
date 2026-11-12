import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
def cap(frames, steps, title, intro, panel, aria, hid, delay=5500):
    return anim_one('Animated', title, intro, panel, aria, cap_frames(frames, steps), [s[0] + '.' for s in steps], delay=delay, hid=hid)


hk = hook('TiffinGo has 25 developers working in one big codebase. A one-line change to the SMS text needs a full release of the whole app — and last week it broke payments. Should they split everything into 40 microservices tomorrow?',
    'Probably not. A <b>monolith</b> is one deployable application; <b>microservices</b> are many small services, each owning one business capability and its data; <b>serverless</b> builds the app from managed services and functions that run on events. Each style trades simplicity against independence and scale — and most successful companies move <i>gradually</i>. This lesson explains seven architecture styles from monolith to event-driven, shows how one order flows through microservices, and on <b>your own</b> account you wire services together with events — the glue that makes microservices and serverless work.',
    ['Monolith, modular monolith, SOA, microservices, serverless, event-driven — what really differs.', 'Why many teams go back to a modular monolith.', 'Wire services with events without writing code.'])

def story_scene():
    o = t(180, 12, 'One codebase, 25 developers', 9, 'ink', bold=True)
    o += box(14, 26, 130, 82, 'red', rx=8) + t(79, 46, 'monolith', 8.4, 'ink', bold=True) + t(79, 64, 'orders · payments', 6.8, 'ink') + t(79, 78, 'SMS · menu · kitchen', 6.8, 'ink') + t(79, 96, 'one release for all', 6.8, 'ink2')
    o += arrow(148, 66, 170, 66) + t(159, 58, '?', 9, 'ink', bold=True)
    for i, n in enumerate(['orders', 'payments', 'SMS', 'menu', 'kitchen']):
        o += box(176 + (i % 3) * 60, 26 + (i // 3) * 44, 54, 36, 'blue', rx=6) + t(203 + (i % 3) * 60, 48 + (i // 3) * 44, n, 6.8, 'ink', bold=True)
    o += t(180, 126, 'Split everything — or split wisely?', 7.6, 'ink', bold=True)
    return o
scene_svg = scene('A monolith containing orders, payments, SMS, menu and kitchen beside five separate service boxes, with a question mark between them.', story_scene(), 'Architecture follows <tspan font-weight="700" class="s-acc">teams and change</tspan>.', h=136)
dialogue = '''R> Sir, a change to the SMS text broke payments. Let’s rewrite everything as microservices!
A> Microservices fix one problem — independent deployment — and bring ten new ones: network calls, data consistency, monitoring 40 services.
K> Then what?
A> First make the monolith modular, with clear boundaries. Then pull out the parts that change often or scale differently — SMS and notifications first — and connect them with events.
R> And serverless?
A> Perfect for those small, event-driven pieces. Let’s compare all the styles honestly.'''

# ------------------------------------------------------------------ picture
def threefig():
    o = t(320, 16, 'Monolith vs microservices vs serverless — the same TiffinGo app', 10.5, 'ink', bold=True)
    o += box(10, 30, 196, 196, 'red', rx=10) + t(108, 48, 'MONOLITH', 8.6, 'ink', bold=True)
    o += box(26, 58, 164, 120, 'card', rx=6) + t(108, 74, 'one deployable app', 7.2, 'ink', bold=True)
    for i, n in enumerate(['orders', 'payments', 'SMS', 'menu']): o += box(36 + (i % 2) * 74, 84 + (i // 2) * 42, 68, 34, 'amber', rx=4) + t(70 + (i % 2) * 74, 105 + (i // 2) * 42, n, 6.8, 'ink')
    o += cyl(78, 184, 60, 34, 'one DB', 'card')
    o += box(222, 30, 196, 196, 'blue', rx=10) + t(320, 48, 'MICROSERVICES', 8.6, 'ink', bold=True)
    for i, n in enumerate(['orders', 'payments', 'SMS', 'menu']):
        x = 234 + (i % 2) * 90; y = 60 + (i // 2) * 80
        o += box(x, y, 80, 32, 'card', rx=4) + t(x + 40, y + 20, n, 6.8, 'ink', bold=True) + cyl(x + 18, y + 36, 44, 30, 'own DB', 'card')
    o += box(434, 30, 196, 196, 'green', rx=10) + t(532, 48, 'SERVERLESS', 8.6, 'ink', bold=True)
    for i, (n, s) in enumerate([('API Gateway', 'managed'), ('functions', 'per request'), ('queues / events', 'managed'), ('DynamoDB', 'per request')]):
        o += box(450, 60 + i * 40, 164, 32, 'card', rx=4) + t(532, 74 + i * 40, n, 7, 'ink', bold=True) + t(532, 86 + i * 40, s, 6.2, 'ink2')
    o += t(320, 244, 'Left: deploy everything together · Middle: deploy each service alone · Right: assemble managed services; no servers at all.', 7.4, 'ink2')
    return o
THREE = bigfig('Three panels: a monolith with orders, payments, SMS and menu modules sharing one database; microservices each with its own database; a serverless app made of API Gateway, functions, queues and DynamoDB.', threefig(), h=254)

def tradefig():
    o = t(320, 16, 'Trade-offs at a glance', 11, 'ink', bold=True)
    rows = [('Start-up speed', [3, 1, 3]), ('Independent deploys', [1, 3, 3]), ('Scale parts separately', [1, 3, 3]), ('Operational simplicity', [3, 1, 2]), ('Debugging / testing ease', [3, 1, 2]), ('Cost at low traffic', [2, 1, 3]), ('Cost at steady high traffic', [3, 2, 1])]
    for j, n in enumerate(['Monolith', 'Microservices', 'Serverless']): o += t(330 + j * 110, 40, n, 8, 'ink', bold=True)
    for i, (n, v) in enumerate(rows):
        y = 52 + i * 26
        o += t(270, y + 15, n, 7.6, 'ink', anchor='end', bold=True)
        for j, s in enumerate(v):
            for d in range(3): o += f'<circle cx="{306 + j * 110 + d * 22}" cy="{y + 11}" r="7" style="fill:{["#2E8B57", "#2E8B57", "#2E8B57"][d] if d < s else "none"};stroke:#2E8B57;stroke-width:1.2"/>'
    o += t(320, 246, 'Three dots = strong. No style wins everywhere — choose by team size, change rate and traffic shape.', 7.4, 'ink2')
    return o
TRADE = bigfig('Trade-off table with dots: monolith strong on start-up speed, simplicity, debugging and steady-traffic cost; microservices strong on independent deploys and scaling parts; serverless strong on independent deploys, scaling and low-traffic cost.', tradefig(), h=256)

picture = ('  <p>The same TiffinGo app in three architecture styles:</p>\n' + THREE + '\n  <p>And what each style is good and bad at:</p>\n' + TRADE)

# ------------------------------------------------------------------ how: an order through microservices
RN = {'app': (4, 54, 54, 50, 'phone', 'App', 'place order'), 'gw': (66, 4, 60, 46, 'cloud', 'API gateway', 'auth, route'), 'ord': (66, 104, 60, 46, 'server', 'Orders svc', 'own DB'),
      'bus': (138, 54, 62, 50, 'dns', 'Event bus', 'OrderPlaced'), 'pay': (212, 4, 64, 46, 'shield', 'Payments', 'charge'), 'kit': (212, 104, 64, 46, 'app', 'Kitchen', 'cook'), 'sms': (290, 54, 66, 50, 'phone', 'SMS svc', 'down ✘ → later')}
RS = [dict(on=['app', 'gw'], hot='gw', move=(58, 70, 70, 40, 'POST'), head='Step 1 · One front door', text='The app calls POST /orders on the API gateway, which checks the token and routes', text2='to the orders service. Clients never see the internal services.', svc='API Gateway / APIM / Apigee — or an ingress in Kubernetes'),
      dict(on=['app', 'gw', 'ord'], hot='ord', move=(96, 50, 96, 104, 'route'), head='Step 2 · The orders service owns orders', text='It validates and saves the order in its own database — no other service may', text2='write to that table (database per service).', svc='Each service = own code, own data, own team, own deploys'),
      dict(on=['app', 'gw', 'ord', 'bus'], hot='bus', move=(126, 127, 150, 90, 'publish'), head='Step 3 · Publish an event, do not call everyone', text='It publishes “OrderPlaced {id:101}” to an event bus and replies to the app at once.', text2='It does not know or wait for who listens.', svc='EventBridge / SNS · Event Grid / Service Bus · Pub/Sub / Eventarc'),
      dict(on=['app', 'gw', 'ord', 'bus', 'pay', 'kit'], hot='kit', move=(200, 70, 222, 120, 'deliver'), head='Step 4 · Subscribers react independently', text='Payments charges the card; kitchen adds the tiffin to the cooking queue — in', text2='parallel, each scaled and deployed separately.', svc='Loose coupling: add a new subscriber without changing orders'),
      dict(on=list(RN), hot='sms', move=(276, 127, 298, 90, 'retry'), head='Step 5 · A failure stays local', text='The SMS service is down: its queue keeps the event and it sends the SMS when it', text2='recovers. Orders and payments never noticed.', svc='Failure isolation — the main benefit (and the main complexity)')]
FLOW = flow_anim('One order through microservices', 'How independent services cooperate through an API gateway and events.', 'Microservices flow', 'Animation: app calls the API gateway; orders service saves to its own database; publishes an event; payments and kitchen react; the SMS service is down and catches up later.', RN, RS, hid='msflow')

# ------------------------------------------------------------------ types
def mapfig():
    o = t(320, 16, 'Seven application architecture styles', 11, 'ink', bold=True)
    items = [('1', 'Monolith', 'one deployable unit', 'red'), ('2', 'Modular monolith', 'one deploy, strict modules', 'amber'), ('3', 'SOA', 'shared services + ESB', 'violet'),
             ('4', 'Microservices', 'small independent services', 'blue'), ('5', 'Serverless', 'functions + managed services', 'green'), ('6', 'Event-driven', 'react to events', 'violet'), ('7', 'Strangler fig', 'migrate step by step', 'amber')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 12 + (i % 4) * 156; y = 32 + (i // 4) * 84
        o += box(x, y, 148, 70, tn, rx=8) + pin(x + 16, y + 16, n) + t(x + 80, y + 34, a, 7.8, 'ink', bold=True) + t(x + 78, y + 54, b, 6.8, 'ink2')
    o += t(320, 210, '1–4 split code more and more · 5–6 change how parts run and talk · 7 is how you move between styles safely.', 7.6, 'ink2')
    return o
MAP = bigfig('Map of seven architecture styles: monolith, modular monolith, service-oriented architecture, microservices, serverless, event-driven, strangler fig migration.', mapfig(), h=222)

def row3(k, items, tones, cap_):
    o = ''
    for i, l in enumerate(items):
        on = i <= k
        o += box(20 + i * 112, 34, 100, 74, tones[i] if on else 'card', rx=8)
        for j, w in enumerate(l.split('|')): o += t(70 + i * 112, 60 + j * 14, w, 7.2 if j == 0 else 6.6, 'ink', bold=(j == 0))
    return o + t(180, 132, cap_, 7.2, 'ink', bold=True)

def a_mono(k):
    o = t(180, 12, ['One codebase', 'One build, one deploy', 'Scale = copy the whole app'][k], 9, 'ink', bold=True)
    return o + row3(k, ['codebase|all modules|in-process calls', 'release|everything|together', 'scale|N copies of|whole app'], ['red', 'amber', 'blue'], ['function calls are fast and simple to debug', 'a small change ships the whole app', 'even idle modules are copied'][k])
A_MONO = cap([a_mono(k) for k in range(3)], [('One codebase', 'All features live in one application and call each other in-process.', ''), ('One deploy', 'Every change ships as a new version of the whole app.', ''), ('Scale whole', 'Scaling means running more copies of everything.', '')],
    'Monolith in action', 'One app, one deploy.', 'Monolith', 'Animation: one codebase with all modules; one release for everything; scaling copies the whole app.', 'm1anim')
T1 = vtype(1, 'Monolith', 'red',
    'A <b>monolithic architecture</b> builds an application as a single deployable unit in which all features — user interface, business logic and data access — share one codebase, one process (or tightly coupled processes) and usually one database, and are built, tested, deployed and scaled together.',
    'A joint family kitchen: one big kitchen cooks everything; easy to coordinate — but renovating the stove means nobody eats that day.',
    'TiffinGo’s original Django app: orders, payments, SMS and menu in one repository, deployed as one container on EC2 Auto Scaling behind an ALB. Fine for 5 developers; painful for 25.',
    'Any single app on VMs or PaaS (Elastic Beanstalk, App Service, App Engine) or one container on ECS/Container Apps/Cloud Run.',
    '', A_MONO,
    'small teams, new products, simple domains — start here.',
    'many teams change different parts at different speeds, or one part needs very different scaling.',
    plain='The whole app is one big program. Simple to build and run, but every change means releasing everything.',
    how=[('Code', 'All modules in one repository and one runtime.'), ('Call', 'Modules call each other as functions (fast, transactional).'), ('Store', 'One shared database, ACID transactions across features.'), ('Deploy', 'Build and release the whole app.'), ('Scale', 'Run more identical copies behind a load balancer.')],
    words=[('deployable unit', 'what you release as one piece'), ('in-process call', 'a function call inside the same program'), ('ACID transaction', 'changes that all succeed or all fail')],
    diff=table(['', 'Monolith', 'Microservices'], [['Deploy', 'all together', 'each service alone'], ['Calls', 'in-process', 'over the network'], ['Data', 'one database', 'database per service'], ['Ops effort', 'low', 'high']], minw=440),
    where=['Start-ups and MVPs', 'Small teams and simple domains', 'Internal business apps'],
    realworld='Shopify runs one of the world’s largest Ruby on Rails monoliths, handling Black Friday peaks — by making it a strictly modular monolith rather than splitting into microservices.',
    pro='“Monolith” is a deployment property, not a quality grade. A monolith with clean module boundaries is easier to split later than “microservices” that share one database — the dreaded <b>distributed monolith</b>.')

def a_mod(k):
    o = t(180, 12, ['Strict module boundaries', 'Each module owns its tables', 'Still one deploy'][k], 9, 'ink', bold=True)
    return o + row3(k, ['orders|module|public API', 'tables|orders_*|only orders writes', 'deploy|one app|one pipeline'], ['amber', 'violet', 'blue'], ['modules call each other only through defined interfaces', 'data ownership is clear — ready to split later', 'you keep monolith simplicity'][k])
A_MOD = cap([a_mod(k) for k in range(3)], [('Boundaries', 'Modules expose small interfaces; internals are hidden.', ''), ('Data ownership', 'Each module owns its tables; no cross-module joins.', ''), ('One deploy', 'Still built and deployed as one application.', '')],
    'Modular monolith in action', 'Monolith simplicity, microservice boundaries.', 'Modular monolith', 'Animation: modules with interfaces; each owning its tables; deployed as one app.', 'm2anim')
T2 = vtype(2, 'Modular monolith', 'amber',
    'A <b>modular monolith</b> is a single deployable application internally divided into well-defined modules aligned to business capabilities, each with a clear public interface and ownership of its own data, with dependency rules enforced in code — combining monolith simplicity with microservice-style boundaries.',
    'One building divided into separate flats with their own doors and meters: one address, one roof, but neighbours do not walk through each other’s kitchens.',
    'TiffinGo’s first step: split the Django app into packages <code>orders</code>, <code>payments</code>, <code>notifications</code>, <code>menu</code>; only <code>payments</code> may touch payment tables; a build check fails if modules import each other’s internals.',
    'Same hosting as a monolith; tools such as module boundary checkers (ArchUnit, import-linter, Packwerk for Rails).',
    '', A_MOD,
    'you want independence between teams but not yet the operational cost of microservices — often the best default.',
    'parts truly need separate scaling, technology or release cadence — then extract them as services.',
    plain='Still one program, but neatly divided into separate parts that do not mess with each other — easy to split later if needed.',
    how=[('Find boundaries', 'Business capabilities (bounded contexts).'), ('Hide internals', 'Modules talk through interfaces.'), ('Own data', 'Separate schemas/tables per module.'), ('Enforce', 'Build-time dependency checks.'), ('Extract later', 'A module can become a service with little rework.')],
    words=[('module', 'a self-contained part of the code'), ('bounded context', 'a business area with its own model and words'), ('interface', 'the agreed way to call a module')],
    diff=table(['', 'Modular monolith', 'Microservices'], [['Boundaries', 'in code', 'over the network'], ['Deploys', 'one', 'many'], ['Failure isolation', 'limited (one process)', 'strong']], minw=440),
    where=['Growing start-ups', 'Teams of 5–50 engineers', 'Preparation for microservices'],
    realworld='In 2023 Amazon Prime Video’s monitoring team publicly described moving an audio/video quality service from distributed serverless components back into a single process and cutting infrastructure cost by about 90% — a famous reminder that splitting is not always better.',
    pro='Microsoft’s and Google’s architecture guides now recommend starting with a modular monolith (“monolith first”) unless team scale already demands independent deployment.')

def a_soa(k):
    o = t(180, 12, ['Shared enterprise services', 'Enterprise service bus', 'Central governance'][k], 9, 'ink', bold=True)
    return o + row3(k, ['services|customer, billing|reused by many apps', 'ESB|routes + transforms|SOAP/XML', 'governance|central team|contracts'], ['violet', 'amber', 'blue'], ['coarse services shared across the company', 'a central bus does routing and transformation (smart pipes)', 'standard contracts; slow change'][k])
A_SOA = cap([a_soa(k) for k in range(3)], [('Shared services', 'Coarse-grained services shared by many applications.', ''), ('ESB', 'An enterprise service bus routes, transforms and orchestrates calls.', ''), ('Governance', 'Central contracts and teams control change.', '')],
    'SOA in action', 'Enterprise-wide shared services.', 'SOA', 'Animation: shared enterprise services; an enterprise service bus; central governance.', 'm3anim')
T3 = vtype(3, 'Service-oriented architecture (SOA)', 'violet',
    '<b>Service-oriented architecture (SOA)</b> structures enterprise systems as coarse-grained, reusable services with formal contracts (often SOAP/WSDL), typically connected and orchestrated through a central <b>enterprise service bus (ESB)</b> that handles routing, transformation and protocol mediation, under central governance.',
    'A government office with a central inward-section clerk: every file passes through one desk that stamps, translates and forwards it to the right department.',
    'A bank TiffinGo partners with exposes a “customer” and “payments” service on its ESB; every channel — branch, ATM, net banking — reuses them.',
    'Enterprise integration products (IBM, Oracle, TIBCO, MuleSoft) and cloud successors: Amazon MQ, Azure Service Bus + Logic Apps, Apigee and API management.',
    '', A_SOA,
    'large enterprises integrating many existing systems with shared business services.',
    'you need rapid independent releases — the central bus and governance become bottlenecks.',
    plain='An older style where big shared services are connected through one central message system that controls everything.',
    how=[('Define services', 'Business functions with formal contracts.'), ('Register', 'In a service registry.'), ('Connect via ESB', 'The bus routes and transforms messages.'), ('Orchestrate', 'Business processes call multiple services.'), ('Govern', 'Central standards and versioning.')],
    words=[('ESB', 'enterprise service bus — a central integration hub'), ('SOAP', 'an XML-based web-service protocol'), ('orchestration', 'a central controller calling services in order')],
    diff=table(['', 'SOA', 'Microservices'], [['Service size', 'coarse, shared', 'small, single purpose'], ['Communication', 'smart central bus', 'smart endpoints, dumb pipes'], ['Data', 'often shared', 'per service'], ['Governance', 'central', 'per team']], minw=480),
    where=['Banks, telecom, government', 'Integrating ERP/CRM/legacy systems', 'Shared enterprise APIs'],
    realworld='Indian public-sector banks and insurers built large SOA/ESB integration layers in the 2000s–2010s; many now expose those services as REST APIs through API gateways while modernising behind them.',
    pro='Microservices are often described as “SOA done right”: the key change is <b>smart endpoints, dumb pipes</b> — logic moves out of the central bus into the services, and the bus becomes simple messaging.')

def a_ms(k):
    o = t(180, 12, ['Service per capability', 'Own data, own deploys', 'Talk over APIs and events'][k], 9, 'ink', bold=True)
    return o + row3(k, ['orders svc|team A|Go', 'payments svc|team B|Java, own DB', 'APIs + events|loose coupling|versioned'], ['blue', 'green', 'violet'], ['each service owns one business capability', 'separate databases, pipelines and releases', 'contracts between services, not shared tables'][k])
A_MS = cap([a_ms(k) for k in range(3)], [('Capability', 'Each service owns one business capability.', ''), ('Independent', 'Own data, own technology, own deployment pipeline and team.', ''), ('Communicate', 'Through APIs and events with versioned contracts.', '')],
    'Microservices in action', 'Small services, independent teams.', 'Microservices', 'Animation: services per business capability; each with its own team, technology and database; communicating through APIs and events.', 'm4anim')
T4 = vtype(4, 'Microservices', 'blue',
    'A <b>microservices architecture</b> builds an application as a suite of small, independently deployable services, each aligned to a business capability, owning its own data, communicating over lightweight APIs or asynchronous events, and typically developed and operated by a small autonomous team.',
    'A food court instead of one restaurant: each stall has its own cooks, menu and stock; one stall closing does not close the court.',
    'TiffinGo extracts <code>notifications</code> (SMS/WhatsApp) and <code>payments</code> into services on ECS Fargate with their own databases and pipelines; orders publish events to them. The SMS team now releases five times a day without touching payments.',
    'Containers on EKS/ECS/Fargate, AKS/Container Apps, GKE/Cloud Run; API gateways; service meshes (App Mesh successor options, Istio, Linkerd); observability (X-Ray, Application Insights, Cloud Trace).',
    '', A_MS,
    'large or fast-growing teams, parts with very different scaling or release needs, strong DevOps maturity.',
    'a small team or unclear domain — you pay network, consistency and operations costs without the benefits.',
    plain='The app is split into many small programs, each doing one job with its own data, built by its own team and updated on its own.',
    how=[('Split by capability', 'Bounded contexts → services.'), ('Own data', 'Database per service; no shared tables.'), ('Communicate', 'REST/gRPC for queries, events for changes.'), ('Deploy independently', 'Pipeline per service; containers or functions.'), ('Operate', 'Tracing, centralised logs, per-service SLOs, resilience patterns (7.5).')],
    words=[('service', 'a separately deployed program with an API'), ('database per service', 'each service keeps its own data'), ('gRPC', 'a fast service-to-service protocol'), ('distributed tracing', 'following a request across services')],
    diff=table(['', 'Microservices', 'Serverless'], [['Unit', 'long-running service (container)', 'function / managed service'], ['Idle cost', 'containers running', '≈ 0'], ['Control', 'high', 'lower (platform limits)'], ['Can combine?', 'yes — a microservice can be serverless', 'yes']], minw=480),
    where=['Large platforms (e-commerce, streaming, ride-hailing)', 'Organisations with many teams', 'Parts with different scaling (search, payments)'],
    realworld='Netflix moved from a monolith to hundreds of microservices on AWS after a 2008 database corruption stopped DVD shipments for three days — the story most often told about why microservices exist.',
    pro='The hardest part is data: a business transaction spanning services (pay + reserve kitchen slot) cannot use one ACID transaction — teams use the <b>saga</b> pattern (a series of local steps with compensating actions) and accept eventual consistency.')

def a_sl(k):
    o = t(180, 12, ['Assemble managed services', 'Functions glue them', 'Pay per use'][k], 9, 'ink', bold=True)
    return o + row3(k, ['managed|API GW, DB,|queues, auth', 'functions|small logic|on events', 'billing|per request|idle ≈ ₹0'], ['green', 'blue', 'amber'], ['most of the app is configuration of managed services', 'your code is only the business glue', 'no servers, automatic scaling, pay per use'][k])
A_SL = cap([a_sl(k) for k in range(3)], [('Managed services', 'Authentication, APIs, storage, queues and databases are all managed services.', ''), ('Functions', 'Small functions implement the business logic between them.', ''), ('Per use', 'Billing per request; scaling and availability by the platform.', '')],
    'Serverless architecture in action', 'Build from managed parts.', 'Serverless', 'Animation: managed services as building blocks; functions as glue; per-request billing.', 'm5anim')
T5 = vtype(5, 'Serverless architecture', 'green',
    'A <b>serverless architecture</b> builds applications primarily from fully managed services — functions (FaaS), API gateways, managed databases, queues, event buses, authentication — so that developers write only business logic and the platform handles provisioning, scaling, availability and per-use billing.',
    'Hosting a wedding entirely with hired services — caterer, decorator, DJ, valet — you plan and coordinate; you do not own a single plate.',
    'TiffinGo’s corporate-lunch portal: Cognito login, API Gateway, Lambda functions, DynamoDB and EventBridge — no servers. Monthly bill at 2,000 orders: under ₹1,000.',
    'AWS Lambda, API Gateway, DynamoDB, EventBridge, Step Functions, SQS; Azure Functions, API Management, Cosmos DB, Event Grid, Durable Functions; Cloud Run, Cloud Run functions, Firestore, Pub/Sub, Workflows.',
    'Lessons 4.5 and 6.1 explain how functions run internally.', A_SL,
    'event-driven or spiky workloads, small teams, fast experiments.',
    'very steady high load, long-running or latency-critical processes, or heavy dependence on one provider’s features is unacceptable.',
    plain='You build the app by connecting ready-made cloud services, and write only small pieces of code. No servers to manage; you pay per use.',
    how=[('Choose services', 'Auth, API, data, messaging, workflow — all managed.'), ('Write functions', 'Small handlers for events and API routes.'), ('Wire with events', 'Triggers connect services.'), ('Configure', 'Permissions (IAM), limits, retries in IaC (SAM, CDK, Bicep, Terraform).'), ('Observe', 'Per-function metrics, traces and costs.')],
    words=[('FaaS', 'function as a service'), ('trigger', 'what starts a function'), ('cold start', 'delay when a new function copy starts'), ('vendor lock-in', 'dependence on one provider’s services')],
    diff=table(['', 'Serverless', 'Containers (microservices)'], [['Scaling', 'per request, automatic', 'autoscaling rules'], ['Max run time', 'limited (e.g. 15 min Lambda)', 'unlimited'], ['Portability', 'lower', 'higher']], minw=440),
    where=['APIs with spiky traffic', 'Event processing and automation', 'Start-up MVPs'],
    realworld='Coca-Cola’s vending machine payment back end and many media companies’ image pipelines are frequently cited AWS serverless case studies — chosen because traffic is bursty and idle cost matters.',
    pro='Serverless shifts cost from capacity to <b>per-request</b>: at very high steady traffic a container fleet with a Savings Plan can be cheaper. Calculate the break-even (Lesson 5.5) instead of assuming.')

def a_ev(k):
    o = t(180, 12, ['Producer emits an event', 'Router delivers it', 'Consumers react independently'][k], 9, 'ink', bold=True)
    return o + row3(k, ['orders|“OrderPlaced”|fact, past tense', 'event bus|rules, filters|retries', 'payments · kitchen|SMS · analytics|in parallel'], ['blue', 'violet', 'green'], ['events describe what happened, not what to do', 'the router knows subscribers; producers do not', 'add consumers without changing the producer'][k])
A_EV = cap([a_ev(k) for k in range(3)], [('Emit', 'A service records a fact: “OrderPlaced”.', ''), ('Route', 'An event bus or topic delivers it to every interested subscriber.', ''), ('React', 'Consumers act independently and in parallel.', '')],
    'Event-driven architecture in action', 'Services react to facts.', 'Event-driven', 'Animation: a producer emits an OrderPlaced event; an event bus routes it; payments, kitchen, SMS and analytics react independently.', 'm6anim')
T6 = vtype(6, 'Event-driven architecture', 'violet',
    'An <b>event-driven architecture</b> lets components communicate by producing and consuming <b>events</b> — immutable records that something happened (e.g. “OrderPlaced”) — through brokers such as topics, queues, event buses or streams, so producers and consumers are decoupled in time, location and knowledge of each other.',
    'A temple bell: the priest rings it once; devotees, flower sellers and the prasad counter each react in their own way — the priest does not phone each of them.',
    'TiffinGo’s orders service publishes OrderPlaced; payments, kitchen, SMS and analytics subscribe. Adding a “loyalty points” service last month needed zero changes in orders — it just subscribed.',
    'Amazon EventBridge, SNS, SQS, Kinesis, MSK; Azure Event Grid, Service Bus, Event Hubs; Google Pub/Sub, Eventarc, Managed Service for Apache Kafka.',
    'Lab: steps 1 and 2 below build event routing on your own account.', A_EV,
    'several parts must react to the same change, workloads are spiky, or you want to add features without touching existing services.',
    'you need an immediate answer from the other side (use a request/response API) or strict global ordering everywhere.',
    plain='Parts of the app announce “this happened” and other parts react to it on their own — nobody waits for anybody.',
    how=[('Define events', 'Name (past tense), schema, version.'), ('Publish', 'Producer sends to a topic/bus/stream.'), ('Route', 'Rules or subscriptions deliver copies.'), ('Consume', 'Each consumer processes at its pace; idempotently.'), ('Handle failure', 'Retries, dead-letter queues, replay from streams.')],
    words=[('event', 'a record that something happened'), ('producer / consumer', 'who sends / who reacts'), ('broker', 'the service that stores and delivers events'), ('eventual consistency', 'all parts agree after a short delay')],
    diff=table(['', 'Event-driven', 'Request/response'], [['Coupling', 'loose (producer does not know consumers)', 'tight (caller knows callee)'], ['Caller waits', 'no', 'yes'], ['Best for', 'notifications, workflows, fan-out', 'queries needing an answer now']], minw=480),
    where=['Order and payment workflows', 'IoT and click streams', 'Integrations between SaaS and internal systems'],
    realworld='Amazon EventBridge can receive events directly from SaaS partners (e.g. Zendesk, Datadog, Shopify) — so a “new support ticket” in a SaaS app can trigger your AWS workflow without polling.',
    pro='Events should carry <b>facts, not commands</b>: “OrderPlaced” lets any service decide what to do; “SendSMS” couples the producer to one consumer’s job. Good event names keep the architecture open for future services.')

def a_str(k):
    o = t(180, 12, ['Put a façade in front', 'Route one feature to new code', 'Monolith shrinks away'][k], 9, 'ink', bold=True)
    o += box(14, 46, 70, 46, 'green', rx=6) + t(49, 73, 'users', 7.4, 'ink') + arrow(86, 69, 112, 69)
    o += box(114, 40, 80, 58, 'amber', rx=6) + t(154, 64, 'gateway', 7.4, 'ink', bold=True) + t(154, 80, 'routes', 6.6, 'ink2')
    mono = [140, 100, 40][k]
    o += box(220, 30, mono, 40, 'red', rx=6) + t(220 + mono / 2, 54, 'monolith', 7, 'ink')
    if k >= 1: o += box(220, 78, 60, 30, 'blue', rx=4) + t(250, 97, 'SMS svc', 6.6, 'ink')
    if k == 2: o += box(286, 78, 60, 30, 'blue', rx=4) + t(316, 97, 'payments', 6.6, 'ink') + box(270, 30, 76, 40, 'blue', rx=4) + t(308, 54, 'orders svc', 6.6, 'ink')
    o += arrow(196, 60, 218, 50)
    o += t(180, 134, ['all traffic still goes to the old app', '/notifications now goes to the new service', 'feature by feature until the old app can be retired'][k], 7.2, 'ink', bold=True)
    return o
A_STR = cap([a_str(k) for k in range(3)], [('Façade', 'Put an API gateway or proxy in front of the monolith.', ''), ('Redirect', 'Route one feature’s paths to a new service.', ''), ('Strangle', 'Repeat until the old system can be switched off.', '')],
    'Strangler fig in action', 'Replace a system piece by piece.', 'Strangler fig', 'Animation: a gateway in front of the monolith; one feature routed to a new service; more features moved until the monolith is small.', 'm7anim')
T7 = vtype(7, 'Strangler fig migration', 'amber',
    'The <b>strangler fig pattern</b> incrementally migrates a legacy system by placing a routing façade in front of it and redirecting one capability at a time to new services, until the old system can be retired — avoiding a risky “big bang” rewrite.',
    'Renovating a house room by room while the family keeps living in it, instead of demolishing it and living on the street for a year.',
    'TiffinGo puts API Gateway in front of the Django monolith. <code>/notifications</code> goes to the new SMS service first; payments next quarter. The monolith keeps serving everything else and shrinks each release.',
    'API Gateway, ALB path routing, AWS Migration Hub Refactor Spaces; Azure API Management, Front Door; Apigee, Cloud Load Balancing URL maps.',
    '', A_STR,
    'modernising a large running system without stopping it.',
    'the old system cannot be put behind a proxy, or data cannot be separated feature by feature (plan data migration first).',
    plain='Moving from an old app to a new design one piece at a time, with a traffic router deciding which part handles each request.',
    how=[('Façade', 'Route all traffic through a gateway/proxy.'), ('Pick a seam', 'A feature with clear boundaries and high change rate.'), ('Build new', 'New service + its data (sync data during transition).'), ('Redirect', 'Change routing rules; monitor; roll back if needed.'), ('Retire', 'Remove dead code; repeat.')],
    words=[('façade', 'a front that hides what is behind it'), ('seam', 'a natural place to cut a system apart'), ('big bang rewrite', 'replacing everything at once')],
    diff=table(['', 'Strangler fig', 'Big-bang rewrite'], [['Risk', 'small steps, reversible', 'all-or-nothing'], ['Value delivered', 'continuously', 'only at the end'], ['Duration', 'long but safe', 'often overruns']], minw=440),
    where=['Legacy modernisation', 'Mainframe and old web apps', 'Monolith-to-microservices moves'],
    realworld='The name comes from Martin Fowler’s 2004 article, inspired by strangler fig trees in Australia that grow around a host tree until they replace it — now the standard modernisation advice in AWS, Azure and Google migration guides.',
    pro='The façade is also a measurement point: routing by percentage (canary) lets you send 5% of /payments traffic to the new service and compare errors and latency before switching fully.')

SUMMARY = table(['#', 'Style', 'Deploy unit', 'Data', 'Best for'], [
    ['1', 'Monolith', 'whole app', 'one DB', 'small teams, new products'], ['2', 'Modular monolith', 'whole app', 'per module (logical)', 'growing teams — good default'], ['3', 'SOA', 'shared services + ESB', 'often shared', 'enterprise integration'],
    ['4', 'Microservices', 'each service', 'per service', 'many teams, different scaling'], ['5', 'Serverless', 'functions/config', 'managed', 'spiky, event-driven, small teams'], ['6', 'Event-driven', '(communication style)', 'events + per-service', 'fan-out, workflows'], ['7', 'Strangler fig', '(migration path)', 'migrate per feature', 'modernising legacy']], minw=620)
CHECK = ('  <h3>Check yourself: which style?</h3>\n' +
    qx('A. Three developers building a new app for a college canteen.', ['Microservices', 'Monolith (modular)', 'SOA with ESB', 'Event sourcing'], 1, 'Keep it simple.') +
    qx('B. 200 engineers, 30 teams, payments must release separately from search.', ['Single monolith', 'Microservices', 'Two-tier', 'Batch'], 1, 'Team scale.') +
    qx('C. A new “loyalty points” feature must react to every order without changing the orders code.', ['Direct API call from orders', 'Subscribe to an OrderPlaced event', 'Shared database trigger', 'Bigger monolith'], 1, 'Event-driven.') +
    qx('D. Replace a 15-year-old billing system with zero downtime.', ['Big-bang rewrite', 'Strangler fig', 'Delete and rebuild', 'Lift and shift only'], 1, 'Incremental.'))

TYPES = ('  <p>Seven architecture styles, each in the same pattern: definition, plain words, analogy, internal steps, animation, differences, where used, real-world example, TiffinGo scenario and an expert note.</p>\n'
         + challenge(['What is a “distributed monolith” and why is it the worst of both worlds?', 'How do microservices do a transaction across two databases?', 'Why should events be facts, not commands?'], 'types 1, 4 and 6') + MAP
         + jump(['Monolith', 'Modular', 'SOA', 'Microservices', 'Serverless', 'Event-driven', 'Strangler']) + T1 + T2 + T3 + T4 + T5 + T6 + T7
         + '\n  <h3 style="margin-top:34px">All seven side by side</h3>\n' + SUMMARY + '\n' + CHECK)

parts = wwu([
    ('API gateway', 'Single entry point for clients.', 'Auth, routing, rate limits, versioning.', 'API Gateway, APIM, Apigee.'),
    ('Service discovery', 'How services find each other.', 'Addresses change as containers move.', 'Cloud Map, Kubernetes DNS, Consul.'),
    ('Event bus / broker', 'Delivers events and messages.', 'Decouples producers and consumers.', 'EventBridge, Service Bus, Pub/Sub, Kafka.'),
    ('Distributed tracing', 'Follows one request across services.', 'Debugging across 20 services needs it.', 'X-Ray, Application Insights, Cloud Trace, OpenTelemetry.'),
    ('Saga', 'A multi-step business transaction with compensations.', 'Replaces cross-service ACID transactions.', 'Step Functions, Durable Functions, Workflows.'),
    ('Conway’s law', 'Systems mirror the communication structure of the organisation.', 'Design services around teams.', '“Two-pizza teams” owning services.')])

DEEP = ('  <h3>When to split: a checklist</h3>\n  <ul><li>Different parts need <b>different release speeds</b> (SMS text changes daily, payments monthly).</li><li>Different parts need <b>different scaling</b> (search at Diwali ×20, admin ×1).</li><li>Teams block each other in one codebase.</li><li>You have CI/CD, monitoring, tracing and on-call maturity.</li></ul>\n  <p>If fewer than two boxes are ticked, improve the modular monolith first.</p>\n'
    '  <h3>The costs nobody puts on the slide</h3>\n' + table(['Cost', 'Why'], [['Network latency and failures', 'every call can be slow or fail; needs timeouts, retries, circuit breakers (7.5)'], ['Data consistency', 'no cross-service transactions; sagas and eventual consistency'], ['Observability', 'logs and traces across many services'], ['Platform work', 'pipelines, service mesh, secrets, versioning for each service'], ['Testing', 'contract tests between services']], minw=520) +
    '\n  <h3>Choreography vs orchestration</h3>\n  <p><b>Choreography</b>: services react to events with no central controller (flexible, harder to see the whole flow). <b>Orchestration</b>: a workflow service (Step Functions, Durable Functions, Google Workflows) calls each step and handles failures (visible, central). Many systems use events between domains and orchestration inside one workflow.</p>')

clouds = vendor_tabs('<p><b>AWS:</b> monolith on Elastic Beanstalk/EC2; microservices on ECS/EKS/Fargate with API Gateway, Cloud Map; serverless with Lambda, API Gateway, DynamoDB, Step Functions; events with EventBridge, SNS, SQS, Kinesis; migration with Refactor Spaces.</p>',
    '<p><b>Azure:</b> monolith on App Service; microservices on AKS/Container Apps (with Dapr) and API Management; serverless with Functions and Durable Functions, Cosmos DB, Logic Apps; events with Event Grid, Service Bus, Event Hubs.</p>',
    '<p><b>Google Cloud:</b> monolith on App Engine/Cloud Run; microservices on GKE/Cloud Run with Apigee/API Gateway; serverless with Cloud Run functions, Firestore, Workflows; events with Pub/Sub and Eventarc.</p>') + \
    cloud3([['Monolith hosting', 'Elastic Beanstalk, EC2', 'App Service', 'App Engine, Cloud Run'], ['Microservices runtime', 'ECS/EKS/Fargate', 'AKS, Container Apps', 'GKE, Cloud Run'], ['Functions', 'Lambda', 'Functions', 'Cloud Run functions'], ['Event bus', 'EventBridge / SNS', 'Event Grid / Service Bus', 'Pub/Sub / Eventarc'], ['Workflow (saga)', 'Step Functions', 'Durable Functions / Logic Apps', 'Workflows']])

# ------------------------------------------------------------------ practical
MOCKQ.extend([
 (mock('aws', ['Amazon SQS', 'Queues', 'tiffingo-kitchen'], ['Queues'], 'Queues',
       [('SNS subscriptions', 'Subscribe to Amazon SNS topic'), ('Specify an Amazon SNS topic', '▾ tiffingo-order-placed'), ('Access policy', 'updated automatically to allow the topic')], 'Save'),
  mock('az', ['Home', 'Event Grid Topics', 'tiffingo-orders', 'Create Event Subscription'], ['Overview', 'Event Subscriptions', 'Access keys', 'Metrics'], 'Event Subscriptions',
       [('Name', 'kitchen'), ('Endpoint type', '▾ Storage Queues'), ('Endpoint', 'tiffingo… / kitchen')], 'Create'),
  mock('gcp', ['Pub/Sub', 'Topics', 'tiffingo-order-placed'], ['Topics', 'Subscriptions', 'Snapshots', 'Schemas'], 'Topics',
       [('Subscriptions', 'kitchen-sub · sms-sub'), ('Publish message', 'Message body: {"order":101}')], 'Publish')),
 (mock('aws', ['Amazon S3', 'tiffingo-photos-…', 'Create event notification'], ['Objects', 'Properties', 'Permissions'], 'Properties',
       [('Event name', 'photo-uploaded'), ('Event types', '[x] All object create events'), ('Destination', '( ) SQS queue — tiffingo-photo-worker')], 'Save changes'),
  mock('az', ['Home', 'tiffingo…', 'Events', 'Event Subscription'], ['Overview', 'Events', 'Containers', 'Queues'], 'Events',
       [('Filter to Event Types', '▾ Blob Created'), ('Endpoint type', '▾ Storage Queues'), ('Endpoint', 'tiffingo… / photo-worker')], 'Create'),
  mock('gcp', ['Cloud Storage', 'tiffingo-photos-…'], ['Objects', 'Configuration', 'Permissions'], 'Configuration',
       [('Pub/Sub notifications (CLI)', 'gcloud storage buckets notifications create …'), ('Event type', 'OBJECT_FINALIZE')], 'Done')),
])

AWS_POL = "python3 -c \"import json,sys; q,s,src=sys.argv[1:4]; print(json.dumps({'Policy': json.dumps({'Version':'2012-10-17','Statement':[{'Effect':'Allow','Principal':{'Service':s},'Action':'sqs:SendMessage','Resource':q,'Condition':{'ArnEquals':{'aws:SourceArn':src}}}]})}))\""

STEP1 = ('1 · Fan-out: one event, two independent services', tri(
    (['[[Simple Notification Service]] → [[Topics]] → [[Create topic]] → [[Standard]], name <code>tiffingo-order-placed</code>.', '[[SQS]] → create queues <code>tiffingo-kitchen</code> and <code>tiffingo-sms</code>; for each: [[Subscribe to Amazon SNS topic]] → choose the topic (the console adds the queue policy).', 'Topic → [[Publish message]] → body <code>{"order":101}</code>; each queue → [[Send and receive messages]] → [[Poll for messages]]: both got it.'],
     f"T=$(aws sns create-topic --name tiffingo-order-placed --query TopicArn --output text)\nfor q in kitchen sms; do\n  U=$(aws sqs create-queue --queue-name tiffingo-$q --query QueueUrl --output text)\n  A=$(aws sqs get-queue-attributes --queue-url $U --attribute-names QueueArn --query Attributes.QueueArn --output text)\n  aws sqs set-queue-attributes --queue-url $U --attributes \"$({AWS_POL} $A sns.amazonaws.com $T)\"\n  aws sns subscribe --topic-arn $T --protocol sqs --notification-endpoint $A --attributes RawMessageDelivery=true\ndone\naws sns publish --topic-arn $T --message '{{\"order\":101}}'\nfor q in kitchen sms; do aws sqs receive-message --queue-url $(aws sqs get-queue-url --queue-name tiffingo-$q --query QueueUrl --output text) --wait-time-seconds 5 --query 'Messages[0].Body' --output text; done",
     '<code>{\"order\":101}</code> printed twice — once from the kitchen queue and once from the SMS queue. The publisher did not know either of them.'),
    (['[[Subscriptions]] → [[Resource providers]] → register <code>Microsoft.EventGrid</code>.', '[[Event Grid Topics]] → [[Create]] → <code>tiffingo-orders-&lt;n&gt;</code>, Central India. In your storage account create queues <code>kitchen</code> and <code>sms</code>.', 'Topic → [[+ Event Subscription]] → endpoint type [[Storage Queues]] → queue kitchen; repeat for sms. Publish with the CLI (the portal has no publish button) and look at both queues in [[Storage browser]].'],
     "az provider register --namespace Microsoft.EventGrid\nTOPIC=tiffingo-orders-$RANDOM\naz eventgrid topic create --resource-group rg-tiffingo --name $TOPIC --location centralindia\nTID=$(az eventgrid topic show --resource-group rg-tiffingo --name $TOPIC --query id --output tsv)\nSAID=$(az storage account show --name $SA --query id --output tsv)\nfor q in kitchen sms; do\n  az storage queue create --account-name $SA --name $q --auth-mode key\n  az eventgrid event-subscription create --name $q --source-resource-id $TID \\\n    --endpoint-type storagequeue --endpoint $SAID/queueservices/default/queues/$q\ndone\nEP=$(az eventgrid topic show --resource-group rg-tiffingo --name $TOPIC --query endpoint --output tsv)\nKEY=$(az eventgrid topic key list --resource-group rg-tiffingo --name $TOPIC --query key1 --output tsv)\ncurl -s -X POST -H \"aeg-sas-key: $KEY\" -H 'Content-Type: application/json' $EP \\\n  -d '[{\"id\":\"1\",\"eventType\":\"OrderPlaced\",\"subject\":\"orders/101\",\"eventTime\":\"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'\",\"data\":{\"order\":101},\"dataVersion\":\"1.0\"}]'\nfor q in kitchen sms; do az storage message get --account-name $SA --queue-name $q --auth-mode key --query \"[0].content\" --output tsv; done",
     'two messages (base64-encoded event JSON with <code>OrderPlaced</code>) — one per queue.'),
    (['[[Pub/Sub]] → [[Create topic]] <code>tiffingo-order-placed</code> (untick default subscription).', '[[Subscriptions]] → [[Create subscription]] <code>kitchen-sub</code> and <code>sms-sub</code> on that topic, pull delivery.', 'Topic → [[Messages]] → [[Publish message]] <code>{"order":101}</code>; each subscription → [[Messages]] → [[Pull]].'],
     "gcloud pubsub topics create tiffingo-order-placed\nfor s in kitchen-sub sms-sub; do gcloud pubsub subscriptions create $s --topic=tiffingo-order-placed; done\ngcloud pubsub topics publish tiffingo-order-placed --message='{\"order\":101}'\nfor s in kitchen-sub sms-sub; do gcloud pubsub subscriptions pull $s --auto-ack --limit=1 --format='value(message.data)'; done",
     '<code>{\"order\":101}</code> twice — each subscription gets its own copy.')),
    'This is the backbone of microservices and serverless: add a third subscriber tomorrow without touching the publisher.')

STEP2 = ('2 · A storage upload becomes an event (no code)', tri(
    (['Create queue <code>tiffingo-photo-worker</code>; edit its [[Access policy]] to allow <code>s3.amazonaws.com</code> to SendMessage from your bucket ARN.', 'Bucket → [[Properties]] → [[Event notifications]] → [[Create event notification]] → all object create events → destination [[SQS queue]] → tiffingo-photo-worker → [[Save changes]].', 'Upload any file → poll the queue: an S3 event with the object key.'],
     f"B=tiffingo-photos-$RANDOM$RANDOM; aws s3 mb s3://$B --region ap-south-1\nU=$(aws sqs create-queue --queue-name tiffingo-photo-worker --query QueueUrl --output text)\nA=$(aws sqs get-queue-attributes --queue-url $U --attribute-names QueueArn --query Attributes.QueueArn --output text)\naws sqs set-queue-attributes --queue-url $U --attributes \"$({AWS_POL} $A s3.amazonaws.com arn:aws:s3:::$B)\"\naws s3api put-bucket-notification-configuration --bucket $B --notification-configuration \\\n  '{{\"QueueConfigurations\":[{{\"QueueArn\":\"'$A'\",\"Events\":[\"s3:ObjectCreated:*\"]}}]}}'\necho thali > thali.jpg && aws s3 cp thali.jpg s3://$B/\naws sqs receive-message --queue-url $U --wait-time-seconds 10 --query 'Messages[].Body' --output text | head -c 400",
     'a JSON body with <code>\"eventName\":\"ObjectCreated:Put\"</code> and <code>\"key\":\"thali.jpg\"</code> (the first message may be an <code>s3:TestEvent</code>).'),
    (['Storage account → [[Queues]] → create <code>photo-worker</code>.', '[[Events]] → [[+ Event Subscription]] → name photo-upload, event types [[Blob Created]], endpoint [[Storage Queues]] → photo-worker → [[Create]].', 'Upload a blob to any container → [[Storage browser]] → queue photo-worker: one message.'],
     "SAID=$(az storage account show --name $SA --query id --output tsv)\naz storage queue create --account-name $SA --name photo-worker --auth-mode key\naz eventgrid event-subscription create --name photo-upload --source-resource-id $SAID \\\n  --endpoint-type storagequeue --endpoint $SAID/queueservices/default/queues/photo-worker \\\n  --included-event-types Microsoft.Storage.BlobCreated\naz storage container create --account-name $SA --name photos --auth-mode key\necho thali > thali.jpg && az storage blob upload --account-name $SA --container-name photos --name thali.jpg --file thali.jpg --auth-mode key\nsleep 10; az storage message get --account-name $SA --queue-name photo-worker --auth-mode key --query \"[0].content\" --output tsv | base64 -d | head -c 400",
     'an Event Grid event with <code>\"eventType\":\"Microsoft.Storage.BlobCreated\"</code> and the blob URL.'),
    (['Create a bucket and a topic <code>photo-uploads</code>.', 'Bucket notifications are set from the CLI (no console page): run the commands on the right.', 'Upload a file → [[Pub/Sub]] → subscription photo-worker → [[Pull]].'],
     "B=tiffingo-photos-$RANDOM$RANDOM\ngcloud storage buckets create gs://$B --location=asia-south1\ngcloud pubsub topics create photo-uploads\ngcloud storage buckets notifications create gs://$B --topic=photo-uploads --event-types=OBJECT_FINALIZE\ngcloud pubsub subscriptions create photo-worker --topic=photo-uploads\necho thali > thali.jpg && gcloud storage cp thali.jpg gs://$B/\nsleep 10; gcloud pubsub subscriptions pull photo-worker --auto-ack --limit=1 --format='table(message.attributes.eventType,message.attributes.objectId)'",
     '<code>OBJECT_FINALIZE  thali.jpg</code>. The Cloud Storage service agent is granted publish rights on the topic automatically.')),
    'A photo-resizing microservice or function would read this queue — the upload code never needs to know it exists.')

prac = practical(OWN_INTRO + ' Topics, queues and event subscriptions cost nothing at this volume.', [SETUP_STEP, STEP1, STEP2],
    cleanup='<b>AWS:</b> <code>aws sns delete-topic --topic-arn $T; for q in kitchen sms photo-worker; do aws sqs delete-queue --queue-url $(aws sqs get-queue-url --queue-name tiffingo-$q --query QueueUrl --output text); done; aws s3 rb s3://$B --force</code>.<br>'
            '<b>Azure:</b> <code>az group delete --name rg-tiffingo --yes --no-wait</code>.<br>'
            '<b>Google Cloud:</b> <code>gcloud pubsub subscriptions delete kitchen-sub sms-sub photo-worker; gcloud pubsub topics delete tiffingo-order-placed photo-uploads; gcloud storage rm --recursive gs://$B</code>.')

mist = mistakes([
    ['Starting a new product with dozens of microservices.', 'Hype; copying Netflix.', 'Modular monolith first; extract when a checklist says so.'],
    ['Services sharing one database.', 'Easier than moving data.', 'Database per service; integrate via APIs/events.'],
    ['Chains of synchronous calls (A→B→C→D).', 'Feels like function calls.', 'Use events; add timeouts, retries, circuit breakers.'],
    ['Big-bang rewrites.', 'Old code feels hopeless.', 'Strangler fig, feature by feature.'],
    ['Events named as commands (“SendSMS”).', 'Thinking of one consumer.', 'Publish facts (“OrderPlaced”).'],
    ['Non-idempotent consumers.', 'Assuming exactly-once delivery.', 'Deduplicate by event ID; make handlers idempotent.'],
    ['No tracing across services.', 'Logging per service only.', 'OpenTelemetry + X-Ray / App Insights / Cloud Trace from day one.']])

cert = table(['Exam / syllabus', 'What is asked'], [['C-DAC PGCP-BDA', 'Monolithic vs microservices vs serverless architectures in the cloud.'], ['AWS CLF-C02', 'Decoupling with SQS/SNS/EventBridge, serverless (Lambda), containers (ECS/EKS/Fargate), monolith vs microservices concepts.'], ['AZ-900', 'Containers (ACI, Container Apps, AKS), Functions, App Service, serverless concepts.'], ['Google Cloud Digital Leader', 'Modernising applications: microservices, containers, serverless, APIs; Cloud Run, GKE, Apigee.']], minw=560) + \
    qx('1. Which architecture deploys the whole application as one unit?', ['Microservices', 'Monolith', 'Serverless', 'Event-driven'], 1, 'Monolith.') + \
    qx('2. Which AWS service decouples microservices with a fully managed message queue?', ['Amazon SQS', 'Amazon EBS', 'Amazon Route 53', 'AWS Snowball'], 0, 'SQS.') + \
    qx('3. A main benefit of microservices is…', ['simpler operations', 'independent deployment and scaling of services', 'fewer network calls', 'one shared database'], 1, 'Independence.') + \
    qx('4. Which pattern migrates a legacy system piece by piece behind a façade?', ['Strangler fig', 'Big bang', 'Lift and shift', 'Sharding'], 0, 'Strangler fig.') + \
    qx('5. Which Google Cloud service provides asynchronous messaging between services?', ['Pub/Sub', 'Cloud SQL', 'Filestore', 'Cloud DNS'], 0, 'Pub/Sub.') + \
    qx('6. In serverless architectures, scaling and server management are handled by…', ['the customer', 'the cloud provider', 'the database', 'the CDN'], 1, 'Provider.')

proj = miniproject('Mini project: a modernisation plan for TiffinGo',
    'Decide what to split, how, and in which order — and prove the event backbone.',
    ['<b>Map capabilities:</b> orders, payments, menu, kitchen, notifications, loyalty.',
     '<b>Score them:</b> change rate, scaling need, team ownership (use the “when to split” checklist).',
     '<b>Plan:</b> modular-monolith steps first; then the first two services to extract via strangler fig.',
     '<b>Events:</b> name 5 events (facts) and who subscribes.',
     '<b>Prove it:</b> on your own account build the fan-out and the storage event (steps 1–2).',
     '<b>Risks:</b> list data-consistency and observability work needed (saga, tracing).'],
    'A capability map, an extraction roadmap, an event catalogue and a working fan-out demo.', 'This lesson + 6.4 (integration) + 7.3 (tiers) + 7.5 (patterns).')

assemble_v2(HERE, story_h2='A one-line change that broke payments', hook_html=hk,
    narration='TiffinGo’s 25 developers share one codebase. A tiny SMS change broke payments. The team wants microservices — the question is how much, and how fast.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Monolith vs microservices vs serverless',
    formal='A <b>monolithic architecture</b> deploys an application as a single unit; a <b>microservices architecture</b> composes it from small, independently deployable services aligned to business capabilities, each owning its data and communicating via APIs or events; a <b>serverless architecture</b> builds it from fully managed services and event-triggered functions where the provider handles servers, scaling and per-use billing.',
    simple='Monolith = one big app. Microservices = many small apps working together. Serverless = an app built from cloud services and small functions, with no servers to manage.',
    interview=['“A monolith is one deployable unit — simple to build and run. Microservices split by business capability with their own data and deployments — independent teams and scaling, but more network, data-consistency and operational complexity.”', '“Serverless uses managed services and functions — no servers, pay per use. I usually start with a modular monolith and extract services with the strangler fig pattern, connecting them with events.”'],
    terms_rows=[('Monolith', 'One deployable unit.'), ('Modular monolith', 'One deploy, strict modules.'), ('Microservice', 'Small independent service.'), ('SOA / ESB', 'Shared services, central bus.'), ('Serverless', 'Managed services + functions.'), ('Event', 'Record of something that happened.'), ('Pub/sub', 'Publish once, many receive.'), ('Saga', 'Multi-step transaction with compensations.'), ('Strangler fig', 'Incremental migration.'), ('Conway’s law', 'Systems mirror teams.')],
    exam='Expect decoupling questions (SQS/SNS/EventBridge, Service Bus/Event Grid, Pub/Sub), serverless vs containers, and the benefits/drawbacks of microservices.',
    picture_h2='Three styles side by side, and their trade-offs', picture_html=picture,
    after_picture=[('types', 'Types, one by one', 'Seven architecture styles, one by one', TYPES)],
    how_h2='One order through microservices', how_intro='How independent services cooperate — and contain failures.', how_anim=FLOW,
    parts_h2='Six building blocks of service-based systems', parts_html=parts, lv='',
    myth_rows=[('Microservices are always better.', 'They trade simplicity for independence.', 'Trade-offs figure.'), ('Serverless means no architecture.', 'You design events, limits, permissions and costs.', 'Type 5.'), ('Splitting fixes bad code.', 'Bad boundaries become a distributed monolith.', 'Type 1 expert note.')],
    extra_secs=[('deep', 'Deep dive', 'When to split, hidden costs, choreography vs orchestration', DEEP)],
    clouds_html=clouds, practical_html=prac, mistakes_html=mist, cert_html=cert, project_html=proj,
    can_now=['Compare monolith, modular monolith, SOA, microservices and serverless.', 'Explain event-driven communication and why events decouple services.', 'Decide when to split a monolith and use the strangler fig pattern.', 'Explain sagas, Conway’s law and choreography vs orchestration.', 'Build pub/sub fan-out and storage-event routing on your own account.'],
    next_html='<a href="../05-cloud-design-patterns-load-balancing-auto-scaling-caching/">7.5 Cloud design patterns</a>.',
    pre='<b>Before you start:</b> <a href="../03-multi-tier-architecture/">7.3 Multi-tier</a> and <a href="../../06-cloud-building-blocks/04-cloud-products-and-solutions-map/">6.4 (integration services)</a>.')
