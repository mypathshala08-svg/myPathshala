import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
def cap(frames, steps, title, intro, panel, aria, hid, delay=5500):
    return anim_one('Animated', title, intro, panel, aria, cap_frames(frames, steps), [s[0] + '.' for s in steps], delay=delay, hid=hid)


hk = hook('TiffinGo’s new menu page is ready. Last time, Kabir copied files to the server at 7 pm, the site broke for every customer, and rolling back took 40 minutes. How do cloud teams release ten times a day without that fear?',
    'By separating <b>deploy</b> (putting a new version in place) from <b>release</b> (sending users to it), and choosing a <b>deployment strategy</b>: all-at-once, rolling, blue/green, canary, immutable, or feature flags. This lesson shows what happens inside a cloud deployment step by step, explains the six strategies one by one, and on <b>your own</b> account you deploy a real web app, release v2 to 10% of users, then roll back in one command — on AWS Lambda, Azure App Service or Google Cloud Run.',
    ['Why “deploy” and “release” are two different moments.', 'How a canary catches a bad version before most users see it.', 'Why rollback should be a traffic switch, not a rebuild.'])

def story_scene():
    o = t(180, 12, 'Two ways to ship the new menu', 9, 'ink', bold=True)
    o += box(8, 28, 160, 74, 'red', rx=8) + t(88, 48, 'Copy files at 7 pm', 8.4, 'ink', bold=True) + t(88, 64, 'all users get v2 at once', 7, 'ink2') + t(88, 78, 'bug → everyone hit', 7, 'ink2') + t(88, 92, 'rollback: 40 min', 7.4, 'ink', bold=True)
    o += box(192, 28, 160, 74, 'green', rx=8) + t(272, 48, 'Canary + switch', 8.4, 'ink', bold=True) + t(272, 64, 'v2 to 10% first', 7, 'ink2') + t(272, 78, 'errors? switch back', 7, 'ink2') + t(272, 92, 'rollback: 10 seconds', 7.4, 'ink', bold=True)
    o += t(180, 122, 'Same code, different risk', 7.6, 'ink', bold=True)
    return o
scene_svg = scene('Left: copying files at 7 pm gives every user v2 at once and a 40-minute rollback. Right: canary sends v2 to 10% first and rollback is a 10-second switch.', story_scene(), 'Make releasing <tspan font-weight="700" class="s-acc">boring</tspan>.', h=132)
dialogue = '''K> Sir, I tested on my laptop. It worked. Production still broke.
A> Your laptop is not production — different config, different data. So assume every release can fail, and make failing cheap.
R> How?
A> Keep the old version running. Put the new one beside it. Send 10% of users first, watch errors, then move everyone. If anything looks bad, switch back.
K> So rollback is just moving traffic?
A> Exactly. Let’s see how each cloud does it.'''

# ------------------------------------------------------------------ picture
def pipefig():
    o = t(320, 16, 'From code to customers: build once, deploy, release', 11, 'ink', bold=True)
    S = [('Code', 'Git commit', 'card'), ('Build', 'test, package', 'blue'), ('Artifact', 'zip / image, versioned', 'violet'), ('Deploy', 'new version in place', 'amber'), ('Release', 'shift traffic', 'green'), ('Observe', 'errors, latency', 'red')]
    for i, (a, b, tn) in enumerate(S):
        x = 10 + i * 104
        o += box(x, 40, 96, 64, tn, rx=8) + t(x + 48, 66, a, 8.6, 'ink', bold=True) + t(x + 48, 84, b, 6.6, 'ink2')
        if i < 5: o += arrow(x + 96, 72, x + 104, 72)
    o += '<path d="M570 106 C 570 150, 400 150, 400 108" style="fill:none;stroke:var(--track);stroke-width:1.6;stroke-dasharray:4 3"/>' + t(486, 156, 'bad? shift traffic back (rollback)', 7.2, 'ink', bold=True)
    o += t(320, 186, 'The same artifact moves through test → staging → production; only configuration changes.', 7.4, 'ink2')
    return o
PIPE = bigfig('Pipeline: code, build, artifact, deploy, release, observe; a dashed arrow from observe back to release shows rollback by shifting traffic.', pipefig(), h=196)

def targfig():
    o = t(320, 16, 'Where can the app run? (deployment targets)', 11, 'ink', bold=True)
    T = [('VMs', 'EC2 · Azure VMs · Compute Engine', 'you manage OS', 'amber'), ('App platform (PaaS)', 'Elastic Beanstalk · App Service · App Engine', 'push code', 'blue'), ('Containers', 'ECS/EKS · Container Apps/AKS · Cloud Run/GKE', 'push image', 'violet'), ('Functions', 'Lambda · Azure Functions · Cloud Run functions', 'push function', 'green'), ('Static site', 'S3 + CloudFront · Static Web Apps · Firebase Hosting', 'push files', 'card')]
    for i, (a, b, c, tn) in enumerate(T):
        y = 30 + i * 32
        o += box(14, y, 150, 26, tn, rx=5) + t(89, y + 17, a, 7.8, 'ink', bold=True) + t(372, y + 17, b, 7, 'ink') + t(586, y + 17, c, 7, 'ink2')
    o += t(320, 202, 'Lesson 2.5 helps choose; the strategies below work on all of them.', 7.4, 'ink2')
    return o
TARG = bigfig('Five deployment targets: VMs, app platform, containers, functions, static sites, with AWS, Azure and Google examples.', targfig(), h=210)

picture = ('  <p>Every cloud deployment follows the same path. The key idea: <b>build once</b>, keep a versioned artifact, and make rollback a traffic switch.</p>\n' + PIPE +
           '\n  <p>The same strategies apply wherever the app runs:</p>\n' + TARG +
           '\n  <h3>Deploy vs release</h3>\n' + table(['', 'Deploy', 'Release'], [['What', 'put a new version in place', 'send users to it'], ['Risk to users', 'none (no traffic yet)', 'yes'], ['Example', 'new Cloud Run revision with --no-traffic', 'update-traffic to 10%, then 100%'], ['Undo', 'delete the version', 'shift traffic back']], minw=520))

# ------------------------------------------------------------------ how: inside a deployment
RN = {'dev': (4, 54, 50, 50, 'user', 'Developer', 'v2 ready'), 'art': (66, 4, 62, 46, 'disk', 'Artifact', 'image / zip v2'), 'svc': (66, 104, 62, 46, 'gear', 'Service', 'new revision'),
      'hc': (142, 54, 60, 50, 'meter', 'Health check', '/health = 200?'), 'lb': (216, 4, 62, 46, 'lb', 'Router', '90 / 10 split'), 'mon': (216, 104, 62, 46, 'chart', 'Metrics', 'errors v2?'), 'users': (292, 54, 64, 50, 'phone', 'Users', 'all on v2')}
