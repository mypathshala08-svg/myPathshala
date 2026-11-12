import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
def cap(frames, steps, title, intro, panel, aria, hid, delay=5500):
    return anim_one('Animated', title, intro, panel, aria, cap_frames(frames, steps), [s[0] + '.' for s in steps], delay=delay, hid=hid)


hk = hook('Diwali, 8 p.m.: traffic jumps 12× in ten minutes, the payment provider slows down, and the menu database is hit 4,000 times a second for the same page. Which small, reusable designs keep TiffinGo alive?',
    'Seven <b>cloud design patterns</b>: a <b>load balancer</b> spreads requests; <b>auto scaling</b> adds servers; <b>cache-aside</b> serves repeated reads from memory; a <b>CDN</b> answers static content at the edge; a <b>queue</b> levels write bursts; <b>retries with exponential backoff and jitter</b> survive brief glitches without causing storms; a <b>circuit breaker</b> stops calling a failing dependency. Patterns are named, proven solutions — learn them once and you will recognise them in every architecture. You then build a load-balanced, auto-scaled web tier on <b>your own</b> account and watch it fail over.',
    ['Seven patterns that turn a fragile app into a resilient one.', 'Why retries without jitter can take down a healthy service.', 'Watch a load balancer route around a stopped server.'])

def story_scene():
    o = t(180, 12, 'Diwali 8 p.m.: three problems at once', 9, 'ink', bold=True)
    for i, (n, s, tn) in enumerate([('Traffic ×12', 'servers busy', 'red'), ('Same menu read', '4,000/s on DB', 'amber'), ('Payments slow', '8 s per call', 'violet')]):
        x = 14 + i * 114
        o += box(x, 26, 104, 70, tn, rx=8) + t(x + 52, 52, n, 8, 'ink', bold=True) + t(x + 52, 72, s, 7, 'ink')
    o += t(180, 116, 'Answers: load balancing + auto scaling · caching · circuit breaker.', 7.6, 'ink', bold=True)
    return o
scene_svg = scene('Three boxes: traffic times twelve, the same menu read 4,000 times a second, a slow payment provider.', story_scene(), 'Patterns are <tspan font-weight="700" class="s-acc">named solutions</tspan> to recurring problems.', h=132)
dialogue = '''R> Sir, last Diwali we added servers by hand at 8:15 — too late. And when payments got slow, our whole app froze.
A> Three different problems. Load balancer plus auto scaling handles the traffic — automatically, before 8:15.
K> And the database being hit for the same menu thousands of times?
A> Cache it. The first request reads the database and stores the answer in Redis for five minutes; the next four thousand read memory.
R> And the frozen app?
A> Every thread was waiting 8 seconds for payments. A timeout plus a circuit breaker would have failed fast and shown “pay on delivery”. Let’s learn the seven patterns.'''

# ------------------------------------------------------------------ picture
def layerfig():
    o = t(320, 16, 'Where each pattern sits in a request path', 11, 'ink', bold=True)
    nodes = [('Users', 'green'), ('CDN', 'violet'), ('Load balancer', 'amber'), ('App (ASG)', 'blue'), ('Cache', 'red'), ('Database', 'violet')]
    for i, (n, tn) in enumerate(nodes):
        x = 12 + i * 104
        o += box(x, 40, 92, 44, tn, rx=8) + t(x + 46, 66, n, 7.8, 'ink', bold=True)
        if i < 5: o += arrow(x + 92, 62, x + 104, 62)
    pats = [(1, 'edge caching'), (2, 'load balancing'), (3, 'auto scaling'), (4, 'cache-aside'), (3, 'retry + backoff · circuit breaker')]
    for j, (i, p) in enumerate(pats):
        x = 12 + i * 104 + 46; y = 110 + (j % 2) * 26 + (30 if j == 4 else 0)
        o += f'<path d="M{x},86 L{x},{y - 10}" style="stroke:currentColor;stroke-width:1;stroke-dasharray:3 3;opacity:.5"/>' + t(x, y, p, 7.2, 'ink', bold=True)
    o += box(430, 182, 196, 44, 'card', rx=6) + t(528, 200, 'Queue-based load leveling', 7.8, 'ink', bold=True) + t(528, 215, 'app → queue → workers → DB', 7, 'ink2')
    o += arrow(412, 86, 470, 180)
    o += t(320, 242, 'Each pattern solves one problem; together they make the tier elastic and failure-tolerant.', 7.4, 'ink2')
    return o
LAYER = bigfig('A request path users → CDN → load balancer → app in an auto scaling group → cache → database, labelled with patterns: edge caching, load balancing, auto scaling, cache-aside, retry with backoff and circuit breaker, plus queue-based load leveling for writes.', layerfig(), h=252)

def probfig():
    o = t(320, 16, 'Problem → pattern', 11, 'ink', bold=True)
    rows = [('Too much traffic for one server', 'Load balancing', 'blue'), ('Traffic changes during the day', 'Auto scaling', 'green'), ('Same data read again and again', 'Cache-aside', 'red'), ('Users far away, static content', 'CDN / edge caching', 'violet'),
            ('Write bursts overload the database', 'Queue-based load leveling', 'amber'), ('Brief network glitches', 'Retry + exponential backoff + jitter', 'blue'), ('A dependency is failing or slow', 'Circuit breaker', 'red')]
    for i, (p, s, tn) in enumerate(rows):
        y = 30 + i * 30
        o += box(20, y, 300, 24, 'card', rx=4) + t(170, y + 16, p, 7.6, 'ink') + arrow(322, y + 12, 346, y + 12) + box(348, y, 272, 24, tn, rx=4) + t(484, y + 16, s, 7.6, 'ink', bold=True)
    return o
PROB = bigfig('Seven rows mapping problems to patterns: too much traffic to load balancing; changing traffic to auto scaling; repeated reads to cache-aside; distant users to CDN; write bursts to queue-based load leveling; glitches to retry with backoff and jitter; failing dependency to circuit breaker.', probfig(), h=246)

picture = ('  <p>Where the patterns live in a typical request path:</p>\n' + LAYER + '\n  <p>And which problem each one solves:</p>\n' + PROB)

# ------------------------------------------------------------------ how: Diwali spike
RN = {'u': (4, 54, 54, 50, 'phone', 'Spike', '×12 users'), 'cdn': (66, 4, 60, 46, 'globe', 'CDN', '90% hits'), 'lb': (66, 104, 60, 46, 'lb', 'Load bal.', 'spread'),
      'asg': (138, 54, 62, 50, 'meter', 'Auto Scaling', '2 → 10'), 'cache': (212, 4, 64, 46, 'chip', 'Cache', 'menu hit'), 'q': (212, 104, 64, 46, 'dns', 'Queue', 'buffer writes'), 'cb': (290, 54, 66, 50, 'shield', 'Breaker', 'payments open')}
RS = [dict(on=['u', 'cdn'], hot='cdn', move=(58, 70, 70, 40, 'static'), head='Step 1 · The CDN absorbs static traffic', text='Photos, JS and CSS are served from edge caches — most of the 12× spike never', text2='reaches TiffinGo’s servers.', svc='CloudFront · Front Door · Cloud CDN'),
      dict(on=['u', 'cdn', 'lb'], hot='lb', move=(28, 104, 66, 128, 'API'), head='Step 2 · The load balancer spreads API calls', text='Requests go to the least-busy healthy servers across AZs; overloaded or failing', text2='ones get fewer or none.', svc='Least outstanding requests / round robin + health checks'),
      dict(on=['u', 'cdn', 'lb', 'asg'], hot='asg', move=(126, 127, 150, 90, 'scale'), head='Step 3 · Auto scaling adds servers', text='CPU passes the 50% target; the group grows from 2 to 10 instances in a few minutes', text2='(scheduled scaling had already raised the minimum at 7:30 p.m.).', svc='Target tracking + scheduled / predictive scaling (Lesson 5.3)'),
      dict(on=['u', 'cdn', 'lb', 'asg', 'cache'], hot='cache', move=(200, 70, 222, 40, 'GET'), head='Step 4 · Cache-aside protects the database', text='“menu:pune:today” is read from Redis 4,000 times a second; the database answers', text2='only on a miss, once every 5 minutes.', svc='ElastiCache / Azure Managed Redis / Memorystore'),
      dict(on=['u', 'cdn', 'lb', 'asg', 'cache', 'q'], hot='q', move=(200, 90, 222, 120, 'enqueue'), head='Step 5 · The queue levels the writes', text='Order confirmations, SMS and invoices go to a queue; workers process them at a', text2='steady rate the database can handle.', svc='SQS · Service Bus · Pub/Sub'),
      dict(on=list(RN), hot='cb', move=(276, 127, 298, 90, 'trip'), head='Step 6 · The circuit breaker fails fast', text='Payments time out repeatedly → the breaker opens; for 30 s calls fail instantly and', text2='the app offers “pay on delivery” instead of freezing. Then it tests again.', svc='Timeouts + retries with jitter + circuit breaker')]
SPIKE = flow_anim('Diwali spike: seven patterns working together', 'How the patterns keep the app fast and alive under a 12× surge.', 'Patterns in action', 'Animation: CDN absorbs static traffic; load balancer spreads requests; auto scaling adds servers; cache serves menu reads; queue buffers writes; circuit breaker isolates slow payments.', RN, RS, hid='patflow')

# ------------------------------------------------------------------ types
def mapfig():
    o = t(320, 16, 'Seven cloud design patterns', 11, 'ink', bold=True)
    items = [('1', 'Load balancing', 'spread requests', 'blue'), ('2', 'Auto scaling', 'capacity follows load', 'green'), ('3', 'Cache-aside', 'read from memory first', 'red'),
             ('4', 'CDN / edge caching', 'answer near users', 'violet'), ('5', 'Queue-based leveling', 'buffer bursts', 'amber'), ('6', 'Retry + backoff + jitter', 'survive glitches', 'blue'), ('7', 'Circuit breaker', 'fail fast, recover', 'red')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 12 + (i % 4) * 156; y = 32 + (i // 4) * 84
        o += box(x, y, 148, 70, tn, rx=8) + pin(x + 16, y + 16, n) + t(x + 80, y + 34, a, 7.8, 'ink', bold=True) + t(x + 78, y + 54, b, 6.8, 'ink2')
    o += t(320, 210, '1–2 scale the compute · 3–4 cache reads · 5 smooths writes · 6–7 handle failures between services.', 7.6, 'ink2')
    return o
MAP = bigfig('Map of seven patterns: load balancing, auto scaling, cache-aside, CDN edge caching, queue-based load leveling, retry with exponential backoff and jitter, circuit breaker.', mapfig(), h=222)

def a_lb(k):
    o = t(180, 12, ['Round robin', 'Least outstanding requests', 'Hash / sticky'][k], 9, 'ink', bold=True)
    o += box(14, 54, 70, 40, 'green', rx=6) + t(49, 78, 'requests', 7.2, 'ink') + box(110, 44, 80, 60, 'amber', rx=8) + t(150, 78, 'LB', 8, 'ink', bold=True) + arrow(86, 74, 108, 74)
    loads = [[3, 3, 3], [5, 1, 2], [4, 0, 5]][k]
    for i, l in enumerate(loads):
        o += box(230, 30 + i * 40, 110, 32, 'blue', rx=4) + t(250, 50 + i * 40, f'srv {i + 1}', 7, 'ink', bold=True)
        for d in range(l): o += box(272 + d * 12, 38 + i * 40, 9, 16, 'red' if (k == 1 and i == 1 and d == 0) else 'card', rx=1)
        o += arrow(192, 74, 228, 46 + i * 40)
    o += t(180, 150, ['next request to the next server in turn', 'next request to the server with fewest in-flight requests (srv 2)', 'same user/key → same server (sessions, caches) — uneven load risk'][k], 7.2, 'ink', bold=True)
    return o
A_LB = cap([a_lb(k) for k in range(3)], [('Round robin', 'Requests are handed to servers in turn.', ''), ('Least outstanding', 'New requests go to the server with the fewest in-flight requests.', ''), ('Hash / sticky', 'A key (client IP, cookie) always maps to the same server.', '')],
    'Load balancing algorithms', 'How the balancer picks a server.', 'Load balancing', 'Animation: round robin; least outstanding requests; hash-based sticky routing.', 'q1anim')
T1 = vtype(1, 'Load balancing', 'blue',
    'The <b>load balancing pattern</b> places a balancer in front of a pool of interchangeable instances and distributes requests among the healthy ones using an algorithm — round robin, least outstanding requests/connections, weighted, or hash-based (sticky) — so no single instance is overloaded and failed instances are bypassed.',
    'The token system at a passport office: a dispatcher sends each person to whichever counter is free, and skips the counter whose officer is on leave.',
    'TiffinGo’s ALB uses “least outstanding requests” because some API calls (order placement) take 10× longer than others (menu); round robin left one server choking while others idled.',
    'AWS ALB/NLB/GWLB; Azure Load Balancer, Application Gateway, Front Door; Google Cloud Load Balancing; NGINX/HAProxy on VMs.',
    'Load balancer types (L4/L7) are in Lesson 6.3.', A_LB,
    'more than one instance serves the same workload.',
    'you rely on sticky sessions for state — use an external session store instead.',
    plain='A dispatcher that sends each visitor to a server that is free and healthy, so the work is shared.',
    how=[('Register targets', 'Instances/containers/IPs in a target group or backend pool.'), ('Health checks', 'Only healthy targets receive traffic.'), ('Pick a target', 'Algorithm per request (L7) or per connection/flow (L4).'), ('Forward', 'Optionally terminate TLS and add headers (X-Forwarded-For).'), ('Drain', 'Deregistering targets finish in-flight requests first.')],
    words=[('round robin', 'take turns'), ('least outstanding requests', 'the one with the fewest unfinished requests'), ('sticky session', 'the same user always goes to the same server'), ('connection draining', 'letting current requests finish before removal')],
    diff=table(['Algorithm', 'Good for', 'Watch out'], [['Round robin', 'similar, short requests', 'uneven request costs'], ['Least outstanding / connections', 'variable request times', 'slightly more state in the LB'], ['Hash / sticky', 'session or cache affinity', 'hot spots, uneven load']], minw=480),
    where=['Every multi-instance web/API tier', 'Database read replicas (proxies)', 'Global traffic across Regions'],
    realworld='AWS added the “least outstanding requests” algorithm to ALB in 2019 for exactly TiffinGo’s problem: mixed fast and slow requests on the same target group.',
    pro='Slow start mode gives a newly added instance a gradually increasing share of traffic — without it, a fresh instance with a cold cache and JIT compiler gets a full share instantly and can fail its first health checks under load.')

def a_as(k):
    o = t(180, 12, ['Metric crosses target', 'Group adds instances', 'Load drops → scale in'][k], 9, 'ink', bold=True)
    n = [2, 5, 3][k]
    o += box(14, 40, 100, 60, ['red', 'amber', 'green'][k], rx=8) + t(64, 64, ['CPU 82%', 'CPU 55%', 'CPU 31%'][k], 9, 'ink', bold=True) + t(64, 84, 'target 50%', 7, 'ink2')
    for i in range(6): o += box(140 + i * 34, 52, 28, 36, 'blue' if i < n else 'card', rx=3)
    o += t(180, 128, ['the alarm on the group average fires', 'new instances join the load balancer after warm-up', 'extra instances are removed (after cooldown) to save money'][k], 7.2, 'ink', bold=True)
    return o
A_AS = cap([a_as(k) for k in range(3)], [('Detect', 'Average CPU (or requests per target) rises above the target.', ''), ('Scale out', 'Instances are added and registered with the load balancer.', ''), ('Scale in', 'When load falls, extra instances are removed.', '')],
    'Auto scaling in action', 'Capacity follows demand.', 'Auto scaling', 'Animation: CPU above target; instances added; load drops and instances removed.', 'q2anim')
T2 = vtype(2, 'Auto scaling', 'green',
    'The <b>auto scaling pattern</b> automatically adjusts the number of instances in a group to match demand using policies — target tracking on a metric, step rules, schedules or predictions — within minimum and maximum limits, working together with a load balancer and health checks.',
    'A bank opening more counters when the queue grows and closing them in the quiet afternoon.',
    'TiffinGo’s group: minimum 2, maximum 10, target average CPU 50%, plus a scheduled action raising the minimum to 6 at 7:30 p.m. on festival days. Full details are in Lesson 5.3.',
    'EC2 Auto Scaling, Application Auto Scaling (ECS, DynamoDB), Karpenter; Azure VMSS autoscale, Container Apps scale rules; Google MIG autoscaler, GKE autoscalers.',
    'Lesson 5.3 covers scaling types in depth.', A_AS,
    'demand varies and the app tier is stateless.',
    'start-up time is longer than the spike — pre-scale with schedules or keep warm capacity.',
    plain='The cloud adds servers automatically when the app gets busy and removes them when it gets quiet.',
    how=[('Group', 'Launch template + min/max/desired.'), ('Policy', 'Target tracking (e.g. 50% CPU) or schedule.'), ('Alarm', 'Metric crosses the threshold.'), ('Act', 'Launch/terminate; register with LB after health checks.'), ('Cool down', 'Warm-up and cooldown prevent flapping.')],
    words=[('target tracking', 'keep a metric near a chosen value'), ('cooldown', 'waiting time before another scaling action'), ('flapping', 'scaling out and in repeatedly')],
    diff=table(['', 'Auto scaling', 'Load balancing'], [['Changes', 'how many servers', 'which server gets each request'], ['Needs the other?', 'yes, to send traffic to new servers', 'yes, to have enough servers']], minw=420),
    where=['Web and API tiers', 'Worker fleets reading queues', 'Container services'],
    realworld='Scaling on <b>queue depth per instance</b> (backlog per worker) is AWS’s recommended policy for queue workers — CPU can stay low while thousands of messages wait.',
    pro='Scale on the metric closest to user experience: requests per target or latency often react better than CPU for I/O-bound APIs, where CPU stays at 30% while users wait.')

def a_ca(k):
    o = t(180, 12, ['1st request: miss', 'Store in cache with TTL', 'Next requests: hit'][k], 9, 'ink', bold=True)
    o += box(14, 44, 80, 50, 'blue', rx=6) + t(54, 74, 'app', 8, 'ink', bold=True)
    o += box(140, 30, 90, 46, 'red' if k == 2 else 'card', rx=6) + t(185, 52, 'cache', 8, 'ink', bold=True) + t(185, 66, ['empty', 'menu (5 min)', 'HIT 0.5 ms'][k], 6.8, 'ink2')
    o += box(260, 80, 86, 46, 'violet' if k < 2 else 'card', rx=6) + t(303, 102, 'database', 7.6, 'ink', bold=True) + t(303, 116, ['5 ms', 'read once', 'not touched'][k], 6.6, 'ink2')
    o += arrow(96, 62, 138, 54)
    if k < 2: o += arrow(96, 80, 258, 102)
    if k == 1: o += arrow(258, 92, 232, 66) + t(250, 74, 'SET', 6.4, 'ink2')
    o += t(180, 146, ['GET cache → nothing → read the database', 'write the result into the cache with an expiry', 'thousands of reads served from memory'][k], 7.2, 'ink', bold=True)
    return o
A_CA = cap([a_ca(k) for k in range(3)], [('Miss', 'The app checks the cache first; on a miss it reads the database.', ''), ('Populate', 'It stores the result in the cache with a time-to-live (TTL).', ''), ('Hit', 'Following reads come from memory until the TTL expires or the data changes.', '')],
    'Cache-aside in action', 'Read from memory first.', 'Cache-aside', 'Animation: cache miss reads the database; result stored in the cache with a TTL; subsequent reads hit the cache.', 'q3anim')
T3 = vtype(3, 'Cache-aside (lazy loading)', 'red',
    'The <b>cache-aside pattern</b> has the application check a cache before the data store: on a <b>hit</b> it returns the cached value; on a <b>miss</b> it reads the data store, writes the result into the cache with a time-to-live, and returns it; on updates it writes to the store and invalidates or updates the cache entry.',
    'Keeping today’s menu written on a whiteboard at the counter: staff read the board instead of asking the chef every time — and rewrite it when the menu changes.',
    'TiffinGo caches <code>menu:{city}:{date}</code> in Redis for 5 minutes. At Diwali peak 99.9% of menu reads are hits; the database handles 1 query every 5 minutes per city instead of 4,000 a second.',
    'Amazon ElastiCache (Redis OSS/Valkey, Memcached), MemoryDB, DynamoDB Accelerator (DAX); Azure Managed Redis; Google Memorystore; in-process caches.',
    '', A_CA,
    'data is read much more often than written and slightly stale data is acceptable.',
    'every read must be perfectly fresh (balances, stock at checkout) — read from the database or use short TTLs and invalidation.',
    plain='Keep a copy of popular data in fast memory. Look there first; only ask the slow database when the copy is missing or old.',
    how=[('Read', 'GET key from cache.'), ('Hit', 'Return immediately.'), ('Miss', 'Query the database, SET key with TTL, return.'), ('Update', 'Write to database, then delete (or update) the cache key.'), ('Evict', 'Memory full → least recently used keys removed.')],
    words=[('cache hit / miss', 'found / not found in the cache'), ('TTL', 'time to live — when the cached copy expires'), ('invalidation', 'removing a stale cached copy'), ('eviction', 'the cache deleting old entries to free memory')],
    diff=table(['Pattern', 'How writes work', 'Trade-off'], [['Cache-aside', 'app writes DB, invalidates cache', 'simple; possible brief staleness'], ['Write-through', 'app writes cache and DB together', 'cache always fresh; slower writes'], ['Write-behind', 'cache writes DB later', 'fast writes; risk of loss']], minw=520),
    where=['Menus, product catalogues, profiles', 'Session data and leaderboards', 'Expensive computed results'],
    realworld='AWS rebranded ElastiCache’s Redis offering to support <b>Valkey</b>, the Linux Foundation fork created in 2024 after Redis changed its licence — the caching layer of many architectures now runs on Valkey.',
    pro='When a hot key expires, thousands of requests can miss at once and stampede the database. Add jitter to TTLs, let one request refresh while others serve the stale value (“stale-while-revalidate”), or use request coalescing.')

def a_cdn(k):
    o = t(180, 12, ['Static at the edge', 'Cache-control decides', 'Version files to update'][k], 9, 'ink', bold=True)
    o += box(14, 44, 70, 46, 'green', rx=6) + t(49, 72, 'users', 7.4, 'ink') + box(116, 36, 100, 62, 'violet', rx=8) + t(166, 60, 'edge', 8, 'ink', bold=True) + t(166, 78, ['photo HIT', 'max-age=86400', 'app.v42.js'][k], 6.8, 'ink2', mono=(k > 0))
    o += box(256, 44, 90, 46, 'card', rx=6) + t(301, 72, 'origin', 7.4, 'ink') + arrow(86, 67, 114, 67) + arrow(218, 67, 254, 67)
    o += t(180, 130, ['images, JS, CSS, video segments served near users', 'origin headers tell the CDN how long to keep each file', 'new file names instead of invalidating caches'][k], 7.2, 'ink', bold=True)
    return o
A_CDN = cap([a_cdn(k) for k in range(3)], [('Edge', 'Static content is cached at edge locations near users.', ''), ('Policy', 'Cache-Control headers and cache policies set lifetimes.', ''), ('Versioning', 'Changing file names (app.v42.js) updates clients instantly without purges.', '')],
    'Edge caching in action', 'Answer close to the user.', 'CDN', 'Animation: static files served from an edge cache; cache-control headers; versioned file names.', 'q4anim')
T4 = vtype(4, 'CDN / edge caching', 'violet',
    'The <b>edge caching pattern</b> serves cacheable content — static files and, where possible, API responses — from a content delivery network’s edge locations close to users, controlled by cache headers and cache policies, offloading the origin and cutting latency.',
    'Regional warehouses of an e-commerce company: popular items ship from a nearby city instead of the central warehouse.',
    'TiffinGo’s images and JS bundles go through CloudFront with a one-year cache for versioned files; the public “today’s menu” API response is cached at the edge for 60 seconds — at Diwali 90% of requests never reached the origin.',
    'Amazon CloudFront (+ Lambda@Edge, CloudFront Functions), Azure Front Door, Google Cloud CDN / Media CDN.',
    'CDN fundamentals are in Lessons 5.1 and 6.3.', A_CDN,
    'content is the same for many users — static assets, public pages, video, public API responses.',
    'responses are personalised or private — or you cache errors and serve them to everyone.',
    plain='Copies of your files are kept in many cities, so each user gets them from somewhere close — and your servers do less work.',
    how=[('Distribution', 'Origins (bucket, LB) and behaviours per path.'), ('Cache key', 'Path + chosen headers/cookies/query strings.'), ('TTL', 'From Cache-Control / policy.'), ('Invalidate or version', 'Purge paths or use new file names.'), ('Edge logic', 'Small functions for redirects, headers, A/B tests.')],
    words=[('Cache-Control', 'an HTTP header that says how long a response may be cached'), ('cache key', 'what makes two requests “the same”'), ('purge / invalidation', 'removing content from edge caches')],
    diff=table(['', 'CDN cache', 'App cache (Redis)'], [['Location', 'edge, near users', 'next to the app'], ['Caches', 'HTTP responses', 'any data objects'], ['Saves', 'network latency + origin load', 'database load']], minw=440),
    where=['Images, video, downloads', 'Single-page app bundles', 'Public read-only APIs'],
    realworld='Video platforms such as Hotstar (JioHotstar) rely on CDNs for cricket streaming peaks of tens of millions of concurrent viewers — a load no single origin could serve.',
    pro='Use immutable, content-hashed file names (app.3f9a.js) with a one-year max-age and keep index.html short-lived: deploys become instant and you almost never need paid invalidations.')

def a_q(k):
    o = t(180, 12, ['Burst arrives', 'Queue absorbs it', 'Workers drain steadily'][k], 9, 'ink', bold=True)
    o += box(14, 40, 70, 60, 'red' if k == 0 else 'card', rx=6) + t(49, 66, '5,000', 8, 'ink', bold=True) + t(49, 82, 'writes/min', 6.6, 'ink2')
    qn = [0, 9, 4][k]
    o += box(110, 46, 130, 46, 'amber', rx=6)
    for i in range(qn): o += box(116 + i * 13, 54, 10, 30, 'card', rx=1)
    o += box(266, 40, 80, 60, 'blue', rx=6) + t(306, 66, 'workers', 7.6, 'ink', bold=True) + t(306, 82, '500/min', 6.8, 'ink2') + arrow(86, 70, 108, 70) + arrow(242, 70, 264, 70)
    o += t(180, 128, ['the database could not take this rate directly', 'messages wait safely; the app responds “order received”', 'workers process at a rate the database can sustain'][k], 7.2, 'ink', bold=True)
    return o
A_Q = cap([a_q(k) for k in range(3)], [('Burst', 'Writes arrive faster than the back end can process them.', ''), ('Buffer', 'The queue stores them durably; the front end replies immediately.', ''), ('Drain', 'Workers consume at a steady rate; scale workers on queue depth.', '')],
    'Queue-based load leveling in action', 'Smooth bursts into a steady flow.', 'Load leveling', 'Animation: a burst of writes; the queue fills; workers drain it at a steady rate.', 'q5anim')
T5 = vtype(5, 'Queue-based load leveling', 'amber',
    'The <b>queue-based load leveling pattern</b> places a durable queue between a task producer and a service that processes the tasks, so bursts of requests are buffered and consumed at a sustainable rate, protecting the service from overload and keeping the producer responsive.',
    'A dam on a river: monsoon floods fill the reservoir, and the gates release water at a steady rate the canals can handle.',
    'At Diwali, invoice generation and SMS go to SQS; 4 workers process 500 jobs a minute. When the queue passes 2,000 messages, worker auto scaling adds more — the order API never slows down.',
    'Amazon SQS (+ Lambda/ECS consumers), Azure Service Bus / Storage Queues (+ Functions), Google Pub/Sub / Cloud Tasks.',
    'Messaging services were introduced in Lesson 6.4.', A_Q,
    'work can be done slightly later and arrives in bursts.',
    'the user needs the result immediately in the same request.',
    plain='Put incoming jobs in a waiting line so the back end can work through them steadily instead of being flooded.',
    how=[('Produce', 'Front end sends a message per task and replies at once.'), ('Store', 'The queue keeps messages durably.'), ('Consume', 'Workers poll, process, delete.'), ('Scale', 'Worker count follows queue depth.'), ('Fail safely', 'Retries and a dead-letter queue for poison messages.')],
    words=[('buffer', 'temporary storage that absorbs bursts'), ('backlog', 'messages waiting in the queue'), ('poison message', 'a message that always fails processing'), ('DLQ', 'dead-letter queue — where failed messages are parked')],
    diff=table(['', 'Load leveling (queue)', 'Auto scaling'], [['Handles bursts by', 'waiting', 'adding capacity'], ['User waits?', 'no (async)', 'yes (sync)'], ['Best combined?', 'yes — scale workers on queue depth', 'yes']], minw=440),
    where=['Order processing and notifications', 'Video/image processing', 'Imports and batch updates'],
    realworld='Ticketing sites use virtual waiting rooms — a queue in front of the checkout — during big sales so the payment and inventory systems see a steady flow instead of a stampede.',
    pro='A queue hides overload — until it doesn’t. Alarm on the <b>age of the oldest message</b>, not just queue length: 10,000 messages processed in 2 minutes is fine; 50 messages stuck for an hour is an incident.')

def a_retry(k):
    o = t(180, 12, ['Immediate retries: storm', 'Exponential backoff', 'Backoff + jitter'][k], 9, 'ink', bold=True)
    o += f'<path d="M20,110 L340,110" style="stroke:currentColor;stroke-width:1;opacity:.4"/>' + t(330, 124, 'time →', 6.6, 'ink2', anchor='end')
    if k == 0:
        for c in range(4):
            for r in range(4): o += f'<circle cx="{40 + r * 10}" cy="{40 + c * 16}" r="4" style="fill:#D64545"/>'
        o += t(200, 70, 'all clients retry at once, again and again', 7.4, 'ink')
    else:
        for c in range(4):
            for r, base in enumerate([0, 20, 60, 140]):
                x = 40 + base + (c * 7 * r if k == 2 else 0)
                o += f'<circle cx="{x}" cy="{40 + c * 16}" r="4" style="fill:{"#2E8B57" if k == 2 else "#E0A100"}"/>'
        o += t(270, 26 if k == 2 else 70, ['waits 0.1, 0.2, 0.4, 0.8 s…', 'random spread breaks the sync'][k - 1], 7.2, 'ink')
    o += t(180, 146, ['a brief glitch becomes a self-inflicted overload', 'waits grow exponentially — but clients still retry together', 'random jitter spreads retries; add a retry limit'][k], 7.2, 'ink', bold=True)
    return o
A_RETRY = cap([a_retry(k) for k in range(3)], [('Naive retries', 'Every client retries instantly — a retry storm multiplies load.', ''), ('Backoff', 'Wait 2× longer after each failure.', ''), ('Jitter', 'Add randomness so clients do not retry in lock-step; cap the attempts.', '')],
    'Retry with backoff and jitter in action', 'Retry politely.', 'Retries', 'Animation: synchronised immediate retries causing a storm; exponential backoff; backoff with random jitter spreading retries.', 'q6anim')
T6 = vtype(6, 'Retry with exponential backoff and jitter', 'blue',
    'The <b>retry pattern</b> handles transient faults by retrying failed operations; <b>exponential backoff</b> increases the wait between attempts (e.g. 100 ms, 200 ms, 400 ms…) and <b>jitter</b> randomises it so many clients do not retry simultaneously, with a maximum number of attempts and only for safe (idempotent) operations.',
    'Calling a busy customer-care number: if it is engaged, you wait a minute, then two, then four — and everyone else waits a different random time, so the line is not flooded at the same second.',
    'TiffinGo’s app retries a failed menu fetch up to 3 times with “full jitter” backoff; order placement retries carry an idempotency key so a retry never creates two orders. The AWS SDKs do this by default.',
    'Built into AWS SDKs (standard/adaptive retry modes), Azure SDK retry policies, Google client libraries; libraries like Polly (.NET), resilience4j (Java), tenacity (Python).',
    '', A_RETRY,
    'errors are transient — throttling (429), timeouts, brief network issues.',
    'the error is permanent (400, 403) or the operation is not idempotent without a key — retries make it worse.',
    plain='If something fails for a moment, try again — but wait a bit longer each time and add a random delay, so everyone does not retry at the same instant.',
    how=[('Classify', 'Retry only transient errors (timeouts, 429, 503).'), ('Wait', 'base × 2^attempt, capped.'), ('Jitter', 'random(0, wait) — “full jitter”.'), ('Limit', 'Max attempts and a total time budget.'), ('Idempotency', 'Safe to repeat — or use an idempotency key.')],
    words=[('transient fault', 'a short, temporary error'), ('exponential backoff', 'waiting longer each time, doubling'), ('jitter', 'random variation in the wait'), ('idempotent', 'doing it twice has the same effect as once')],
    diff=table(['', 'Retry + backoff', 'Circuit breaker'], [['For', 'short glitches', 'longer failures'], ['Action', 'try again later', 'stop trying for a while'], ['Used together?', 'yes — retries inside, breaker around', 'yes']], minw=440),
    where=['Every network call to cloud APIs and services', 'Mobile apps on flaky networks', 'Queue consumers'],
    realworld='The AWS Architecture Blog’s analysis “Exponential Backoff and Jitter” showed that adding full jitter dramatically reduces the total work and completion time compared with plain exponential backoff — the reason SDKs use it by default.',
    pro='Retries multiply across layers: 3 retries in the app × 3 in the SDK × 3 in the load balancer = up to 27 calls for one user click. Retry at one layer, close to the client, and use a retry budget.')

def a_cb(k):
    o = t(180, 12, ['Closed: calls pass', 'Open: fail fast', 'Half-open: test, then close'][k], 9, 'ink', bold=True)
    o += box(14, 44, 80, 50, 'blue', rx=6) + t(54, 74, 'order svc', 7.6, 'ink', bold=True)
    o += box(130, 40, 100, 58, ['green', 'red', 'amber'][k], rx=8) + t(180, 64, 'breaker', 8, 'ink', bold=True) + t(180, 82, ['CLOSED', 'OPEN 30 s', 'HALF-OPEN'][k], 7.4, 'ink', bold=True)
    o += box(266, 44, 80, 50, 'violet' if k != 1 else 'card', rx=6) + t(306, 66, 'payments', 7.4, 'ink', bold=True) + t(306, 82, ['ok', 'slow ✘', '1 test call'][k], 6.6, 'ink2')
    o += arrow(96, 69, 128, 69)
    if k != 1: o += arrow(232, 69, 264, 69)
    o += t(180, 128, ['failures are counted; below the threshold all calls go through', 'after 5 failures calls fail instantly → fallback “pay on delivery”', 'after the wait one trial call: success closes, failure re-opens'][k], 7.2, 'ink', bold=True)
    return o
A_CB = cap([a_cb(k) for k in range(3)], [('Closed', 'Calls pass through; failures are counted.', ''), ('Open', 'Too many failures: calls fail immediately and a fallback is used.', ''), ('Half-open', 'After a timeout a trial call checks recovery.', '')],
    'Circuit breaker in action', 'Stop hammering a failing service.', 'Circuit breaker', 'Animation: breaker closed with calls passing; open after failures with fast fallback; half-open trial call.', 'q7anim')
T7 = vtype(7, 'Circuit breaker', 'red',
    'The <b>circuit breaker pattern</b> wraps calls to a remote dependency and tracks failures; when failures exceed a threshold it <b>opens</b> and fails calls immediately (often with a fallback) for a period, then lets a few trial calls through (<b>half-open</b>) and <b>closes</b> again if they succeed — preventing cascading failures and giving the dependency time to recover.',
    'The electrical MCB in your house: when a fault draws too much current it trips at once to protect the wiring; you reset it after the fault is fixed.',
    'When the payment provider slowed to 8 seconds, TiffinGo’s threads all waited and the whole app froze. Now a breaker with a 2-second timeout opens after 5 failures; for 30 seconds checkout offers “pay on delivery”, and menu browsing stays fast.',
    'Libraries: resilience4j, Polly, Hystrix (retired), Envoy/Istio outlier detection; managed: App Mesh successors/Service mesh policies, Azure API Management circuit breaker, Apigee; Step Functions error handling.',
    '', A_CB,
    'a call to another service can fail or slow down — payments, third-party APIs, other microservices.',
    'there is no sensible fallback and the caller must wait — then use timeouts and clear errors instead.',
    plain='If another service keeps failing, stop calling it for a while and use a backup plan, instead of waiting and getting stuck. Try again later.',
    how=[('Wrap', 'All calls to the dependency go through the breaker.'), ('Count', 'Errors/timeouts in a rolling window.'), ('Open', 'Threshold reached → fail fast + fallback.'), ('Wait', 'Open for N seconds.'), ('Half-open', 'Trial calls decide close or re-open.')],
    words=[('cascading failure', 'one failure causing failures upstream'), ('fallback', 'the backup behaviour when a call fails'), ('timeout', 'the maximum time to wait for a reply'), ('half-open', 'testing state after a pause')],
    diff=table(['', 'Circuit breaker', 'Timeout only'], [['Stops calling a dead service', 'yes', 'no — every call waits the timeout'], ['Protects caller threads', 'yes', 'partly'], ['Gives the dependency time to recover', 'yes', 'no']], minw=440),
    where=['Payments and third-party APIs', 'Microservice-to-microservice calls', 'Service meshes and API gateways'],
    realworld='Netflix popularised circuit breakers with its open-source Hystrix library (2012); it is now in maintenance mode and the industry moved to resilience4j and to breakers built into service meshes like Istio/Envoy.',
    pro='Every remote call needs a <b>timeout</b> shorter than the caller’s own timeout — otherwise the breaker never sees failures quickly enough, and threads pile up long before it opens.')

SUMMARY = table(['#', 'Pattern', 'Problem', 'Cloud services'], [
    ['1', 'Load balancing', 'one server can’t handle the load', 'ALB/NLB · LB/App Gateway · Cloud LB'], ['2', 'Auto scaling', 'load changes over time', 'ASG · VMSS autoscale · MIG autoscaler'], ['3', 'Cache-aside', 'repeated reads overload the DB', 'ElastiCache · Managed Redis · Memorystore'],
    ['4', 'CDN / edge caching', 'distant users, static content', 'CloudFront · Front Door · Cloud CDN'], ['5', 'Queue-based leveling', 'write bursts', 'SQS · Service Bus · Pub/Sub'], ['6', 'Retry + backoff + jitter', 'transient faults', 'SDK retry policies'], ['7', 'Circuit breaker', 'failing/slow dependency', 'resilience libraries, service mesh, APIM']], minw=640)
CHECK = ('  <h3>Check yourself: which pattern?</h3>\n' +
    qx('A. The same product page is read 10,000 times a minute from the database.', ['Circuit breaker', 'Cache-aside', 'Queue', 'Sharding'], 1, 'Read from memory.') +
    qx('B. A third-party SMS API is down and your threads are all waiting on it.', ['Retry immediately', 'Circuit breaker with timeout and fallback', 'Bigger instance', 'CDN'], 1, 'Fail fast.') +
    qx('C. A nightly import sends 1 million updates in 5 minutes.', ['Queue-based load leveling', 'CDN', 'Sticky sessions', 'DNS'], 0, 'Buffer the burst.') +
    qx('D. Thousands of mobile clients retry at the same moment after an outage.', ['Remove retries', 'Exponential backoff with jitter', 'Bigger load balancer', 'Static IPs'], 1, 'Spread retries.'))

TYPES = ('  <p>Seven patterns, each in the same pattern: definition, plain words, analogy, internal steps, animation, differences, where used, real-world example, TiffinGo scenario and an expert note.</p>\n'
         + challenge(['How can 3 retries become 27 calls for one click?', 'What is a cache stampede and how do you prevent it?', 'Which queue metric should you alarm on — length or age?'], 'patterns 6, 3 and 5') + MAP
         + jump(['Load balancing', 'Auto scaling', 'Cache-aside', 'CDN', 'Queue', 'Retry', 'Circuit breaker']) + T1 + T2 + T3 + T4 + T5 + T6 + T7
         + '\n  <h3 style="margin-top:34px">All seven side by side</h3>\n' + SUMMARY + '\n' + CHECK)

parts = wwu([
    ('Health check', 'Probe that decides if a target gets traffic.', 'Feeds load balancing and auto scaling.', 'LB target health, MIG autohealing.'),
    ('Idempotency key', 'A unique ID per operation.', 'Makes retries safe (no double orders).', 'Payment APIs, SQS FIFO deduplication.'),
    ('TTL', 'How long cached data is valid.', 'Balances freshness and load.', 'Redis EXPIRE, Cache-Control max-age.'),
    ('Dead-letter queue', 'Holding area for failed messages.', 'Stops poison messages blocking work.', 'SQS DLQ, Service Bus DLQ, Pub/Sub dead-letter topic.'),
    ('Timeout', 'Maximum wait for a call.', 'Without it, breakers and retries cannot work.', 'SDK and HTTP client settings.'),
    ('Sharding', 'Splitting data across nodes by key.', 'Scales writes beyond one database.', 'DynamoDB partitions, Cosmos DB partition keys, Spanner splits.')])

DEEP = ('  <h3>More patterns worth knowing</h3>\n' + table(['Pattern', 'One-line idea'], [['Bulkhead', 'separate resource pools so one failing dependency cannot use all threads'], ['Throttling / rate limiting', 'limit requests per client to protect the service (429)'], ['CQRS', 'separate models for writes and reads (e.g. DB for writes, search index for reads)'], ['Event sourcing', 'store every change as an event; rebuild state by replay'], ['Sidecar', 'helper process next to each service (proxy, logging) — the basis of service meshes'], ['Ambassador / gateway offloading', 'move TLS, auth, retries into a gateway'], ['Saga', 'multi-step transaction with compensations (Lesson 7.4)'], ['Static content hosting', 'serve static files from object storage + CDN (Lesson 7.3)']], minw=520) +
    '\n  <p>Microsoft’s Azure Architecture Center keeps the best-known catalogue of cloud design patterns; AWS Prescriptive Guidance and Google’s Architecture Center describe the same patterns with their services.</p>\n'
    '  <h3>Patterns combine</h3>\n  <p>Retries live inside a circuit breaker; auto scaling needs load balancing; caching needs TTLs and invalidation; queues need idempotent consumers and DLQs. Draw the combination for each dependency in your architecture.</p>')

clouds = vendor_tabs('<p><b>AWS:</b> ELB (ALB/NLB), EC2 Auto Scaling, Application Auto Scaling, ElastiCache/MemoryDB/DAX, CloudFront, SQS with DLQs, SDK retry modes, API Gateway throttling, Route 53 health checks.</p>',
    '<p><b>Azure:</b> Load Balancer, Application Gateway, Front Door, VMSS autoscale, Container Apps scale rules, Azure Managed Redis, Service Bus with DLQs, SDK retry policies, API Management (rate limits, circuit breaker).</p>',
    '<p><b>Google Cloud:</b> Cloud Load Balancing, MIG autoscaler, GKE autoscaling, Memorystore, Cloud CDN, Pub/Sub dead-letter topics, client-library retries, Apigee policies.</p>') + \
    cloud3([['Load balancing', 'ALB / NLB', 'App Gateway / Load Balancer', 'Cloud Load Balancing'], ['Auto scaling', 'EC2 Auto Scaling', 'VMSS autoscale', 'MIG autoscaler'], ['App cache', 'ElastiCache', 'Azure Managed Redis', 'Memorystore'], ['CDN', 'CloudFront', 'Front Door', 'Cloud CDN'], ['Queue', 'SQS', 'Service Bus', 'Pub/Sub'], ['API rate limits', 'API Gateway', 'API Management', 'Apigee']])

# ------------------------------------------------------------------ practical
WEB_AL = '#!/bin/bash\ndnf install -y nginx\necho "<h1>served by $(hostname)</h1>" > /usr/share/nginx/html/index.html\nsystemctl enable --now nginx'
WEB_DEB = '#!/bin/bash\napt-get update && apt-get install -y nginx\necho "<h1>served by $(hostname)</h1>" > /var/www/html/index.html\nsystemctl enable --now nginx'

MOCKQ.extend([
 (mock('aws', ['EC2', 'Load balancers', 'Create Application Load Balancer'], ['Load Balancers', 'Target Groups', 'Auto Scaling Groups'], 'Load Balancers',
       [('Name · Scheme', 'tiffingo-alb · Internet-facing'), ('Mappings', '[x] ap-south-1a · [x] ap-south-1b'), ('Security groups', '▾ tiffingo-web-sg'), ('Listener HTTP:80 → forward to', '▾ tiffingo-tg')], 'Create load balancer'),
  mock('az', ['Home', 'Virtual machine scale sets', 'Create', 'Networking'], ['Basics', 'Disks', 'Networking', 'Scaling', 'Advanced'], 'Networking',
       [('Load balancing options', '( ) Azure load balancer'), ('Select a load balancer', '▾ (new) tiffingo-vmss-lb'), ('Inbound ports', 'HTTP (80)')], 'Review + create'),
  mock('gcp', ['Network services', 'Load balancing', 'Create load balancer'], ['Load balancing', 'Cloud CDN', 'Health checks'], 'Load balancing',
       [('Type', '( ) Application Load Balancer (HTTP/S)'), ('Public facing · Global', '( ) Public · Global'), ('Backend', 'web-bs → instance group web-mig, health check web-hc'), ('Frontend', 'HTTP · port 80')], 'Create')),
 (mock('aws', ['EC2', 'Auto Scaling groups', 'tiffingo-web-asg', 'Create dynamic scaling policy'], ['Details', 'Automatic scaling', 'Instance management'], 'Automatic scaling',
       [('Policy type', '▾ Target tracking scaling'), ('Metric type', '▾ Average CPU utilization'), ('Target value', '50')], 'Create'),
  mock('az', ['Home', 'tiffingo-vmss', 'Scaling'], ['Overview', 'Instances', 'Scaling', 'Networking'], 'Scaling',
       [('Choose how to scale', '( ) Custom autoscale'), ('Scale out rule', 'CPU > 50% (avg 5 min) → +1'), ('Instance limits', 'min 2 · max 4 · default 2')], 'Save'),
  mock('gcp', ['Compute Engine', 'Instance groups', 'web-mig', 'Edit'], ['Details', 'Autoscaling', 'Autohealing'], 'Autoscaling',
       [('Autoscaling mode', '▾ On: add and remove instances'), ('Signal', 'CPU utilization 50%'), ('Min · Max', '2 · 4')], 'Save')),
 (mock('aws', ['EC2', 'Target groups', 'tiffingo-tg'], ['Targets', 'Health checks', 'Monitoring'], 'Targets',
       [('Registered targets', 'i-0aa… healthy · i-0bb… healthy'), ('After stopping one', 'i-0aa… unused (stopped) · i-0bb… healthy')], 'Refresh'),
  mock('az', ['Home', 'tiffingo-vmssLB', 'Backend pools'], ['Overview', 'Frontend IP', 'Backend pools', 'Health probes', 'Load balancing rules'], 'Backend pools',
       [('Health probe', 'http (TCP 80)'), ('Instances', 'tiffingo-vmss_0 running · tiffingo-vmss_1 stopped')], 'Refresh'),
  mock('gcp', ['Network services', 'Load balancing', 'web-lb'], ['Details', 'Monitoring', 'Caching'], 'Details',
       [('Backend web-bs', 'Healthy 2 of 2 → 1 of 2'), ('Cloud CDN', '[x] Enable Cloud CDN (optional)')], 'Refresh')),
])

STEP1 = ('1 · A load-balanced web tier across two zones', tri(
    (['Create security group <code>tiffingo-web-sg</code> allowing HTTP 80 from anywhere (lab).', '[[Launch templates]] → <code>tiffingo-web-lt</code>: Amazon Linux 2023, t3.micro, that SG, [[Advanced details]] → [[User data]] = the script below.', '[[Target groups]] → <code>tiffingo-tg</code> (instances, HTTP 80, health check /). [[Load balancers]] → [[Application Load Balancer]] → internet-facing, AZs 1a + 1b, SG tiffingo-web-sg, listener 80 → tiffingo-tg.', '[[Auto Scaling groups]] → <code>tiffingo-web-asg</code> from the template, subnets 1a + 1b, attach to tiffingo-tg, desired/min 2, max 4, [[ELB]] health checks.'],
     f"cat > web.sh <<'EOF'\n{WEB_AL}\nEOF\nVPC=$(aws ec2 describe-vpcs --filters Name=is-default,Values=true --query 'Vpcs[0].VpcId' --output text)\nSUBS=$(aws ec2 describe-subnets --filters Name=default-for-az,Values=true --query 'Subnets[0:2].SubnetId' --output text)\nSG=$(aws ec2 create-security-group --group-name tiffingo-web-sg --description web --vpc-id $VPC --query GroupId --output text)\naws ec2 authorize-security-group-ingress --group-id $SG --protocol tcp --port 80 --cidr 0.0.0.0/0\naws ec2 create-launch-template --launch-template-name tiffingo-web-lt --launch-template-data \\\n  \"{{\\\"ImageId\\\":\\\"resolve:ssm:/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64\\\",\\\"InstanceType\\\":\\\"t3.micro\\\",\\\"SecurityGroupIds\\\":[\\\"$SG\\\"],\\\"UserData\\\":\\\"$(base64 -w0 web.sh)\\\"}}\"\nTG=$(aws elbv2 create-target-group --name tiffingo-tg --protocol HTTP --port 80 --vpc-id $VPC --query 'TargetGroups[0].TargetGroupArn' --output text)\nLB=$(aws elbv2 create-load-balancer --name tiffingo-alb --subnets $SUBS --security-groups $SG --query 'LoadBalancers[0].LoadBalancerArn' --output text)\naws elbv2 create-listener --load-balancer-arn $LB --protocol HTTP --port 80 --default-actions Type=forward,TargetGroupArn=$TG\naws autoscaling create-auto-scaling-group --auto-scaling-group-name tiffingo-web-asg --launch-template LaunchTemplateName=tiffingo-web-lt \\\n  --min-size 2 --max-size 4 --desired-capacity 2 --vpc-zone-identifier \"$(echo $SUBS | tr ' ' ',')\" \\\n  --target-group-arns $TG --health-check-type ELB --health-check-grace-period 120\nDNS=$(aws elbv2 describe-load-balancers --load-balancer-arns $LB --query 'LoadBalancers[0].DNSName' --output text)\nsleep 180; curl http://$DNS",
     '<code>&lt;h1&gt;served by ip-172-31-…&lt;/h1&gt;</code> from the ALB DNS name, once both targets are healthy (about 3 minutes). The ALB costs a few rupees per hour — delete it after the lab.'),
    (['[[Virtual machine scale sets]] → [[Create]] → rg-tiffingo, <code>tiffingo-vmss</code>, Central India, zones 1, 2, orchestration [[Uniform]], Ubuntu 24.04, Standard_B1s, 2 instances.', '[[Networking]] → [[Load balancing options]] → [[Azure load balancer]] → create new; allow inbound HTTP 80. [[Advanced]] → [[Custom data]] = the Ubuntu script.', 'After creation: load balancer → [[Health probes]] → add TCP 80; [[Load balancing rules]] → add port 80 → 80 using that probe.'],
     f"cat > web.sh <<'EOF'\n{WEB_DEB}\nEOF\naz group create --name rg-tiffingo --location centralindia\naz network nsg create --resource-group rg-tiffingo --name web-nsg\naz network nsg rule create --resource-group rg-tiffingo --nsg-name web-nsg --name http --priority 100 \\\n  --access Allow --protocol Tcp --destination-port-ranges 80\naz vmss create --resource-group rg-tiffingo --name tiffingo-vmss --orchestration-mode Uniform --image Ubuntu2404 \\\n  --vm-sku Standard_B1s --instance-count 2 --zones 1 2 --lb-sku Standard --nsg web-nsg \\\n  --upgrade-policy-mode Automatic --custom-data web.sh --admin-username azureuser --generate-ssh-keys\nLBN=$(az network lb list --resource-group rg-tiffingo --query '[0].name' --output tsv)\nFE=$(az network lb frontend-ip list --resource-group rg-tiffingo --lb-name $LBN --query '[0].name' --output tsv)\nBP=$(az network lb address-pool list --resource-group rg-tiffingo --lb-name $LBN --query '[0].name' --output tsv)\naz network lb probe create --resource-group rg-tiffingo --lb-name $LBN --name http --protocol tcp --port 80\naz network lb rule create --resource-group rg-tiffingo --lb-name $LBN --name http --protocol tcp --frontend-port 80 \\\n  --backend-port 80 --frontend-ip-name $FE --backend-pool-name $BP --probe-name http\nIP=$(az network public-ip list --resource-group rg-tiffingo --query '[0].ipAddress' --output tsv)\nsleep 120; curl http://$IP",
     '<code>served by tiffingo-vmss000000</code> (or 000001) from the load balancer’s public IP.'),
    (['[[Instance templates]] → <code>web-tpl</code>: e2-micro, Debian 12, network tag <code>http-server</code>, startup script = the Debian script.', '[[Instance groups]] → managed, multiple zones in asia-south1, 2 instances, port mapping http:80. Firewall: allow tcp:80 to tag http-server.', '[[Load balancing]] → [[Create load balancer]] → Application Load Balancer, public, global → backend = the group with an HTTP health check; frontend HTTP 80 → [[Create]] (ready in ~5 minutes).'],
     f"cat > web.sh <<'EOF'\n{WEB_DEB}\nEOF\ngcloud compute instance-templates create web-tpl --machine-type=e2-micro --image-family=debian-12 \\\n  --image-project=debian-cloud --tags=http-server --metadata-from-file=startup-script=web.sh\ngcloud compute firewall-rules create allow-http-web --allow=tcp:80 --target-tags=http-server\ngcloud compute instance-groups managed create web-mig --region=asia-south1 --template=web-tpl --size=2\ngcloud compute instance-groups managed set-named-ports web-mig --region=asia-south1 --named-ports=http:80\ngcloud compute health-checks create http web-hc --port=80\ngcloud compute backend-services create web-bs --protocol=HTTP --port-name=http --health-checks=web-hc --global\ngcloud compute backend-services add-backend web-bs --instance-group=web-mig --instance-group-region=asia-south1 --global\ngcloud compute url-maps create web-map --default-service=web-bs\ngcloud compute target-http-proxies create web-proxy --url-map=web-map\ngcloud compute forwarding-rules create web-fr --global --target-http-proxy=web-proxy --ports=80\nIP=$(gcloud compute forwarding-rules describe web-fr --global --format='value(IPAddress)')\nsleep 300; curl http://$IP",
     '<code>served by web-mig-xxxx</code> from one global anycast IP (the first minutes may return 404/502 while the LB programs).')),
    'One address in front, two servers in two zones behind it — the base of every scalable web tier.')

STEP2 = ('2 · Add a target-tracking auto scaling policy', tri(
    (['Group → [[Automatic scaling]] → [[Create dynamic scaling policy]] → [[Target tracking scaling]], metric [[Average CPU utilization]], target 50 → [[Create]].'],
     "aws autoscaling put-scaling-policy --auto-scaling-group-name tiffingo-web-asg --policy-name cpu50 \\\n  --policy-type TargetTrackingScaling \\\n  --target-tracking-configuration '{\"PredefinedMetricSpecification\":{\"PredefinedMetricType\":\"ASGAverageCPUUtilization\"},\"TargetValue\":50}'\naws autoscaling describe-policies --auto-scaling-group-name tiffingo-web-asg --query 'ScalingPolicies[].[PolicyName,PolicyType]' --output table",
     '<code>cpu50 TargetTrackingScaling</code>; CloudWatch alarms for high and low CPU are created for you.'),
    (['Scale set → [[Scaling]] → [[Custom autoscale]] → instance limits min 2, max 4 → [[Add a rule]]: Percentage CPU &gt; 50 for 5 minutes → increase by 1; add a scale-in rule &lt; 30 → decrease by 1 → [[Save]].'],
     'az monitor autoscale create --resource-group rg-tiffingo --resource tiffingo-vmss \\\n  --resource-type Microsoft.Compute/virtualMachineScaleSets --name web-autoscale --min-count 2 --max-count 4 --count 2\naz monitor autoscale rule create --resource-group rg-tiffingo --autoscale-name web-autoscale \\\n  --condition "Percentage CPU > 50 avg 5m" --scale out 1\naz monitor autoscale rule create --resource-group rg-tiffingo --autoscale-name web-autoscale \\\n  --condition "Percentage CPU < 30 avg 5m" --scale in 1',
     'an autoscale setting with two rules (Azure uses explicit out/in rules rather than one target).'),
    (['Group → [[Edit]] → [[Autoscaling]] → mode [[On]], signal CPU utilization 50%, min 2, max 4 → [[Save]].'],
     'gcloud compute instance-groups managed set-autoscaling web-mig --region=asia-south1 \\\n  --min-num-replicas=2 --max-num-replicas=4 --target-cpu-utilization=0.5 --cool-down-period=90\ngcloud compute instance-groups managed describe web-mig --region=asia-south1 --format="yaml(autoscaler)"',
     'an autoscaler with <code>cpuUtilization: utilizationTarget: 0.5</code>.')),
    'Load balancing + auto scaling = the elastic web tier from Lessons 5.3 and 7.2, now as one pattern.')

STEP3 = ('3 · Watch it balance — and route around a stopped server', tri(
    (['Open the ALB DNS name in a browser and refresh several times: the hostname changes.', '[[Instances]] → stop one instance → [[Target groups]] → [[Targets]]: it becomes unhealthy/unused; the page keeps working from the other. Auto Scaling then replaces it.'],
     "for i in $(seq 1 6); do curl -s http://$DNS; done | sort | uniq -c\nV=$(aws autoscaling describe-auto-scaling-groups --auto-scaling-group-names tiffingo-web-asg --query 'AutoScalingGroups[0].Instances[0].InstanceId' --output text)\naws ec2 stop-instances --instance-ids $V\nsleep 60; for i in $(seq 1 6); do curl -s http://$DNS; done | sort | uniq -c\naws elbv2 describe-target-health --target-group-arn $TG --query 'TargetHealthDescriptions[].[Target.Id,TargetHealth.State]' --output table",
     'first two hostnames sharing the requests, then only one; target health shows the stopped one as <code>unused</code>/<code>unhealthy</code>, and the group launches a replacement.'),
    (['Open http://PUBLIC-IP and refresh — two instance names alternate (new connections).', 'Scale set → [[Instances]] → select one → [[Stop]]. The probe fails and the LB sends traffic only to the running instance.'],
     'for i in $(seq 1 6); do curl -s http://$IP; done | sort | uniq -c\nID=$(az vmss list-instances --resource-group rg-tiffingo --name tiffingo-vmss --query "[0].instanceId" --output tsv)\naz vmss stop --resource-group rg-tiffingo --name tiffingo-vmss --instance-ids $ID\nsleep 30; for i in $(seq 1 6); do curl -s http://$IP; done | sort | uniq -c',
     'two hostnames, then one. (Azure Load Balancer hashes by connection 5-tuple, so curl’s new connections spread; a browser keeping one connection may stick.)'),
    (['Open http://LB-IP and refresh — hostnames vary.', '[[VM instances]] → stop one group instance; [[Load balancing]] → web-lb → backend shows 1 of 2 healthy; the MIG restarts it to keep 2 running.', 'Optional: backend web-bs → [[Edit]] → tick [[Enable Cloud CDN]] — caching at the edge with one switch.'],
     "for i in $(seq 1 6); do curl -s http://$IP; done | sort | uniq -c\nV=$(gcloud compute instance-groups managed list-instances web-mig --region=asia-south1 --format='value(instance.basename())' --limit=1)\nZ=$(gcloud compute instance-groups managed list-instances web-mig --region=asia-south1 --format='value(instance.segment(-3))' --limit=1)\ngcloud compute instances stop $V --zone=$Z\nsleep 60; gcloud compute backend-services get-health web-bs --global --format='table(status.healthStatus[].instance.basename(),status.healthStatus[].healthState)'\ngcloud compute backend-services update web-bs --enable-cdn --global     # optional: edge caching",
     'two hostnames, then health showing one UNHEALTHY while traffic continues from the other; the MIG brings the stopped VM back.')),
    'Health checks connect the patterns: the load balancer stops sending traffic, the scaling group restores capacity.')

prac = practical(OWN_INTRO + ' A load balancer and 2–4 tiny VMs for about 30 minutes cost a few rupees — run the clean-up straight after.', [SETUP_STEP, STEP1, STEP2, STEP3],
    cleanup='<b>AWS:</b> <code>aws autoscaling delete-auto-scaling-group --auto-scaling-group-name tiffingo-web-asg --force-delete; aws elbv2 delete-load-balancer --load-balancer-arn $LB; sleep 60; aws elbv2 delete-target-group --target-group-arn $TG; aws ec2 delete-launch-template --launch-template-name tiffingo-web-lt; aws ec2 delete-security-group --group-id $SG</code> (retry the SG after instances terminate).<br>'
            '<b>Azure:</b> <code>az group delete --name rg-tiffingo --yes --no-wait</code>.<br>'
            '<b>Google Cloud:</b> <code>gcloud compute forwarding-rules delete web-fr --global --quiet; gcloud compute target-http-proxies delete web-proxy --quiet; gcloud compute url-maps delete web-map --quiet; gcloud compute backend-services delete web-bs --global --quiet; gcloud compute health-checks delete web-hc --quiet; gcloud compute instance-groups managed delete web-mig --region=asia-south1 --quiet; gcloud compute instance-templates delete web-tpl --quiet; gcloud compute firewall-rules delete allow-http-web --quiet</code>.')

mist = mistakes([
    ['Retrying everything, instantly, at every layer.', 'Retries feel safe.', 'Retry once per call chain with backoff + jitter; idempotency keys.'],
    ['No timeouts on remote calls.', 'Library defaults are minutes.', 'Short explicit timeouts; circuit breakers around dependencies.'],
    ['Caching without invalidation.', 'TTL only.', 'Delete keys on update; short TTLs for volatile data.'],
    ['Sticky sessions instead of a session store.', 'Quick fix for logins.', 'Stateless app tier + Redis/DynamoDB sessions.'],
    ['Scaling on CPU for I/O-bound apps.', 'Default metric.', 'Scale on requests per target, latency or queue backlog.'],
    ['Queues without DLQs and age alarms.', 'Happy-path testing.', 'DLQ + alarm on oldest-message age.']])

cert = table(['Exam / syllabus', 'What is asked'], [['C-DAC PGCP-BDA', 'Cloud design patterns: load balancing, auto scaling, caching.'], ['AWS CLF-C02', 'ELB, Auto Scaling, ElastiCache, CloudFront, SQS for decoupling; elasticity and loose coupling design principles.'], ['AZ-900', 'Load Balancer, Application Gateway, Front Door, VMSS autoscale, Azure Cache for Redis/Managed Redis.'], ['Google Cloud Digital Leader', 'Cloud Load Balancing, autoscaling, Memorystore, Cloud CDN, Pub/Sub.']], minw=560) + \
    qx('1. Which AWS service distributes incoming traffic across multiple targets?', ['Amazon EC2 Auto Scaling', 'Elastic Load Balancing', 'Amazon ElastiCache', 'Amazon SQS'], 1, 'ELB.') + \
    qx('2. Which service reduces database read load by keeping frequently used data in memory?', ['Amazon ElastiCache', 'Amazon S3 Glacier', 'AWS Backup', 'Amazon Route 53'], 0, 'Cache.') + \
    qx('3. Adding random variation to retry delays is called…', ['throttling', 'jitter', 'sharding', 'draining'], 1, 'Jitter.') + \
    qx('4. A pattern that stops calls to a failing service for a period is…', ['cache-aside', 'circuit breaker', 'CDN', 'auto scaling'], 1, 'Circuit breaker.') + \
    qx('5. Which pattern smooths bursts of writes using a buffer?', ['Queue-based load leveling', 'Round robin', 'Sticky sessions', 'Blue-green'], 0, 'Queue.') + \
    qx('6. Which Google Cloud feature adds edge caching to a backend service?', ['Cloud CDN', 'Cloud NAT', 'Cloud Router', 'Cloud Armor only'], 0, 'Cloud CDN.')

proj = miniproject('Mini project: make TiffinGo survive Diwali',
    'Apply all seven patterns to TiffinGo and prove two of them.',
    ['<b>Map dependencies:</b> list every call (DB, cache, payments, SMS, maps API).',
     '<b>Assign patterns:</b> LB + ASG for the API, cache-aside for menus, CDN for assets, queue for SMS/invoices, retry + breaker for payments.',
     '<b>Numbers:</b> TTLs, timeouts, retry counts, breaker thresholds, scaling targets — write them down.',
     '<b>Prove it:</b> build the load-balanced, auto-scaled tier and stop an instance (steps 1–3).',
     '<b>Load test (optional):</b> use a tool like <code>hey</code> or <code>ab</code> against the LB and watch scaling.',
     '<b>Clean up</b>.'],
    'A pattern map with concrete settings and a working elastic web tier (then deleted).', 'This lesson + 5.3, 7.2, 7.4.')

assemble_v2(HERE, story_h2='Diwali, 8 p.m.', hook_html=hk,
    narration='Last Diwali TiffinGo added servers by hand too late, hammered the database with the same menu query and froze when payments slowed. Seven well-known patterns would have handled all three.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Cloud design patterns',
    formal='<b>Cloud design patterns</b> are proven, reusable solutions to recurring problems in building scalable and resilient cloud systems — including <b>load balancing</b> (distribute requests across healthy instances), <b>auto scaling</b> (adjust capacity to demand), <b>caching</b> (cache-aside and edge caching to serve repeated reads from fast storage), <b>queue-based load leveling</b>, <b>retry with exponential backoff and jitter</b>, and the <b>circuit breaker</b>.',
    simple='Ready-made design ideas: share work across servers, add servers automatically, keep popular data close and in memory, buffer bursts, retry politely, and stop calling things that are broken.',
    interview=['“For scale I combine a load balancer, an auto scaling group with target tracking, a cache-aside layer like ElastiCache for hot reads and a CDN for static content.”', '“For resilience I put queues in front of slow work, use timeouts with exponential backoff and jitter for transient faults, and circuit breakers with fallbacks for failing dependencies.”'],
    terms_rows=[('Pattern', 'Reusable solution.'), ('Load balancing', 'Spread requests.'), ('Auto scaling', 'Capacity follows load.'), ('Cache-aside', 'Check cache, then DB.'), ('TTL', 'Cache lifetime.'), ('CDN', 'Edge caching.'), ('Load leveling', 'Queue buffers bursts.'), ('Backoff + jitter', 'Growing, random retry waits.'), ('Circuit breaker', 'Fail fast on failing dependency.'), ('Idempotency', 'Safe to repeat.')],
    exam='Expect “which service/pattern” questions: ELB vs Auto Scaling vs ElastiCache vs CloudFront vs SQS, and the design principles of elasticity and loose coupling.',
    picture_h2='Where the patterns sit, and what each solves', picture_html=picture,
    after_picture=[('types', 'Types, one by one', 'Seven design patterns, one by one', TYPES)],
    how_h2='Diwali spike: seven patterns working together', how_intro='One surge, every pattern doing its part.', how_anim=SPIKE,
    parts_h2='Six supporting ideas', parts_html=parts, lv='',
    myth_rows=[('More retries = more reliable.', 'Retries multiply load; use backoff, jitter and limits.', 'Type 6.'), ('Caching is free performance.', 'It brings staleness and stampedes to manage.', 'Type 3.'), ('Auto scaling handles every spike.', 'Instances take minutes; pre-scale and cache.', 'Type 2.')],
    extra_secs=[('deep', 'Deep dive', 'More patterns (bulkhead, throttling, CQRS, sidecar) and how they combine', DEEP)],
    clouds_html=clouds, practical_html=prac, mistakes_html=mist, cert_html=cert, project_html=proj,
    can_now=['Explain load balancing algorithms and auto scaling policies.', 'Apply cache-aside and CDN edge caching correctly.', 'Use queues to level bursts and DLQs for failures.', 'Configure retries with backoff and jitter and explain circuit breakers.', 'Build a load-balanced, auto-scaled web tier and test failover on your own account.'],
    next_html='Module 8 — <a href="../../08-operating-the-cloud/01-administering-and-monitoring-cloud-services/">8.1 Administering and monitoring cloud services</a>.',
    pre='<b>Before you start:</b> <a href="../02-scalability-availability-and-fault-tolerance/">7.2</a> and <a href="../04-monolith-vs-microservices-vs-serverless/">7.4</a>.')