RS = [dict(on=['dev', 'art'], hot='art', move=(54, 79, 72, 30, 'push'), head='Step 1 · Build and store the artifact', text='CI builds the code once into a versioned artifact (container image or zip) and', text2='stores it in a registry or bucket. Same artifact goes to every environment.', svc='ECR · Azure Container Registry · Artifact Registry (or S3/Blob/GCS for zips)'),
      dict(on=['art', 'svc'], hot='svc', move=(97, 50, 97, 104, 'deploy'), head='Step 2 · Deploy a new version beside the old', text='The platform creates revision v2 next to v1. Configuration and secrets come from', text2='the environment, not the artifact. No user traffic yet.', svc='Lambda version · App Service slot · Cloud Run revision'),
      dict(on=['svc', 'hc'], hot='hc', move=(128, 127, 150, 90, 'probe'), head='Step 3 · Health checks prove it starts', text='The platform calls the health endpoint; if v2 cannot start or answer, the deployment', text2='stops here — users never see it.', svc='Readiness/startup probes, load-balancer health checks'),
      dict(on=['hc', 'lb'], hot='lb', move=(202, 66, 226, 30, '10%'), head='Step 4 · Release to a small slice', text='The router sends 10% of requests to v2 (canary). 90% stay on the known-good v1.', text2='', svc='Weighted alias · slot traffic routing · revision traffic split'),
      dict(on=['lb', 'mon'], hot='mon', move=(247, 50, 247, 104, 'watch'), head='Step 5 · Watch the golden signals', text='Compare v2 errors and latency with v1 for a few minutes (Lesson 8.1). Bad? Set v2 to', text2='0% — rollback in seconds. Good? Continue.', svc='Automated canary analysis can decide for you'),
      dict(on=list(RN), hot='users', move=(278, 127, 298, 90, '100%'), head='Step 6 · Promote, keep the old version', text='Shift to 100%. Keep v1 deployed for a while so rollback stays one command away.', text2='Record the release (version, time, who) for the audit trail.', svc='Deploy markers on dashboards make the next incident easier')]
DEPLOY = flow_anim('Inside a safe cloud deployment', 'From a built artifact to every user on v2 — with a rollback path at every step.', 'Safe deployment', 'Animation: build and store artifact; deploy new version beside the old; health checks; release to 10%; watch metrics; promote to 100% keeping the old version.', RN, RS, hid='depflow')

# ------------------------------------------------------------------ types
def mapfig():
    o = t(320, 16, 'Six deployment strategies', 11, 'ink', bold=True)
    items = [('1', 'All-at-once (recreate)', 'replace everything together', 'red'), ('2', 'Rolling', 'replace a batch at a time', 'amber'), ('3', 'Blue/green', 'full new copy, then switch', 'blue'),
             ('4', 'Canary', 'small % first, then more', 'green'), ('5', 'Immutable', 'new servers, never patch old', 'violet'), ('6', 'Feature flags', 'code deployed, feature off', 'card')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 12 + (i % 3) * 208; y = 32 + (i // 3) * 84
        o += box(x, y, 198, 70, tn, rx=8) + pin(x + 16, y + 16, n) + t(x + 106, y + 34, a, 8.2, 'ink', bold=True) + t(x + 106, y + 54, b, 7, 'ink2')
    o += t(320, 210, 'Risk falls and cost/complexity rises from 1 to 4; 5 and 6 combine with any of them.', 7.4, 'ink2')
    return o
MAP = bigfig('Map of six deployment strategies: all-at-once, rolling, blue/green, canary, immutable, feature flags.', mapfig(), h=222)

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

A1 = mk(['All on v1', 'Stop and replace', 'All on v2'], ['v1|every server|serving', 'replace|stop all|install v2', 'v2|every server|hope it works'], ['green', 'red', 'amber'],
        ['every instance runs the old version', 'all are stopped and updated together (brief downtime)', 'every user is on v2 at once — good or bad'],
        [('Before', 'Every instance runs v1.', ''), ('Replace', 'All instances are updated together; usually brief downtime.', ''), ('After', 'All users get v2 at once.', '')],
        'All-at-once in action', 'Simple, fast, risky.', 'All-at-once', 'Animation: all on v1; stop and replace; all on v2.', 'd1anim')
T1 = vt(1, 'All-at-once (recreate / in-place)', 'red',
    'An <b>all-at-once</b> (recreate or in-place) deployment replaces the application on every instance at the same time, usually with a short outage, so that all users move from the old version to the new one together; rollback requires deploying the old version again.',
    'Changing all the bulbs in a hall at once with the main switch off: quick, but the room is dark for a moment, and if the new bulbs are faulty, nobody can see.',
    'Kabir’s 7 pm file copy was all-at-once: every customer got the broken menu page together.',
    'Elastic Beanstalk “All at once”, CodeDeploy in-place AllAtOnce, Kubernetes “Recreate” strategy, App Service direct deploy to production.', '', A1,
    'dev/test environments, or tiny apps where a short outage is acceptable.',
    'customers use the system continuously — any bug hits 100% of them.',
    'Updating all servers to the new version at the same time.',
    [('Stop', 'Take instances out (or accept errors).'), ('Install', 'Deploy v2 everywhere.'), ('Start', 'Bring all back.'), ('Verify', 'Smoke test.'), ('Rollback', 'Redeploy v1 — slow.')],
    [('in-place', 'updating the existing servers rather than replacing them'), ('downtime', 'time when the service is not available'), ('smoke test', 'quick check that the basics work')],
    table(['', 'All-at-once', 'Rolling'], [['Downtime', 'usually yes', 'no'], ['Speed', 'fastest', 'slower'], ['Blast radius', '100%', 'one batch']], minw=420),
    ['Dev and test', 'Internal tools', 'Single-instance apps'],
    'Many early outages in companies’ histories came from all-at-once releases on Friday evenings — the origin of the “don’t deploy on Friday” joke.',
    'If you must use it, at least keep the previous artifact ready and practise the redeploy — rollback speed is what matters.')

A2 = mk(['Batch 1 updated', 'Batch 2 updated', 'All updated'], ['batch 1|v2|others v1', 'batch 2|v2|health OK?', 'fleet|all v2|no downtime'], ['amber', 'amber', 'green'],
        ['a few instances leave the load balancer and get v2', 'when they are healthy, the next batch follows', 'capacity stays up; both versions run for a while'],
        [('Batch 1', 'A few instances are drained, updated, checked.', ''), ('Batch 2', 'Healthy? Continue with the next batch.', ''), ('Done', 'All instances on v2 with no downtime.', '')],
        'Rolling in action', 'A batch at a time.', 'Rolling', 'Animation: first batch updated; second batch; all updated.', 'd2anim')
T2 = vt(2, 'Rolling deployment', 'amber',
    'A <b>rolling deployment</b> updates instances in batches: each batch is removed from the load balancer, updated to the new version, health-checked and returned before the next batch starts, so the service stays available, with old and new versions running side by side during the rollout.',
    'Repainting a hotel floor room by room: guests keep staying in the other rooms while a few are being painted.',
    'TiffinGo’s order API on 6 VMs updates 2 at a time; if a batch fails its health check, the rollout stops with 4 VMs still on v1.',
    'Kubernetes Deployments (default RollingUpdate), EC2 Auto Scaling instance refresh, Elastic Beanstalk Rolling, Azure VM Scale Sets rolling upgrades, Managed Instance Group rolling updates.', '', A2,
    'you want no downtime without paying for a full second environment.',
    'v1 and v2 cannot run together (incompatible database changes) or you need instant rollback.',
    'Updating a few servers at a time while the others keep serving users.',
    [('Batch size', 'e.g. 25% or 2 instances.'), ('Drain', 'Remove from load balancer.'), ('Update', 'New version.'), ('Check', 'Health check passes.'), ('Repeat', 'Next batch; stop on failure.')],
    [('batch', 'a group of instances updated together'), ('drain', 'let current requests finish before removing a server'), ('max surge', 'extra instances allowed during a rollout (Kubernetes)')],
    table(['', 'Rolling', 'Blue/green'], [['Extra capacity', 'little or none', 'full second copy'], ['Rollback', 'roll back batch by batch', 'instant switch'], ['Versions live together', 'yes', 'only during switch']], minw=440),
    ['Kubernetes services', 'Auto Scaling fleets', 'Stateless APIs'],
    'Kubernetes uses rolling updates by default, with maxSurge and maxUnavailable controlling how many pods change at once.',
    'Database changes must be backward-compatible (expand → migrate → contract) because v1 and v2 read the same database during the roll.')

A3 = mk(['Blue serves users', 'Green built and tested', 'Switch traffic'], ['blue|v1|100% traffic', 'green|v2|0% traffic, tested', 'switch|router → green|blue kept for rollback'], ['blue', 'green', 'green'],
        ['the current environment (blue) serves everyone', 'an identical environment (green) runs v2 and is tested privately', 'the router switches; blue stays ready for instant rollback'],
        [('Blue', 'The live environment serves 100% of users.', ''), ('Green', 'A full copy with v2 is deployed and tested privately.', ''), ('Switch', 'Traffic moves to green; blue is kept for instant rollback.', '')],
        'Blue/green in action', 'Two copies, one switch.', 'Blue/green', 'Animation: blue serves; green built and tested; traffic switched.', 'd3anim')
T3 = vt(3, 'Blue/green deployment', 'blue',
    'A <b>blue/green deployment</b> runs two identical production environments: “blue” serves live traffic while “green” receives the new version and is tested; traffic is then switched to green in one step (load balancer, DNS or slot swap), and blue is kept for instant rollback.',
    'A second stage behind the curtain: the next act is fully set up and rehearsed, then the curtain opens on it in a second — and the old set is still there if needed.',
    'Azure App Service deployment slots: TiffinGo deploys v2 to the “staging” slot, tests it at its own URL, then swaps — the slots exchange in seconds (practical step 3).',
    'App Service deployment slots, Elastic Beanstalk environment swap (CNAME swap), CodeDeploy blue/green for ECS/EC2, two Cloud Run revisions with traffic switch, load-balancer target group switch.', '', A3,
    'instant, full rollback matters and you can afford a second environment briefly.',
    'the database cannot serve both versions or the environment is huge and expensive to duplicate.',
    'Keeping two copies of the system; you test the new copy and then switch all users to it at once.',
    [('Clone', 'Create green identical to blue.'), ('Deploy', 'v2 to green.'), ('Test', 'Private URL / slot.'), ('Switch', 'Router/slot swap.'), ('Keep blue', 'Rollback = switch back.')],
    [('slot', 'a separate live copy of an App Service app with its own URL'), ('swap', 'exchange which copy receives production traffic'), ('CNAME swap', 'switching a DNS name between environments')],
    table(['', 'Blue/green', 'Canary'], [['Traffic shift', 'all at once', 'gradual %'], ['Real-user test before full', 'no (private tests only)', 'yes'], ['Rollback', 'instant', 'instant']], minw=420),
    ['Web apps with strict uptime', 'Releases needing warm-up', 'Regulated change windows'],
    'Martin Fowler described blue/green deployment in 2010; deployment slots and environment swaps made it a checkbox feature in PaaS platforms.',
    'Warm up green before the switch (slots can run warm-up requests) — a cold green environment causes a latency spike right after swap.')

A4 = mk(['10% to v2', 'Compare metrics', 'Promote or abort'], ['canary|v2 gets 10%|v1 gets 90%', 'compare|errors, latency|v2 vs v1', 'decide|100% v2|or 0% (rollback)'], ['green', 'amber', 'blue'],
        ['a small share of real users go to the new version', 'its error rate and latency are compared with the old version', 'healthy → increase step by step; unhealthy → back to 0%'],
        [('Slice', 'A small share of real traffic goes to v2.', ''), ('Compare', 'v2 errors and latency are compared with v1.', ''), ('Decide', 'Increase gradually, or roll back to 0%.', '')],
        'Canary in action', 'Test with a few real users.', 'Canary', 'Animation: 10% to v2; compare metrics; promote or abort.', 'd4anim')
T4 = vt(4, 'Canary release', 'green',
    'A <b>canary release</b> gradually shifts a small percentage of real production traffic to the new version (for example 10% → 50% → 100%), compares its health metrics with the old version at each step, and either promotes it or rolls back, limiting the impact of a bad release to a small share of users.',
    'Coal miners carried a canary: if the bird struggled, they left before the gas reached everyone. Here, 10% of requests are the canary.',
    'TiffinGo sends 10% of menu-page traffic to v2 for 15 minutes; v2’s error rate stays at v1’s level, so it moves to 100% (animation above and practical step 3).',
    'Lambda alias weighted routing + CodeDeploy canary, App Service traffic routing, Cloud Run revision traffic split, Container Apps revision weights, Argo Rollouts / Flagger on Kubernetes.', '', A4,
    'you want real-user proof with limited blast radius.',
    'traffic is too low for meaningful comparison (10% of 20 requests tells you nothing) — use longer windows or synthetic tests.',
    'Sending only a few users to the new version first, and everyone else after it proves itself.',
    [('Deploy', 'v2 with 0% traffic.'), ('Shift', '5–10%.'), ('Analyse', 'Errors, latency, business KPIs.'), ('Step up', '25%, 50%, 100%.'), ('Auto-rollback', 'Alarm breach → 0%.')],
    [('blast radius', 'how many users a failure can affect'), ('weighted routing', 'splitting traffic by percentages'), ('canary analysis', 'automatic comparison of canary vs baseline')],
    table(['', 'Canary', 'A/B test'], [['Purpose', 'release safety', 'measure a business hypothesis'], ['Split by', 'random %', 'user groups'], ['Ends when', 'v2 at 100% or rolled back', 'enough statistical evidence']], minw=440),
    ['Large consumer apps', 'Serverless APIs', 'Kubernetes microservices'],
    'Large tech companies roll out changes gradually across users and Regions so that a bad change is caught while only a small fraction of users are affected.',
    'Pair canaries with automated rollback on alarms (CodeDeploy can do this for Lambda/ECS) — humans watching graphs at 2 am miss things.')

A5 = mk(['New image built', 'New instances launched', 'Old ones removed'], ['image|AMI / container|v2, versioned', 'launch|fresh instances|from image', 'retire|old instances|terminated'], ['violet', 'blue', 'green'],
        ['every release is a new, complete image', 'fresh instances are started from it — nothing is patched in place', 'old instances are terminated; no configuration drift'],
        [('Image', 'Each release builds a complete new machine or container image.', ''), ('Launch', 'Fresh instances start from it; nothing is changed in place.', ''), ('Retire', 'Old instances are terminated — no drift.', '')],
        'Immutable deployment in action', 'Replace, never repair.', 'Immutable', 'Animation: new image built; new instances launched; old ones removed.', 'd5anim')
T5 = vt(5, 'Immutable deployment', 'violet',
    'An <b>immutable deployment</b> never modifies running servers: each release is built into a new machine or container image, new instances are launched from it, and old instances are terminated after traffic moves — eliminating configuration drift and making every environment reproducible.',
    'Instead of repairing an old phone again and again, you get a new identical phone with everything installed from a backup image.',
    'TiffinGo bakes a new AMI for its reporting VM every release; an Auto Scaling instance refresh replaces old VMs. No one SSHes in to “fix” production any more.',
    'Containers (every image is immutable), EC2 Image Builder + Auto Scaling instance refresh, Packer images, Elastic Beanstalk “Immutable” policy, Azure VMSS with new image versions, MIG rolling replace.', '', A5,
    'you want reproducible environments and to stop manual changes on servers.',
    'you have stateful servers with local data — move data out first.',
    'Building completely new servers for each version and throwing away the old ones, instead of changing them.',
    [('Build', 'Image per release.'), ('Scan', 'Security scan the image.'), ('Launch', 'New instances.'), ('Shift', 'Traffic via LB.'), ('Terminate', 'Old instances.')],
    [('configuration drift', 'servers slowly becoming different through manual changes'), ('golden image', 'a pre-built, approved machine image'), ('instance refresh', 'Auto Scaling replacing instances with a new template')],
    table(['', 'Immutable', 'Mutable (in-place)'], [['Servers changed after launch?', 'never', 'yes, patched/updated'], ['Drift', 'none', 'common'], ['Rollback', 'launch previous image', 'undo changes (hard)']], minw=440),
    ['Container platforms', 'Auto Scaling fleets', 'Regulated environments'],
    'Containers made immutability the default: a tagged image is never changed, so “it worked in staging” really means the same bits.',
    'Pin images by digest (sha256), not just tag — a tag like :latest can point to different bits tomorrow.')

A6 = mk(['Code deployed, flag off', 'Turn on for staff', 'Turn on for all'], ['deploy|new code in prod|feature hidden', 'flag on|employees, 5%|test live', 'release|everyone|or switch off'], ['card', 'amber', 'green'],
        ['new code ships to production but the feature is switched off', 'a flag turns it on for staff or a small group', 'switch on for all — or off instantly without a redeploy'],
        [('Dark launch', 'New code is in production, feature switched off.', ''), ('Target', 'Turn it on for staff or a small %.', ''), ('Release', 'On for all — or off instantly, no redeploy.', '')],
        'Feature flags in action', 'Release without deploying.', 'Feature flags', 'Animation: code deployed with flag off; on for staff; on for all.', 'd6anim')
T6 = vt(6, 'Feature flags (dark launches)', 'card',
    '<b>Feature flags</b> (toggles) are runtime switches in code that turn a feature on or off for all users or chosen segments without redeploying; they separate deployment from release, enable dark launches and instant kill switches, and are often combined with canary or A/B testing.',
    'A new dish cooked and ready in the kitchen but not on the printed menu — waiters offer it only to regular customers until the chef is sure.',
    'TiffinGo deployed the new “weekly subscription” code a week early with the flag off; it was turned on for staff, then Pune customers, then everyone.',
    'AWS AppConfig feature flags, Azure App Configuration feature manager, Firebase Remote Config; LaunchDarkly, Unleash, OpenFeature standard.', '', A6,
    'you want to release features independently of deployments or need a kill switch.',
    'flags are never removed — old flags become technical debt and hidden complexity.',
    'On/off switches in the app so a new feature can be turned on for some people — or off — without installing a new version.',
    [('Wrap', 'if flag(“subscription”) …'), ('Deploy', 'Flag default off.'), ('Target', 'Staff, city, % of users.'), ('Monitor', 'Errors and KPIs.'), ('Clean up', 'Remove the flag after full release.')],
    [('toggle', 'another word for a feature flag'), ('kill switch', 'flag to turn a feature off instantly'), ('dark launch', 'feature in production but hidden')],
    table(['', 'Feature flag', 'Canary'], [['Splits by', 'feature, user segment', 'version, % traffic'], ['Needs redeploy to undo?', 'no', 'no (traffic shift)'], ['Lives in', 'application code/config', 'platform router']], minw=440),
    ['Consumer apps', 'Mobile apps (can’t roll back installs)', 'Trunk-based development'],
    'Mobile apps rely heavily on flags because a shipped app version cannot be rolled back on users’ phones — the server-side switch is the only fast undo.',
    'Give every flag an owner and an expiry date; teams with hundreds of stale flags lose track of what is really running.')

SUMMARY = table(['#', 'Strategy', 'Downtime', 'Extra cost', 'Rollback', 'Best for'], [
    ['1', 'All-at-once', 'usually', 'none', 'redeploy (slow)', 'dev/test'], ['2', 'Rolling', 'no', 'little', 'roll back batches', 'stateless fleets'], ['3', 'Blue/green', 'no', 'second environment', 'instant switch', 'strict uptime'],
    ['4', 'Canary', 'no', 'small', 'instant (0%)', 'high-traffic services'], ['5', 'Immutable', 'no', 'temporary extra instances', 'previous image', 'reproducibility'], ['6', 'Feature flags', 'no', 'flag service', 'switch off', 'decoupling release']], minw=620)
CHECK = ('  <h3>Check yourself: which strategy?</h3>\n' +
    qx('A. Swap an App Service staging slot into production.', ['Blue/green', 'Canary', 'All-at-once', 'Rolling'], 0, 'Slot swap.') +
    qx('B. 10% of traffic to the new Lambda version for 15 minutes.', ['Canary', 'Immutable', 'Recreate', 'Flag'], 0, 'Weighted alias.') +
    qx('C. Kubernetes replaces pods two at a time.', ['Rolling', 'Blue/green', 'Flag', 'Recreate'], 0, 'RollingUpdate.') +
    qx('D. Turn off a broken feature without deploying.', ['Feature flag', 'Rolling', 'Immutable', 'Blue/green'], 0, 'Kill switch.'))

TYPES = ('  <p>Six strategies, each in the same pattern: definition, plain words, analogy, internal steps, animation, differences, where used, real-world example, TiffinGo scenario and an expert note.</p>\n'
         + challenge(['Why must database changes be backward-compatible in a rolling deployment?', 'Why can’t mobile apps simply roll back?', 'When is a canary useless?'], 'types 2, 6 and 4') + MAP
         + jump(['All-at-once', 'Rolling', 'Blue/green', 'Canary', 'Immutable', 'Flags']) + T1 + T2 + T3 + T4 + T5 + T6
         + '\n  <h3 style="margin-top:34px">All six side by side</h3>\n' + SUMMARY + '\n' + CHECK)

parts = wwu([
    ('Artifact', 'The built, versioned package (zip or image).', 'Build once, deploy the same bits everywhere.', 'ECR / ACR / Artifact Registry, S3/Blob/GCS.'),
    ('Configuration', 'Settings per environment.', 'Same artifact, different config (12-factor).', 'Env vars, App Configuration, Parameter Store.'),
    ('Secrets', 'Passwords, API keys.', 'Never in code or images.', 'Secrets Manager, Key Vault, Secret Manager.'),
    ('Health endpoint', 'A URL that says “I am ready”.', 'Platforms decide traffic from it.', '/health returning 200.'),
    ('Traffic router', 'Decides which version gets requests.', 'Enables canary, blue/green, rollback.', 'Alias weights, slot routing, revision split, LB.'),
    ('Release record', 'Version, time, who, change.', 'Audit and incident investigation.', 'Deploy markers, change log.')])

DEEP = ('  <h3>The 12-factor app (the rules that make cloud deploys easy)</h3>\n' + table(['Factor', 'Meaning in practice'], [['Codebase', 'one repo, many deploys'], ['Dependencies', 'declared (requirements.txt), not assumed'], ['Config', 'in the environment, not code'], ['Backing services', 'DB, cache, queue attached by URL'], ['Build, release, run', 'separate stages; releases are immutable'], ['Processes', 'stateless; state in DB/cache'], ['Port binding', 'app serves HTTP on $PORT'], ['Disposability', 'fast start, graceful shutdown'], ['Dev/prod parity', 'environments as similar as possible'], ['Logs', 'write to stdout; platform collects'], ['Admin processes', 'one-off tasks run like the app'], ['Concurrency', 'scale by adding processes']], minw=520) +
    '\n  <h3>Database changes without downtime: expand and contract</h3>\n  <ol><li><b>Expand:</b> add the new column/table; old code ignores it.</li><li><b>Deploy</b> code that writes both old and new, reads new with fallback.</li><li><b>Migrate</b> existing data in the background.</li><li><b>Contract:</b> after all versions use the new shape, remove the old column.</li></ol>\n'
    '  <h3>DORA metrics: how good is your delivery?</h3>\n' + table(['Metric', 'Meaning'], [['Deployment frequency', 'how often you release to production'], ['Lead time for changes', 'commit → production'], ['Change failure rate', '% of releases causing incidents'], ['Time to restore', 'how fast you recover from a bad release']], minw=460) +
    '\n  <p>Safe strategies (canary, blue/green, flags) improve the last two, which lets teams safely improve the first two. Lesson 8.3 automates the whole pipeline.</p>')

clouds = vendor_tabs('<p><b>AWS:</b> Elastic Beanstalk (all-at-once, rolling, immutable, traffic splitting), CodeDeploy (EC2, ECS, Lambda; canary/linear/blue-green with alarm rollback), Lambda versions and aliases, ECS rolling and blue/green, Amplify Hosting; App Runner is closed to new customers (ECS Express Mode replaces it).</p>',
    '<p><b>Azure:</b> App Service deployment slots, slot swap and traffic routing; Container Apps revisions with traffic weights; Azure Functions slots; AKS rolling updates; Azure Deployment Environments; App Configuration feature flags.</p>',
    '<p><b>Google Cloud:</b> Cloud Run revisions with traffic splitting and tags; Cloud Deploy (canary and progressive delivery for GKE and Cloud Run); App Engine versions with traffic splitting; GKE rolling updates; Firebase Remote Config.</p>') + \
    cloud3([['Version unit', 'Lambda version / ECS task def', 'Slot / revision', 'Revision / version'], ['Canary routing', 'Alias weights, CodeDeploy', 'Slot traffic routing, revision weights', 'Revision traffic split, Cloud Deploy'], ['Blue/green', 'CodeDeploy, Beanstalk swap', 'Slot swap', 'Tagged revision + switch'], ['Feature flags', 'AppConfig', 'App Configuration', 'Firebase Remote Config'], ['Registry', 'ECR', 'Azure Container Registry', 'Artifact Registry']])

# ------------------------------------------------------------------ practical
APP = '''mkdir menu && cd menu
cat > app.py <<'EOF'
import os
from flask import Flask
app = Flask(__name__)
VERSION = os.environ.get("APP_VERSION", "v1")
@app.route("/")
def home():
    return f"<h1>TiffinGo menu {VERSION}</h1><p>Today: paneer thali</p>"
@app.route("/health")
def health():
    return "ok"
EOF
printf "flask\\ngunicorn\\n" > requirements.txt
echo "web: gunicorn -b :\\$PORT app:app" > Procfile'''

LAMBDA = '''mkdir menu && cd menu
cat > lambda_function.py <<'EOF'
import os
def lambda_handler(event, context):
    v = os.environ.get("APP_VERSION", "v1")
    return {"statusCode": 200, "headers": {"Content-Type": "text/html"},
            "body": f"<h1>TiffinGo menu {v}</h1><p>Today: paneer thali</p>"}
EOF
zip -q fn.zip lambda_function.py'''

MOCKQ.extend([
 (mock('aws', ['Lambda', 'Functions', 'Create function'], ['Dashboard', 'Applications', 'Functions'], 'Functions',
       [('Author from scratch', 'Function name: tiffingo-menu'), ('Runtime', '▾ Python 3.13'), ('Advanced · Enable function URL', '[x] Auth type NONE')], 'Create function'),
  mock('az', ['Home', 'App Services', 'Create Web App'], ['Basics', 'Deployment', 'Networking', 'Monitoring', 'Review + create'], 'Basics',
       [('Name', 'tiffingo-menu-yourname'), ('Publish', '[x] Code'), ('Runtime stack', '▾ Python 3.12'), ('Region', '▾ Central India'), ('Pricing plan', '▾ Free F1')], 'Review + create'),
  mock('gcp', ['Cloud Run', 'Deploy a web service'], ['Services', 'Jobs', 'Worker pools'], 'Services',
       [('Source', '[x] Continuously deploy from a repository / upload'), ('Service name', 'tiffingo-menu'), ('Region', '▾ asia-south1 (Mumbai)'), ('Authentication', '[x] Allow public access')], 'Create')),
 (mock('aws', ['Lambda', 'tiffingo-menu', 'Versions'], ['Code', 'Test', 'Monitor', 'Configuration', 'Aliases', 'Versions'], 'Versions',
       [('Version 1', 'APP_VERSION = v1'), ('Version 2', 'APP_VERSION = v2'), ('Alias live', '1 → 90% · 2 → 10%')], 'Publish new version'),
  mock('az', ['Home', 'App Services', 'tiffingo-menu', 'Deployment slots'], ['Overview', 'Deployment slots', 'Configuration', 'Scale up'], 'Deployment slots',
       [('tiffingo-menu (PRODUCTION)', 'Traffic % 90'), ('tiffingo-menu-staging', 'Traffic % 10'), ('Note', 'slots need Standard (S1) or higher')], 'Swap'),
  mock('gcp', ['Cloud Run', 'tiffingo-menu', 'Revisions'], ['Metrics', 'SLOs', 'Logs', 'Revisions', 'Triggers'], 'Revisions',
       [('tiffingo-menu-00001', 'v1 · 90%'), ('tiffingo-menu-00002 (tag green)', 'v2 · 10%')], 'Manage traffic')),
 (mock('aws', ['Lambda', 'tiffingo-menu', 'Aliases', 'live'], ['Aliases', 'Versions'], 'Aliases',
       [('Version', '▾ 1'), ('Weighted alias', 'remove additional version')], 'Save'),
  mock('az', ['Home', 'App Services', 'tiffingo-menu', 'Deployment slots'], ['Overview', 'Deployment slots'], 'Deployment slots',
       [('Swap', 'Source: production ⇄ Target: staging'), ('Preview changes', 'settings that will move')], 'Swap'),
  mock('gcp', ['Cloud Run', 'tiffingo-menu', 'Manage traffic'], ['Revisions'], 'Revisions',
       [('tiffingo-menu-00001', '100%'), ('tiffingo-menu-00002', '0% (kept, tag green)')], 'Save')),
])

STEP1 = ('1 · Write the app and deploy v1', tri(
    (['[[Lambda]] → [[Create function]] → [[Author from scratch]], name <code>tiffingo-menu</code>, runtime Python 3.13 → [[Create]].', 'Paste the handler on the right into the editor → [[Deploy]]. [[Configuration]] → [[Environment variables]] → <code>APP_VERSION=v1</code>.', 'Function URL comes in step 2 (on an alias), so rollback is a traffic switch.'],
     LAMBDA + "\nROLE=$(aws iam create-role --role-name tiffingo-menu-role --assume-role-policy-document '{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"lambda.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}' --query Role.Arn --output text)\naws iam attach-role-policy --role-name tiffingo-menu-role --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole\nsleep 10\naws lambda create-function --function-name tiffingo-menu --runtime python3.13 --handler lambda_function.lambda_handler \\\n  --role $ROLE --zip-file fileb://fn.zip --environment 'Variables={APP_VERSION=v1}'\naws lambda wait function-active-v2 --function-name tiffingo-menu\naws lambda publish-version --function-name tiffingo-menu --query Version --output text",
     '<code>1</code> — version 1 is an immutable snapshot of code + configuration.'),
    (['[[App Services]] → [[Create]] → [[Web App]]: name <code>tiffingo-menu-yourname</code>, [[Code]], Python 3.12, Central India, plan [[Free F1]] → [[Create]].', 'Simplest path: run <code>az webapp up</code> from the folder (right) — it creates the app and deploys your code.'],
     APP + '\nAPP=tiffingo-menu-$RANDOM\naz webapp up --name $APP --resource-group rg-deploy --location centralindia --runtime "PYTHON:3.12" --sku F1\naz webapp config appsettings set -g rg-deploy -n $APP --settings APP_VERSION=v1\ncurl -s https://$APP.azurewebsites.net/',
     '<code>&lt;h1&gt;TiffinGo menu v1&lt;/h1&gt;</code> (the first request can take 30–60 s while the app starts).'),
    (['[[Cloud Run]] → [[Deploy container]] / [[Create service]] → from source; name <code>tiffingo-menu</code>, asia-south1, [[Allow public access]] → [[Create]].', 'Or run the CLI on the right in Cloud Shell — it builds the code with Cloud Build and deploys it.'],
     APP + '\ngcloud run deploy tiffingo-menu --source . --region asia-south1 --allow-unauthenticated --set-env-vars APP_VERSION=v1\nURL=$(gcloud run services describe tiffingo-menu --region asia-south1 --format="value(status.url)")\ncurl -s $URL',
     'build logs, then “Service [tiffingo-menu] revision [tiffingo-menu-00001-…] has been deployed and is serving 100 percent of traffic”, and the v1 heading from curl. Accept enabling the APIs and creating the Artifact Registry repository when asked.')),
    'Same app, three platforms: functions (Lambda), PaaS (App Service), serverless containers (Cloud Run).')

STEP2 = ('2 · Deploy v2 beside v1 and release it to 10% (canary)', tri(
    (['[[Configuration]] → set <code>APP_VERSION=v2</code> → [[Versions]] → [[Publish new version]] (2).', '[[Aliases]] → [[Create alias]] <code>live</code> → version 1, [[Weighted alias]] version 2 at 10%.', 'Alias → [[Configuration]] → [[Function URL]] → [[Create]], auth type [[NONE]].'],
     "aws lambda update-function-configuration --function-name tiffingo-menu --environment 'Variables={APP_VERSION=v2}'\naws lambda wait function-updated-v2 --function-name tiffingo-menu\naws lambda publish-version --function-name tiffingo-menu --query Version --output text\naws lambda create-alias --function-name tiffingo-menu --name live --function-version 1 \\\n  --routing-config '{\"AdditionalVersionWeights\":{\"2\":0.1}}'\naws lambda add-permission --function-name tiffingo-menu --qualifier live --statement-id url --action lambda:InvokeFunctionUrl \\\n  --principal '*' --function-url-auth-type NONE\naws lambda add-permission --function-name tiffingo-menu --qualifier live --statement-id url-invoke --action lambda:InvokeFunction \\\n  --principal '*' --invoked-via-function-url\nURL=$(aws lambda create-function-url-config --function-name tiffingo-menu --qualifier live --auth-type NONE --query FunctionUrl --output text)\nfor i in $(seq 20); do curl -s $URL | grep -o 'menu v[12]'; done | sort | uniq -c",
     'about 18 × <code>menu v1</code> and 2 × <code>menu v2</code> (random split). Public function URLs need both permissions shown.'),
    (['Slots need [[Standard S1]] or higher: [[Scale up (App Service plan)]] → S1 (about ₹8 per hour — scale back to F1 or delete afterwards).', '[[Deployment slots]] → [[Add slot]] <code>staging</code> → deploy v2 there → set staging [[Traffic %]] to 10.'],
     'PLAN=$(az webapp show -g rg-deploy -n $APP --query appServicePlanId -o tsv)\naz appservice plan update --ids $PLAN --sku S1\naz webapp deployment slot create -g rg-deploy -n $APP --slot staging --configuration-source $APP\naz webapp config appsettings set -g rg-deploy -n $APP --slot staging --slot-settings APP_VERSION=v2\nzip -qr app.zip app.py requirements.txt\naz webapp deploy -g rg-deploy -n $APP --slot staging --src-path app.zip --type zip\ncurl -s https://$APP-staging.azurewebsites.net/\naz webapp traffic-routing set -g rg-deploy -n $APP --distribution staging=10',
     'the v2 heading from the staging URL (tested privately first — blue/green), then 10% of production traffic routed to staging (a cookie keeps each visitor on one side).'),
    (['[[Cloud Run]] → service → [[Edit &amp; deploy new revision]] → variable <code>APP_VERSION=v2</code>, untick [[Serve this revision immediately]] → [[Deploy]].', '[[Revisions]] → [[Manage traffic]] → new revision 10%.'],
     'gcloud run deploy tiffingo-menu --source . --region asia-south1 --set-env-vars APP_VERSION=v2 --no-traffic --tag green\ngcloud run services describe tiffingo-menu --region asia-south1 --format="value(status.traffic)"\nNEW=$(gcloud run revisions list --service tiffingo-menu --region asia-south1 --format="value(name)" --limit 1)\ngcloud run services update-traffic tiffingo-menu --region asia-south1 --to-revisions $NEW=10\nfor i in $(seq 20); do curl -s $URL | grep -o "menu v[12]"; done | sort | uniq -c',
     'v2 reachable first at its own tag URL (<code>https://green---tiffingo-menu-….run.app</code>) with 0% traffic, then roughly 18 × v1 and 2 × v2.')),
    'Deploy and release are now separate: v2 existed (and was testable) before any user saw it.')

STEP3 = ('3 · Promote — then roll back in one command', tri(
    (['Promote: alias <code>live</code> → version 2, remove weighting → [[Save]].', 'Roll back: alias <code>live</code> → version 1 → [[Save]] — instant.'],
     "aws lambda update-alias --function-name tiffingo-menu --name live --function-version 2 --routing-config '{}'\ncurl -s $URL\n# something wrong? roll back:\naws lambda update-alias --function-name tiffingo-menu --name live --function-version 1 --routing-config '{}'\ncurl -s $URL",
     '<code>menu v2</code>, then after the rollback <code>menu v1</code> — no rebuild, no redeploy.'),
    (['[[Deployment slots]] → [[Swap]] staging ⇄ production → [[Swap]]. Production now runs v2; the old v1 sits in staging.', 'Roll back: swap again.'],
     'az webapp traffic-routing clear -g rg-deploy -n $APP\naz webapp deployment slot swap -g rg-deploy -n $APP --slot staging --target-slot production\ncurl -s https://$APP.azurewebsites.net/\n# roll back:\naz webapp deployment slot swap -g rg-deploy -n $APP --slot staging --target-slot production',
     '<code>menu v2</code> on production after the swap; v1 again after swapping back. (APP_VERSION was a slot setting, so it stayed with each slot’s code.)'),
    (['[[Manage traffic]] → new revision 100% → [[Save]].', 'Roll back: old revision 100%.'],
     'gcloud run services update-traffic tiffingo-menu --region asia-south1 --to-latest\ncurl -s $URL\n# roll back to the first revision:\nOLD=$(gcloud run revisions list --service tiffingo-menu --region asia-south1 --format="value(name)" --sort-by=metadata.creationTimestamp --limit 1)\ngcloud run services update-traffic tiffingo-menu --region asia-south1 --to-revisions $OLD=100\ncurl -s $URL',
     '<code>menu v2</code>, then <code>menu v1</code> after rollback — the old revision was never deleted.')),
    'Rollback is a traffic change measured in seconds because the old version is still deployed.')

prac = practical(OWN_INTRO + ' You deploy one tiny web app, release v2 to 10% of users, promote it, and roll back — with real canary routing. Lambda and Cloud Run stay within free tiers; Azure slots need the S1 tier for about an hour (≈ ₹8–10), or skip Azure steps 2–3.', [SETUP_STEP, STEP1, STEP2, STEP3],
    cleanup='<b>AWS:</b> <code>aws lambda delete-function --function-name tiffingo-menu</code> (removes versions, alias and URL); detach the policy and delete <code>tiffingo-menu-role</code>. '
            '<b>Azure:</b> <code>az group delete -n rg-deploy --yes --no-wait</code> (stops the S1 charge). '
            '<b>Google Cloud:</b> <code>gcloud run services delete tiffingo-menu --region asia-south1 --quiet</code>; delete the <code>cloud-run-source-deploy</code> repository in Artifact Registry to avoid storage charges.')

mist = mistakes([
    ['Building separately for each environment.', 'Different build commands.', 'Build once; promote the same artifact with different config.'],
    ['Secrets inside the code or image.', 'Convenience.', 'Secrets Manager / Key Vault / Secret Manager, injected at runtime.'],
    ['Deleting the old version right after release.', 'Tidiness.', 'Keep it until the new one has proven itself.'],
    ['Breaking database changes with rolling deploys.', 'v1 and v2 share the DB.', 'Expand → migrate → contract.'],
    ['Canary without metrics.', 'Nobody compares.', 'Alarm-based automatic rollback.'],
    ['Manual fixes on production servers.', '“Just this once.”', 'Immutable deployments; change only through the pipeline.']])

cert = table(['Exam / syllabus', 'What is asked'], [['C-DAC PGCP-BDA', 'Deploying an application on the cloud (lab).'], ['AWS CLF-C02', 'Elastic Beanstalk, CodeDeploy, Lambda, ECS/EKS at a high level; deployment options.'], ['AZ-900', 'App Service, Container Apps, Azure Functions; deployment slots.'], ['Google Cloud Digital Leader', 'Cloud Run, App Engine, GKE; modernising deployment.']], minw=560) + \
    qx('1. Which deploys an app by uploading code while AWS handles capacity, load balancing and scaling?', ['Elastic Beanstalk', 'CloudTrail', 'Snowball', 'Route 53'], 0, 'PaaS.') + \
    qx('2. Two identical environments with a traffic switch is…', ['blue/green', 'rolling', 'recreate', 'sharding'], 0, 'Blue/green.') + \
    qx('3. Sending 10% of traffic to a new version first is…', ['canary', 'all-at-once', 'immutable', 'recreate'], 0, 'Canary.') + \
    qx('4. Azure App Service feature for staging and swapping versions?', ['Deployment slots', 'Availability sets', 'Blueprints', 'Arc'], 0, 'Slots.') + \
    qx('5. Which AWS service automates deployments to EC2, ECS and Lambda with canary and blue/green?', ['CodeDeploy', 'CodeCommit', 'CloudFormation', 'Config'], 0, 'CodeDeploy.') + \
    qx('6. Where should database passwords live?', ['in the image', 'in Git', 'in a secrets manager injected at runtime', 'in the URL'], 2, 'Secrets manager.')

proj = miniproject('Mini project: zero-fear release for the TiffinGo menu',
    'Design and run a complete safe release.',
    ['<b>Target:</b> choose functions, PaaS or containers for the menu app (Lesson 2.5) and justify.',
     '<b>Artifact:</b> show where the versioned artifact lives and how config/secrets are injected.',
     '<b>Strategy:</b> pick canary or blue/green; write the % steps and wait times.',
     '<b>Signals:</b> name the metrics and thresholds that trigger rollback (Lesson 8.1).',
     '<b>Run it:</b> do steps 1–3 on your cloud and record the commands and timings.',
     '<b>DB change:</b> describe an expand → migrate → contract plan for adding a “spice level” column.'],
    'A release runbook with commands, rollback trigger and measured rollback time.', '2.5 + 7.4 + 8.1 + 8.2.')

assemble_v2(HERE, story_h2='The 7 pm release that broke everything', hook_html=hk,
    narration='TiffinGo’s new menu page was copied onto the production server at 7 pm, just before dinner orders. It broke for every customer, and putting the old page back took 40 minutes.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Deploying an application on the cloud',
    formal='<b>Deploying an application on the cloud</b> means taking a built, versioned artifact (code package or container image), placing it on a cloud runtime — virtual machines, an application platform, containers or functions — with environment-specific configuration and secrets, and <b>releasing</b> it to users through a strategy such as all-at-once, rolling, blue/green, canary or feature flags, with health checks, monitoring and a rollback path.',
    simple='Putting a new version of your app on cloud servers and moving users to it safely, so you can switch back quickly if something goes wrong.',
    interview=['“I build once, store a versioned artifact, deploy it beside the current version, and release gradually — canary or blue/green — watching error rate and latency, with rollback as a traffic switch.”', '“On AWS that is Lambda aliases or CodeDeploy; on Azure, App Service slots; on Google Cloud, Cloud Run revision traffic splitting.”'],
    terms_rows=[('Artifact', 'Built, versioned package.'), ('Deploy vs release', 'Install vs send users.'), ('Rolling', 'Batch by batch.'), ('Blue/green', 'Two environments, one switch.'), ('Canary', 'Small % first.'), ('Immutable', 'Replace, never patch.'), ('Feature flag', 'Runtime on/off switch.'), ('Rollback', 'Return to previous version.')],
    exam='Know which service deploys what (Elastic Beanstalk, CodeDeploy, App Service, Cloud Run) and the strategy names: blue/green, canary, rolling, in-place, immutable.',
    picture_h2='From code to customers', picture_html=picture,
    after_picture=[('types', 'Types, one by one', 'Six deployment strategies, one by one', TYPES)],
    how_h2='Inside a safe cloud deployment', how_intro='What the platform does between “v2 is built” and “everyone is on v2”.', how_anim=DEPLOY,
    parts_h2='Six things every deployment needs', parts_html=parts, lv='',
    myth_rows=[('If it works on my laptop it will work in production.', 'Config, data and scale differ.', 'Canary.'), ('Rollback means rebuilding the old code.', 'Keep the old version deployed; switch traffic.', 'Step 3.'), ('Zero downtime needs Kubernetes.', 'Slots, aliases and revisions do it too.', 'Practical.')],
    extra_secs=[('deep', 'Deep dive', '12-factor apps, expand-and-contract, DORA metrics', DEEP)],
    clouds_html=clouds, practical_html=prac, mistakes_html=mist, cert_html=cert, project_html=proj,
    can_now=['Explain deploy vs release and the path from code to users.', 'Compare all-at-once, rolling, blue/green, canary, immutable and feature flags.', 'Deploy a web app on Lambda, App Service or Cloud Run.', 'Run a real 10% canary and a one-command rollback.', 'Plan database changes that do not break releases.'],
    next_html='<a href="../03-devops-on-the-cloud-lifecycle-agile-and-ci-cd/">8.3 DevOps on the cloud: lifecycle, Agile and CI/CD</a>.',
    pre='<b>Before you start:</b> 2.5 (choosing a model), 7.4 (architecture styles) and 8.1 (monitoring).')
