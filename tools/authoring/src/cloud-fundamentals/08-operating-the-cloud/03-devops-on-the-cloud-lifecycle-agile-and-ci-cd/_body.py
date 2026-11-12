import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
def cap(frames, steps, title, intro, panel, aria, hid, delay=5500):
    return anim_one('Animated', title, intro, panel, aria, cap_frames(frames, steps), [s[0] + '.' for s in steps], delay=delay, hid=hid)


hk = hook('TiffinGo’s developers finish features on Monday. Testers get them on Thursday. Operations deploys “when there is a window” — every second Saturday. A one-line price fix takes 12 days to reach customers. Where do the 12 days go?',
    'Into hand-offs and waiting. <b>DevOps</b> removes them: one team owns the whole <b>lifecycle</b> (plan → code → build → test → release → deploy → operate → monitor), works in short <b>Agile</b> iterations, and lets a <b>CI/CD pipeline</b> do the repetitive steps on every commit. This lesson explains seven practices one by one — Scrum, Kanban, continuous integration, continuous delivery, continuous deployment, infrastructure as code and GitOps — animates one commit travelling through a pipeline, and on <b>your own</b> account you build a pipeline that tests, deploys and creates infrastructure from code.',
    ['Continuous delivery vs continuous deployment: one approval button apart.', 'Why a failing test should stop the pipeline in minutes, not days.', 'How infrastructure becomes code that is reviewed like any other change.'])

def story_scene():
    o = t(180, 12, 'Where does a one-line fix wait?', 9, 'ink', bold=True)
    S = [('Dev', 'Mon'), ('Test team', 'Thu'), ('Ops window', 'Sat+1'), ('Customers', 'day 12')]
    for i, (a, b) in enumerate(S):
        x = 8 + i * 88
        o += box(x, 32, 80, 52, ['blue', 'amber', 'red', 'green'][i], rx=8) + t(x + 40, 54, a, 8, 'ink', bold=True) + t(x + 40, 70, b, 7.2, 'ink2')
        if i < 3: o += arrow(x + 80, 58, x + 88, 58) + t(x + 84, 96, 'wait', 6.6, 'ink2')
    o += t(180, 118, 'With CI/CD: commit → customers in under an hour', 7.6, 'ink', bold=True)
    return o
scene_svg = scene('Four boxes: developer on Monday, test team Thursday, ops window the Saturday after next, customers on day 12, with waiting between each; with CI/CD it takes under an hour.', story_scene(), 'Most of the 12 days is <tspan font-weight="700" class="s-acc">waiting</tspan>, not work.', h=128)
dialogue = '''R> Sir, the developers say testing is slow; testers say code arrives broken; ops says deployments are risky.
A> Three teams, three queues, and nobody owns the whole path. DevOps makes one team responsible from idea to production.
K> But someone still has to test and deploy.
A> A pipeline does it — on every commit, in minutes. People review code and decide what to build; machines repeat the boring steps.
R> And planning?
A> Short Agile iterations: small changes, shipped often, measured in production. Let’s go practice by practice.'''

# ------------------------------------------------------------------ picture
def loopfig():
    o = t(320, 16, 'The DevOps lifecycle (the infinity loop)', 11, 'ink', bold=True)
    o += '<path d="M320 110 C 260 40, 120 40, 120 110 C 120 180, 260 180, 320 110 C 380 40, 520 40, 520 110 C 520 180, 380 180, 320 110 Z" style="fill:none;stroke:var(--blue);stroke-width:3"/>'
    L = [('Plan', 150, 50), ('Code', 92, 112), ('Build', 150, 172), ('Test', 262, 168), ('Release', 378, 52), ('Deploy', 490, 50), ('Operate', 548, 112), ('Monitor', 490, 172)]
    for a, x, y in L:
        o += box(x - 34, y - 12, 68, 22, 'amber' if a in ('Plan', 'Code', 'Build', 'Test') else 'green', rx=11) + t(x, y + 3, a, 7.6, 'ink', bold=True)
    o += t(200, 112, 'Dev', 10, 'ink', bold=True) + t(440, 112, 'Ops', 10, 'ink', bold=True)
    o += t(320, 204, 'Feedback from monitoring flows back into planning — the loop never ends.', 7.4, 'ink2')
    return o
LOOP = bigfig('The DevOps infinity loop: plan, code, build, test on the Dev side; release, deploy, operate, monitor on the Ops side; monitoring feeds back into planning.', loopfig(), h=212)

def calmfig():
    o = t(320, 16, 'CALMS: what DevOps really changes', 11, 'ink', bold=True)
    C = [('Culture', 'shared ownership, blameless reviews', 'violet'), ('Automation', 'pipelines, IaC, tests', 'blue'), ('Lean', 'small batches, less waiting', 'green'), ('Measurement', 'DORA metrics, SLOs', 'amber'), ('Sharing', 'docs, dashboards, runbooks', 'card')]
    for i, (a, b, tn) in enumerate(C):
        x = 12 + i * 126
        o += box(x, 34, 118, 80, tn, rx=8) + t(x + 59, 62, a, 9, 'ink', bold=True) + t(x + 59, 86, b, 6.4, 'ink2')
    o += t(320, 136, 'Tools are only the “A”. Buying a CI server without changing culture gives you faster hand-offs, not DevOps.', 7.4, 'ink2')
    return o
CALMS = bigfig('CALMS model: culture, automation, lean, measurement, sharing.', calmfig(), h=146)

picture = ('  <p>DevOps is a way of working across the whole lifecycle — usually drawn as an infinity loop:</p>\n' + LOOP +
           '\n  <p>And it is more than tools:</p>\n' + CALMS +
           '\n  <h3>Before and after</h3>\n' + table(['', 'Traditional (waterfall + silos)', 'DevOps + Agile + CI/CD'], [
               ['Release size', 'big, months of changes', 'small, hours or days'], ['Testing', 'separate phase at the end', 'automated on every commit'], ['Deployment', 'manual, risky windows', 'pipeline, any time, with rollback'],
               ['Infrastructure', 'tickets, hand-built servers', 'code in Git, reviewed'], ['Who is on call', 'ops team only', 'the team that built it'], ['Feedback', 'after release, from customers', 'minutes, from tests and monitoring']], minw=600))

# ------------------------------------------------------------------ how: one commit
RN = {'dev': (4, 54, 50, 50, 'user', 'Developer', 'git push'), 'git': (66, 4, 62, 46, 'disk', 'Repository', 'pull request'), 'ci': (66, 104, 62, 46, 'gear', 'CI build', 'tests, scan'),
      'art': (142, 54, 60, 50, 'server', 'Artifact', 'image v42'), 'stg': (216, 4, 62, 46, 'cloud', 'Staging', 'auto deploy'), 'ok': (216, 104, 62, 46, 'shield', 'Gate', 'approve / auto'), 'prod': (292, 54, 64, 50, 'globe', 'Production', 'canary')}
RS = [dict(on=['dev', 'git'], hot='git', move=(54, 79, 72, 30, 'push'), head='Step 1 · A small change is pushed', text='Kabir changes the price rule and opens a pull request. A teammate reviews it;', text2='the push triggers the pipeline automatically (webhook).', svc='GitHub · GitLab · Azure Repos · Bitbucket'),
      dict(on=['git', 'ci'], hot='ci', move=(97, 50, 97, 104, 'trigger'), head='Step 2 · CI builds and tests in minutes', text='A fresh build machine installs dependencies, runs unit tests, lint and a security', text2='scan. One failure stops the pipeline and tells Kabir within 5 minutes.', svc='CodeBuild · Azure Pipelines / GitHub Actions · Cloud Build'),
      dict(on=['ci', 'art'], hot='art', move=(128, 127, 150, 90, 'package'), head='Step 3 · Build once, store the artifact', text='Passing code is packaged once (container image v42) and pushed to a registry.', text2='Every later stage uses these exact bits.', svc='ECR · Azure Container Registry · Artifact Registry'),
      dict(on=['art', 'stg'], hot='stg', move=(202, 66, 226, 30, 'deploy'), head='Step 4 · Auto-deploy to staging', text='The pipeline deploys v42 to staging, runs integration and smoke tests against it,', text2='and records the result.', svc='CodeDeploy / CodePipeline · release stages · Cloud Deploy'),
      dict(on=['stg', 'ok'], hot='ok', move=(247, 50, 247, 104, 'gate'), head='Step 5 · The production gate', text='Continuous delivery: a person clicks “approve”. Continuous deployment: the gate is', text2='automatic when all checks pass.', svc='Manual approval actions / environments with reviewers'),
      dict(on=list(RN), hot='prod', move=(278, 127, 298, 90, 'release'), head='Step 6 · Release safely, watch, learn', text='Canary to production (Lesson 8.2), monitor golden signals (8.1). Commit → customers:', text2='about 40 minutes instead of 12 days.', svc='Lead time and deployment frequency improve together')]
PIPE = flow_anim('One commit through a CI/CD pipeline', 'Follow TiffinGo’s one-line price fix from git push to production.', 'CI/CD pipeline', 'Animation: developer pushes; CI builds and tests; artifact stored; staging deploy; production gate; canary release to production.', RN, RS, hid='cicdflow')

# ------------------------------------------------------------------ types
def mapfig():
    o = t(320, 16, 'Seven practices of DevOps on the cloud', 11, 'ink', bold=True)
    items = [('1', 'Scrum', 'Agile in sprints', 'violet'), ('2', 'Kanban', 'Agile as a flow', 'violet'), ('3', 'Continuous integration', 'merge + test often', 'blue'), ('4', 'Continuous delivery', 'always releasable', 'green'),
             ('5', 'Continuous deployment', 'every green commit ships', 'green'), ('6', 'Infrastructure as code', 'servers from files', 'amber'), ('7', 'GitOps', 'Git is the source of truth', 'amber')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 12 + (i % 4) * 156; y = 32 + (i // 4) * 84
        o += box(x, y, 148, 70, tn, rx=8) + pin(x + 16, y + 16, n) + t(x + 80, y + 34, a, 7.8, 'ink', bold=True) + t(x + 78, y + 54, b, 6.6, 'ink2')
    o += t(320, 210, '1–2 decide how work is planned; 3–5 how code reaches users; 6–7 how infrastructure is managed.', 7.4, 'ink2')
    return o
MAP = bigfig('Map of seven practices: Scrum, Kanban, continuous integration, continuous delivery, continuous deployment, infrastructure as code, GitOps.', mapfig(), h=222)

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

A1 = mk(['Sprint planning', 'Two-week sprint', 'Review + retro'], ['backlog|top items|sprint goal', 'sprint|daily stand-up|build + test', 'review|demo to users|retro: improve'], ['violet', 'blue', 'green'],
        ['the team picks the top backlog items for a sprint goal', 'it builds them in a fixed time-box with a 15-minute daily stand-up', 'working software is demoed; the team reflects and improves'],
        [('Plan', 'Pick top backlog items and set a sprint goal.', ''), ('Sprint', '1–4 weeks of building with daily stand-ups.', ''), ('Inspect', 'Demo working software; retrospective to improve.', '')],
        'Scrum in action', 'Work in short sprints.', 'Scrum', 'Animation: sprint planning; sprint; review and retrospective.', 's1anim')
T1 = vt(1, 'Scrum (Agile in sprints)', 'violet',
    '<b>Scrum</b> is an Agile framework in which a small cross-functional team delivers working increments of a product in fixed time-boxes called <b>sprints</b> (usually 1–4 weeks), using defined roles (Product Owner, Scrum Master, Developers), events (planning, daily scrum, review, retrospective) and artifacts (product backlog, sprint backlog, increment).',
    'Cooking a wedding menu in rounds: each round you finish a few complete dishes, let the family taste them, and adjust the next round.',
    'TiffinGo’s app team runs two-week sprints; this sprint’s goal is “customers can pause their subscription”, demoed to the operations team on day 10.',
    'Jira, Azure Boards, GitHub Projects, GitLab issues; Scrum Guide (Schwaber and Sutherland).', '', A1,
    'work can be planned in short cycles and the team benefits from a regular rhythm.',
    'work is mostly unplanned interrupts (support, ops) — Kanban fits better.',
    'Working in short fixed periods, finishing a few useful features each time and improving after each one.',
    [('Backlog', 'Ordered list by the Product Owner.'), ('Planning', 'Choose items for the sprint goal.'), ('Daily scrum', '15 minutes: progress and blockers.'), ('Review', 'Show working increment.'), ('Retrospective', 'Improve the way of working.')],
    [('sprint', 'a fixed time-box, often two weeks'), ('backlog', 'ordered list of work'), ('increment', 'working, usable product piece at sprint end')],
    table(['', 'Scrum', 'Kanban'], [['Cadence', 'fixed sprints', 'continuous flow'], ['Roles', 'defined', 'none required'], ['Change mid-way', 'avoid during sprint', 'any time']], minw=420),
    ['Product teams', 'App and web development', 'Projects with a clear goal'],
    'The Agile Manifesto (2001) gave the values; Scrum is the most widely used Agile framework in surveys of software teams.',
    'Sprints and CI/CD fit together: the increment should be deployable (ideally deployed) during the sprint, not saved for a big release.')

A2 = mk(['Board with columns', 'Limit work in progress', 'Pull the next item'], ['board|to do · doing|review · done', 'WIP limit|max 3 in doing|finish first', 'flow|pull when free|measure cycle time'], ['violet', 'amber', 'green'],
        ['work is visible on a board with columns', 'each column has a work-in-progress limit', 'people pull new work only when they finish — flow is measured'],
        [('Visualise', 'All work on a board with columns.', ''), ('Limit', 'Work-in-progress limits per column.', ''), ('Flow', 'Pull new work when capacity frees up; measure cycle time.', '')],
        'Kanban in action', 'Stop starting, start finishing.', 'Kanban', 'Animation: board with columns; WIP limits; pull the next item.', 's2anim')
T2 = vt(2, 'Kanban (Agile as a flow)', 'violet',
    '<b>Kanban</b> is a flow-based method that visualises work on a board, limits work in progress (WIP) in each stage, and has team members pull new work only when capacity is free, aiming to reduce waiting and improve cycle time continuously without fixed iterations.',
    'A restaurant kitchen ticket rail: orders hang in a line, each cook takes the next ticket only after finishing one, and nobody starts ten dishes at once.',
    'TiffinGo’s platform/ops team uses Kanban: incidents, patching and small requests flow through “To do → Doing (max 3) → Review → Done”.',
    'Jira, Azure Boards, GitHub Projects, Trello; originally from Toyota’s production system.', '', A2,
    'work arrives unpredictably (support, operations) or you want continuous flow.',
    'the team never limits WIP — then it is just a to-do list on a wall.',
    'A board showing all work, with a limit on how many things are in progress, so tasks get finished faster.',
    [('Map stages', 'Columns for each step.'), ('Set WIP', 'Limits per column.'), ('Pull', 'Take work only when free.'), ('Measure', 'Cycle time, throughput.'), ('Improve', 'Fix bottlenecks.')],
    [('WIP', 'work in progress'), ('cycle time', 'time from start to done for one item'), ('throughput', 'items finished per week')],
    table(['', 'Kanban', 'Scrum'], [['Planning', 'continuous', 'per sprint'], ['Measure', 'cycle time', 'velocity'], ['Best for', 'ops, support', 'product features']], minw=420),
    ['Operations and SRE teams', 'Support desks', 'Maintenance work'],
    'Kanban came from Toyota’s production system in the 1950s and was adapted for software in the 2000s.',
    'Little’s Law: average cycle time = WIP ÷ throughput. Halving WIP roughly halves waiting time without anyone working harder.')

A3 = mk(['Commit often', 'Automatic build + test', 'Fast feedback'], ['commit|small change|to main daily', 'CI build|compile, test|lint, scan', 'feedback|pass / fail|in minutes'], ['blue', 'amber', 'green'],
        ['developers merge small changes into the main branch at least daily', 'each merge triggers an automated build and test run', 'everyone knows within minutes whether main still works'],
        [('Commit', 'Small changes merged to main at least daily.', ''), ('Build', 'Each merge triggers automated build and tests.', ''), ('Feedback', 'Pass/fail within minutes; broken builds fixed first.', '')],
        'Continuous integration in action', 'Integrate early, test always.', 'CI', 'Animation: commit often; automatic build and test; fast feedback.', 's3anim')
T3 = vt(3, 'Continuous integration (CI)', 'blue',
    '<b>Continuous integration</b> is the practice of merging every developer’s changes into a shared main branch frequently (at least daily), with each merge automatically built and tested, so integration problems are found within minutes and the main branch always stays in a working state.',
    'Several cooks tasting the shared curry after every ingredient they add, instead of all adding their spices separately and tasting only at the end.',
    'Every TiffinGo pull request runs 300 unit tests and a dependency scan in 4 minutes; merges are blocked until it is green (practical step 2).',
    'AWS CodeBuild; Azure Pipelines, GitHub Actions; Google Cloud Build; Jenkins, GitLab CI.', '', A3,
    'more than one person changes the same codebase — i.e. almost always.',
    'tests are slow or flaky — fix them first, or people ignore red builds.',
    'Automatically building and testing the code every time someone adds a change, so mistakes are found quickly.',
    [('Trunk', 'Short-lived branches, merge daily.'), ('Trigger', 'Webhook on push / PR.'), ('Build', 'Clean environment each time.'), ('Test', 'Unit, lint, security scan.'), ('Report', 'Status on the pull request.')],
    [('main / trunk', 'the shared branch everyone integrates into'), ('pull request', 'a request to merge a change, with review'), ('flaky test', 'a test that sometimes fails without a real bug')],
    table(['', 'CI', 'CD (delivery)'], [['Ends with', 'tested build', 'releasable artifact in staging'], ['Covers', 'build + test', 'build + test + deploy pipeline'], ['Question answered', 'does it work?', 'can we release it now?']], minw=440),
    ['All software teams', 'Open-source projects', 'Infrastructure code (IaC tests)'],
    'Open-source projects run CI on every pull request from strangers — a failing check is how maintainers protect the main branch.',
    'Keep CI under 10 minutes. Slow pipelines make people batch changes, which brings back the integration pain CI removes.')

A4 = mk(['Pipeline after CI', 'Deploy to staging', 'Release on a click'], ['pipeline|artifact v42|automated stages', 'staging|integration tests|smoke tests', 'approve|human button|deploy prod'], ['green', 'blue', 'amber'],
        ['every green build flows into an automated release pipeline', 'it is deployed and tested in production-like staging', 'production release is one approved click, any day'],
        [('Pipeline', 'Every passing build enters an automated pipeline.', ''), ('Staging', 'Deployed and tested in a production-like environment.', ''), ('Approve', 'Release to production is one approved click.', '')],
        'Continuous delivery in action', 'Always ready to release.', 'Continuous delivery', 'Animation: pipeline after CI; staging deploy; release on approval.', 's4anim')
T4 = vt(4, 'Continuous delivery', 'green',
    '<b>Continuous delivery</b> extends CI so that every change that passes the automated pipeline is deployed to staging environments and is always in a releasable state; releasing to production is a business decision made with a single manual approval rather than a technical project.',
    'A packed tiffin on the counter, ready to go: delivery happens the moment someone says “send it”.',
    'TiffinGo’s payments service uses continuous delivery: every merge reaches staging automatically; the payments lead approves production releases after a quick check.',
    'AWS CodePipeline (with manual approval), Azure Pipelines environments with approvals, GitHub Actions environments with reviewers, Google Cloud Deploy promotions.', '', A4,
    'releases need a human or compliance decision but should be easy and frequent.',
    'approval becomes a weekly committee — then you are back to batch releases.',
    'Keeping the software always ready to go live, so releasing is just pressing an approve button.',
    [('Stages', 'Build → test → staging → prod.'), ('Environments', 'Staging mirrors production.'), ('Tests', 'Integration, smoke, performance.'), ('Approval', 'Manual gate for prod.'), ('Release', 'Same artifact, safe strategy.')],
    [('staging', 'production-like environment for final checks'), ('gate', 'a check that must pass before the next stage'), ('promotion', 'moving the same artifact to the next environment')],
    table(['', 'Continuous delivery', 'Continuous deployment'], [['Production step', 'manual approval', 'automatic'], ['Requires', 'good automation', 'excellent tests + monitoring'], ['Typical for', 'regulated systems', 'web/SaaS products']], minw=440),
    ['Banking and payments', 'Enterprise apps', 'Regulated industries'],
    'Jez Humble and David Farley’s book “Continuous Delivery” (2010) defined the practice and the deployment pipeline idea.',
    'Make the approval meaningful: show the approver the change list, test results and risk; otherwise it becomes rubber-stamping.')

A5 = mk(['Commit merged', 'All checks pass', 'Live automatically'], ['merge|to main|reviewed', 'checks|tests, canary|alarms quiet', 'production|no human step|minutes later'], ['blue', 'amber', 'green'],
        ['a reviewed change is merged into main', 'every automated check, including a canary, passes', 'it goes live with no manual step'],
        [('Merge', 'A reviewed change is merged into main.', ''), ('Checks', 'All automated checks and canary analysis pass.', ''), ('Live', 'Production is updated automatically.', '')],
        'Continuous deployment in action', 'Every green commit ships.', 'Continuous deployment', 'Animation: commit merged; checks pass; live automatically.', 's5anim')
T5 = vt(5, 'Continuous deployment', 'green',
    '<b>Continuous deployment</b> goes one step beyond continuous delivery: every change that passes all automated stages — tests, security checks, canary analysis — is released to production automatically with no manual approval, relying on strong automated testing, progressive delivery and monitoring with automatic rollback.',
    'A conveyor belt that sends each finished tiffin straight to the delivery rider — quality checks are built into the belt itself.',
    'TiffinGo’s menu website deploys every merged change automatically through a 10% canary; an alarm on errors rolls it back without waking anyone.',
    'CodePipeline + CodeDeploy with alarms, GitHub Actions to App Service/AKS, Cloud Build + Cloud Deploy automatic promotion, Argo CD / Flux with progressive delivery.', '', A5,
    'tests and monitoring are trustworthy and changes are small.',
    'test coverage is weak or rollback is manual — you would automate outages.',
    'Every change that passes all automatic checks goes live by itself, without anyone pressing a button.',
    [('Small PRs', 'Reviewed, behind flags if needed.'), ('Full automation', 'Tests at every level.'), ('Progressive', 'Canary in production.'), ('Auto-rollback', 'Alarms revert.'), ('Observe', 'DORA metrics.')],
    [('progressive delivery', 'releasing gradually with automated checks'), ('auto-rollback', 'reverting automatically on bad metrics'), ('change failure rate', '% of releases causing problems')],
    table(['', 'Continuous deployment', 'Scheduled releases'], [['Release size', 'one small change', 'many changes'], ['Risk per release', 'low', 'high'], ['Releases per day', 'many', 'rare']], minw=440),
    ['SaaS and websites', 'Internal tools', 'Microservices'],
    'High-performing teams in DORA research deploy on demand, often multiple times per day, with lower change failure rates than teams that release rarely.',
    'Combine with feature flags (Lesson 8.2): code ships continuously, features are released when the business is ready.')

A6 = mk(['Write a template', 'Review + plan', 'Apply'], ['template|bucket, VPC, DB|in Git', 'plan|what will change|code review', 'apply|cloud matches code|repeatable'], ['amber', 'blue', 'green'],
        ['infrastructure is described in a file (declarative)', 'changes are reviewed and a plan shows exactly what will change', 'the tool creates or updates resources to match the code'],
        [('Describe', 'Infrastructure is written as a declarative file in Git.', ''), ('Plan', 'Reviewers see exactly what will change.', ''), ('Apply', 'The tool makes the cloud match the code.', '')],
        'Infrastructure as code in action', 'Servers from files.', 'IaC', 'Animation: write a template; review and plan; apply.', 's6anim')
T6 = vt(6, 'Infrastructure as code (IaC)', 'amber',
    '<b>Infrastructure as code</b> manages cloud resources — networks, servers, databases, permissions — through machine-readable definition files kept in version control, so environments are created, changed and reproduced by tools (declaratively) rather than by manual console clicks.',
    'A recipe card instead of “cook from memory”: anyone can make the same dish again, and changes to the recipe are written down and discussed.',
    'TiffinGo’s staging and production VPCs, databases and alarms come from the same Terraform code with different variables — a new Region took one day instead of three weeks.',
    'AWS CloudFormation and CDK; Azure Resource Manager templates and Bicep; Google Cloud Infrastructure Manager (Terraform); Terraform/OpenTofu, Pulumi; Ansible for configuration.', 'Google Cloud Deployment Manager reached end of support on 31 March 2026.', A6,
    'always for anything beyond a quick experiment.',
    'people still change things in the console afterwards — that causes drift.',
    'Creating cloud resources from written files instead of clicking, so it can be repeated and reviewed.',
    [('Write', 'Declarative template.'), ('Version', 'Commit to Git.'), ('Plan', 'Change set / what-if / plan.'), ('Apply', 'Create/update.'), ('Detect drift', 'Compare real vs code.')],
    [('declarative', 'describe the end state, the tool works out the steps'), ('drift', 'real resources differ from the code'), ('state file', 'Terraform’s record of what it manages')],
    table(['', 'CloudFormation', 'Bicep / ARM', 'Terraform'], [['Clouds', 'AWS', 'Azure', 'all'], ['Preview', 'change sets', 'what-if', 'plan'], ['State', 'managed by AWS', 'managed by Azure', 'state file (you store it)']], minw=480),
    ['Every environment', 'Disaster recovery rebuilds', 'Landing zones'],
    'IaC makes disaster recovery a script: teams that rebuilt Regions from code during incidents recovered far faster than teams with hand-built environments.',
    'Run IaC through the same pipeline as app code — plan on pull request, apply on merge — and block console changes in production.')

A7 = mk(['Desired state in Git', 'Agent compares', 'Cluster reconciled'], ['Git|manifests|reviewed PR', 'agent|Argo CD / Flux|watches Git', 'cluster|matches Git|drift corrected'], ['amber', 'blue', 'green'],
        ['the desired state of the system lives in a Git repository', 'an agent inside the platform continuously compares reality with Git', 'differences are corrected automatically; Git history is the audit log'],
        [('Declare', 'Desired state lives in Git, changed only by pull requests.', ''), ('Compare', 'An in-cluster agent continuously compares reality with Git.', ''), ('Reconcile', 'Drift is corrected; Git history is the audit trail.', '')],
        'GitOps in action', 'Git is the source of truth.', 'GitOps', 'Animation: desired state in Git; agent compares; cluster reconciled.', 's7anim')
T7 = vt(7, 'GitOps', 'amber',
    '<b>GitOps</b> is an operating model in which the desired state of systems (typically Kubernetes manifests or IaC) is stored declaratively in Git, and software agents continuously pull from Git and reconcile the running environment to match it, so every change is a reviewed commit and drift is corrected automatically.',
    'A thermostat set from a written schedule: whatever someone does to the window, the system keeps bringing the room back to what the schedule says.',
    'TiffinGo’s Kubernetes cluster runs Argo CD: changing the order service’s replica count is a pull request; when someone edits it by hand, Argo CD reverts it.',
    'Argo CD, Flux; Azure Arc/AKS GitOps (Flux) extension; GKE Config Sync; Amazon EKS with Argo CD capability/add-ons.', '', A7,
    'you run Kubernetes or declarative platforms and want auditable, self-healing configuration.',
    'secrets are committed in plain text — use sealed/external secrets.',
    'Keeping the whole system’s settings in Git, and letting a tool make the real system match it automatically.',
    [('Repo', 'Environment manifests in Git.'), ('PR', 'Every change reviewed.'), ('Agent', 'Pulls and applies.'), ('Reconcile', 'Fixes drift continuously.'), ('Rollback', 'git revert.')],
    [('reconcile', 'bring reality back to the desired state'), ('pull-based', 'the agent fetches changes instead of a pipeline pushing them'), ('manifest', 'a YAML file describing a Kubernetes resource')],
    table(['', 'GitOps (pull)', 'Pipeline deploy (push)'], [['Who applies changes', 'agent inside the cluster', 'CI/CD system from outside'], ['Drift', 'auto-corrected', 'until next deploy'], ['Credentials', 'stay inside cluster', 'pipeline needs cluster access']], minw=460),
    ['Kubernetes platforms', 'Multi-cluster fleets', 'Edge sites'],
    'The term GitOps was coined by Weaveworks in 2017; Argo CD and Flux are both graduated CNCF projects.',
    'Rollback becomes git revert — and the Git log becomes the change record auditors ask for.')

SUMMARY = table(['#', 'Practice', 'Area', 'Key idea', 'Cloud tools'], [
    ['1', 'Scrum', 'planning', 'sprints, roles, ceremonies', 'Azure Boards, Jira, GitHub Projects'], ['2', 'Kanban', 'planning', 'flow, WIP limits', 'Azure Boards, Jira, GitHub Projects'], ['3', 'CI', 'code → build', 'merge + test often', 'CodeBuild, GitHub Actions/Azure Pipelines, Cloud Build'],
    ['4', 'Continuous delivery', 'build → staging', 'always releasable, manual prod', 'CodePipeline, Azure Pipelines, Cloud Deploy'], ['5', 'Continuous deployment', '→ production', 'automatic prod', 'CodeDeploy + alarms, Cloud Deploy, Argo Rollouts'],
    ['6', 'IaC', 'infrastructure', 'resources from files', 'CloudFormation/CDK, Bicep, Terraform/Infra Manager'], ['7', 'GitOps', 'operations', 'Git = desired state', 'Argo CD, Flux, Config Sync']], minw=640)
CHECK = ('  <h3>Check yourself: which practice?</h3>\n' +
    qx('A. Every merge runs tests automatically in 5 minutes.', ['CI', 'Kanban', 'GitOps', 'Scrum'], 0, 'CI.') +
    qx('B. Production release after a manager clicks approve; everything else automatic.', ['Continuous delivery', 'Continuous deployment', 'Waterfall', 'Kanban'], 0, 'Manual gate.') +
    qx('C. A VPC defined in a Bicep file reviewed in a pull request.', ['IaC', 'Scrum', 'Canary', 'Kanban'], 0, 'Infrastructure as code.') +
    qx('D. Ops team limits “In progress” to 3 tickets.', ['Kanban', 'Scrum', 'CI', 'GitOps'], 0, 'WIP limits.'))

TYPES = ('  <p>Seven practices, each in the same pattern: definition, plain words, analogy, internal steps, animation, differences, where used, real-world example, TiffinGo scenario and an expert note.</p>\n'
         + challenge(['What is the only difference between continuous delivery and continuous deployment?', 'Why does halving work-in-progress shorten waiting time?', 'Who applies changes in GitOps — the pipeline or the cluster?'], 'types 4–5, 2 and 7') + MAP
         + jump(['Scrum', 'Kanban', 'CI', 'Delivery', 'Deployment', 'IaC', 'GitOps']) + T1 + T2 + T3 + T4 + T5 + T6 + T7
         + '\n  <h3 style="margin-top:34px">All seven side by side</h3>\n' + SUMMARY + '\n' + CHECK)

parts = wwu([
    ('Source repository', 'Where code and IaC live.', 'Single source of truth, reviews, history.', 'GitHub, GitLab, Azure Repos, Bitbucket.'),
    ('Pipeline definition', 'The pipeline as a file in the repo.', 'Versioned and reviewed like code.', 'buildspec.yml, azure-pipelines.yml / workflow YAML, cloudbuild.yaml.'),
    ('Build runner', 'Clean machine that runs the steps.', 'Repeatable builds, no “works on my laptop”.', 'CodeBuild, hosted agents/runners, Cloud Build workers.'),
    ('Artifact registry', 'Stores built packages and images.', 'Build once, deploy many.', 'ECR, ACR, Artifact Registry.'),
    ('Pipeline identity', 'How the pipeline logs in to the cloud.', 'No long-lived keys: use roles/OIDC.', 'IAM roles, workload identity federation.'),
    ('Approvals and policies', 'Gates before production.', 'Compliance and safety.', 'Manual approval, branch protection, policy checks.')])

DEEP = ('  <h3>The DORA four, and what “good” looks like</h3>\n' + table(['Metric', 'Elite teams (DORA research)', 'What improves it'], [['Deployment frequency', 'on demand, multiple per day', 'small batches, CI/CD'], ['Lead time for changes', 'less than a day', 'fast CI, automated delivery'], ['Change failure rate', 'low (around 5% or less)', 'tests, canaries, reviews'], ['Time to restore', 'less than an hour', 'monitoring, rollback, flags']], minw=560) +
    '\n  <h3>Pipeline security (DevSecOps)</h3>\n  <ul><li><b>No stored cloud keys:</b> pipelines assume IAM roles or use OIDC federation (GitHub → AWS/Azure/Google) for short-lived tokens.</li><li><b>Scan early:</b> dependency (SCA), code (SAST), container image and IaC scans in CI.</li><li><b>Protect main:</b> required reviews and passing checks before merge.</li><li><b>Supply chain:</b> pin action/image versions, sign artifacts, generate SBOMs (software bill of materials).</li></ul>\n'
    '  <h3>Test pyramid</h3>\n  <p>Many fast unit tests at the bottom, fewer integration tests in the middle, a handful of end-to-end tests at the top. Inverting it (mostly slow UI tests) makes pipelines slow and flaky.</p>\n'
    '  <h3>Tool notes for 2026</h3>\n  <p>AWS CodeBuild, CodePipeline and CodeDeploy remain the native AWS CI/CD services and integrate with GitHub/GitLab sources. Azure offers Azure Pipelines (Azure DevOps) and GitHub Actions, both with OIDC login to Azure. Google Cloud Build and Cloud Deploy cover CI and progressive delivery; Infrastructure Manager runs Terraform now that Deployment Manager is retired.</p>')

clouds = vendor_tabs('<p><b>AWS:</b> CodeBuild (CI), CodePipeline (orchestration), CodeDeploy (EC2/ECS/Lambda deployments), CodeArtifact and ECR (artifacts), CloudFormation and CDK (IaC); sources from GitHub, GitLab, Bitbucket or S3.</p>',
    '<p><b>Azure:</b> Azure DevOps (Boards, Repos, Pipelines, Artifacts, Test Plans) and GitHub (Actions, Projects, Advanced Security); Bicep/ARM (IaC); GitOps with Flux on AKS/Arc; OIDC federated credentials for pipelines.</p>',
    '<p><b>Google Cloud:</b> Cloud Build (CI), Cloud Deploy (CD to GKE/Cloud Run), Artifact Registry, Infrastructure Manager (Terraform), Config Sync (GitOps); developer tools such as Cloud Workstations; Workload Identity Federation for GitHub.</p>') + \
    cloud3([['CI', 'CodeBuild', 'Azure Pipelines / GitHub Actions', 'Cloud Build'], ['CD orchestration', 'CodePipeline + CodeDeploy', 'Azure Pipelines releases / environments', 'Cloud Deploy'], ['Boards', 'third-party (Jira)', 'Azure Boards / GitHub Projects', 'third-party'], ['IaC', 'CloudFormation, CDK', 'Bicep, ARM', 'Infrastructure Manager (Terraform)'], ['GitOps', 'Argo CD on EKS', 'Flux (AKS/Arc)', 'Config Sync']])

# ------------------------------------------------------------------ practical
APP = '''mkdir menu-ci && cd menu-ci
cat > app.py <<'EOF'
from flask import Flask
app = Flask(__name__)
def price(thalis):          # Rs 150 each, 10% off for 5 or more
    total = 150 * thalis
    return total * 0.9 if thalis >= 5 else total
@app.route("/")
def home():
    return f"<h1>TiffinGo menu</h1><p>5 thalis: Rs {price(5):.0f}</p>"
@app.route("/health")
def health():
    return "ok"
EOF
cat > test_app.py <<'EOF'
from app import app, price
def test_price_discount():
    assert price(5) == 675
def test_home():
    r = app.test_client().get("/")
    assert r.status_code == 200 and b"TiffinGo" in r.data
EOF
printf "flask\\ngunicorn\\n" > requirements.txt
pip install -q flask pytest && python3 -m pytest -q'''

MOCKQ.extend([
 (mock('aws', ['CloudShell', 'ap-south-1'], ['Actions', 'Tabs'], 'Tabs',
       [('$ python3 -m pytest -q', '2 passed'), ('after breaking the discount', '1 failed · assert 600.0 == 675')], 'New tab'),
  mock('az', ['Cloud Shell', 'Bash'], ['Bash', 'PowerShell'], 'Bash',
       [('$ python3 -m pytest -q', '2 passed'), ('after breaking the discount', '1 failed')], 'Restart'),
  mock('gcp', ['Cloud Shell', 'Terminal'], ['Editor', 'Terminal'], 'Terminal',
       [('$ python3 -m pytest -q', '2 passed'), ('after breaking the discount', '1 failed')], 'Open editor')),
 (mock('aws', ['CodeBuild', 'Build projects', 'Create build project'], ['Build projects', 'Build history', 'Report groups'], 'Build projects',
       [('Project name', 'tiffingo-menu-ci'), ('Source provider', '▾ Amazon S3 (or GitHub)'), ('Environment image', 'aws/codebuild/standard:7.0'), ('Buildspec', '[x] Use a buildspec file')], 'Create build project'),
  mock('az', ['GitHub', 'your repo', 'Actions'], ['Code', 'Issues', 'Pull requests', 'Actions', 'Settings'], 'Actions',
       [('Workflow', '.github/workflows/ci.yml'), ('Run', '#1 · push to main · test ✔')], 'Re-run jobs'),
  mock('gcp', ['Cloud Build', 'History'], ['Dashboard', 'History', 'Triggers', 'Repositories'], 'History',
       [('Build', 'Source: local upload · Status: ✔ Success'), ('Step 0', 'python:3.12 · pytest · 2 passed')], 'Rebuild')),
 (mock('aws', ['CodeBuild', 'tiffingo-menu-ci', 'Build history'], ['Build details', 'Phase details', 'Build logs'], 'Phase details',
       [('INSTALL', 'Succeeded'), ('BUILD (pytest)', 'Succeeded'), ('POST_BUILD (deploy to Lambda)', 'Succeeded')], 'Retry build'),
  mock('az', ['Microsoft Entra ID', 'App registrations', 'gh-deployer', 'Certificates & secrets'], ['Overview', 'Certificates & secrets', 'API permissions'], 'Certificates & secrets',
       [('Federated credentials', 'GitHub Actions · repo:you/menu-ci · branch main'), ('Client secrets', 'none (OIDC — no secret stored)')], 'Add credential'),
  mock('gcp', ['Cloud Build', 'History', 'Build details'], ['Steps', 'Logs', 'Artifacts'], 'Steps',
       [('0 · test', '✔'), ('1 · docker build', '✔'), ('2 · docker push', '✔'), ('3 · gcloud run deploy', '✔ serving 100%')], 'Rebuild')),
 (mock('aws', ['CloudFormation', 'Stacks', 'tiffingo-ci-bucket'], ['Stacks', 'StackSets', 'Exports'], 'Stacks',
       [('Status', 'CREATE_COMPLETE'), ('Change sets', 'preview before update'), ('Drift', 'Detect stack drift')], 'Update'),
  mock('az', ['Home', 'Resource groups', 'rg-devops', 'Deployments'], ['Overview', 'Deployments', 'Activity log'], 'Deployments',
       [('main (Bicep)', 'Succeeded'), ('What-if', 'shows creates / modifies / deletes before deploy')], 'Redeploy'),
  mock('gcp', ['Cloud Shell', 'Terminal'], ['Editor', 'Terminal'], 'Terminal',
       [('$ terraform plan', 'Plan: 1 to add, 0 to change, 0 to destroy'), ('$ terraform apply', 'Apply complete! Resources: 1 added')], 'Run')),
])

BUILDSPEC = '''cat > buildspec.yml <<'EOF'
version: 0.2
phases:
  install:
    runtime-versions:
      python: 3.12
    commands:
      - pip install -r requirements.txt pytest
  build:
    commands:
      - python -m pytest -q
EOF'''

STEP1 = ('1 · Write a tiny app with tests (and watch a test fail)', tri(
    (['Open [[CloudShell]] (the &gt;_ icon in the console). Paste the commands on the right.', 'Then break the rule on purpose: change <code>0.9</code> to <code>0.8</code> in app.py and run <code>python3 -m pytest -q</code> again.'],
     APP,
     '<code>2 passed</code>; after your change, <code>1 failed</code> with <code>assert 600.0 == 675</code> — exactly what CI will catch for you. Change it back to 0.9.'),
    (['Open [[Cloud Shell]] (Bash) in the portal. Paste the commands on the right.', 'Break the discount on purpose and run the tests again.'],
     APP,
     '<code>2 passed</code>, then <code>1 failed</code> after the change. Change it back.'),
    (['Open [[Cloud Shell]] (top bar &gt;_). Paste the commands on the right.', 'Break the discount on purpose and run the tests again.'],
     APP,
     '<code>2 passed</code>, then <code>1 failed</code> after the change. Change it back.')),
    'Tests are what make automation safe: a pipeline is only as good as the checks inside it.')

STEP2 = ('2 · Run CI in the cloud’s build service', tri(
    (['[[CodeBuild]] → [[Create build project]]: name <code>tiffingo-menu-ci</code>, source [[Amazon S3]] (or connect [[GitHub]]), image <code>aws/codebuild/standard:7.0</code>, [[Use a buildspec file]], new service role → [[Create]] → [[Start build]].'],
     BUILDSPEC + "\nB=tiffingo-ci-$RANDOM; aws s3 mb s3://$B\nzip -qr src.zip app.py test_app.py requirements.txt buildspec.yml && aws s3 cp src.zip s3://$B/\nROLE=$(aws iam create-role --role-name tiffingo-cb-role --assume-role-policy-document '{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"codebuild.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}' --query Role.Arn --output text)\naws iam put-role-policy --role-name tiffingo-cb-role --policy-name ci --policy-document \"{\\\"Version\\\":\\\"2012-10-17\\\",\\\"Statement\\\":[{\\\"Effect\\\":\\\"Allow\\\",\\\"Action\\\":[\\\"logs:*\\\",\\\"s3:GetObject\\\",\\\"s3:GetObjectVersion\\\"],\\\"Resource\\\":\\\"*\\\"}]}\"\nsleep 10\naws codebuild create-project --name tiffingo-menu-ci --source type=S3,location=$B/src.zip --artifacts type=NO_ARTIFACTS \\\n  --environment type=LINUX_CONTAINER,image=aws/codebuild/standard:7.0,computeType=BUILD_GENERAL1_SMALL --service-role $ROLE\nID=$(aws codebuild start-build --project-name tiffingo-menu-ci --query build.id --output text)\nsleep 90; aws codebuild batch-get-builds --ids $ID --query 'builds[0].phases[].[phaseType,phaseStatus]' --output text",
     'phases ending with <code>BUILD SUCCEEDED</code>. Upload a broken app.py and start another build: the BUILD phase shows <code>FAILED</code> and the log shows the failing assert. (CodeBuild free tier: 100 build minutes a month on small instances.)'),
    (['Azure’s pipelines run from a Git repo: create a repo on [[GitHub]] (or Azure Repos), push the folder, add the workflow file on the right.', '[[Actions]] tab → watch the run. (Azure Pipelines works the same way with <code>azure-pipelines.yml</code>; new Azure DevOps organisations may need to request free hosted parallelism first.)'],
     "mkdir -p .github/workflows\ncat > .github/workflows/ci.yml <<'EOF'\nname: ci\non: [push, pull_request]\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n      - uses: actions/setup-python@v5\n        with: { python-version: '3.12' }\n      - run: pip install -r requirements.txt pytest && python -m pytest -q\nEOF\ngit init -b main && git add . && git commit -qm 'menu with tests'\ngit remote add origin https://github.com/YOUR-USER/menu-ci.git && git push -u origin main",
     'a green ✔ for the <code>test</code> job in the Actions tab; push a broken discount and it turns red ✘ within about a minute. GitHub Actions is free for public repos and has a monthly free allowance for private ones.'),
    (['[[Cloud Build]] → [[History]] shows each build. Run the CLI on the right: it uploads the folder and runs the steps in <code>cloudbuild.yaml</code>.'],
     "cat > cloudbuild.yaml <<'EOF'\nsteps:\n- id: test\n  name: python:3.12\n  entrypoint: bash\n  args: ['-c', 'pip install -q -r requirements.txt pytest && python -m pytest -q']\nEOF\ngcloud services enable cloudbuild.googleapis.com\ngcloud builds submit --config cloudbuild.yaml --region asia-south1 .",
     'the build log ending with <code>2 passed</code> and <code>STATUS: SUCCESS</code>; with a broken discount, <code>STATUS: FAILURE</code>. Cloud Build has a monthly free tier of build minutes.')),
    'This is continuous integration: every change is tested on a clean machine, not on someone’s laptop.')

STEP3 = ('3 · Add continuous deployment (only when tests pass)', tri(
    (['Create the Lambda function <code>tiffingo-menu</code> as in Lesson 8.2 step 1 if you deleted it.', 'Add a <code>post_build</code> phase that zips and updates the function only if the build phase succeeded; give the CodeBuild role <code>lambda:UpdateFunctionCode</code>.'],
     "cat >> buildspec.yml <<'EOF'\n  post_build:\n    commands:\n      - '[ \"$CODEBUILD_BUILD_SUCCEEDING\" = \"1\" ] || exit 1'\n      - mkdir -p pkg && cp lambda_function.py pkg/ && cd pkg && zip -q ../fn.zip lambda_function.py && cd ..\n      - aws lambda update-function-code --function-name tiffingo-menu --zip-file fileb://fn.zip --publish\nEOF\naws iam put-role-policy --role-name tiffingo-cb-role --policy-name deploy --policy-document '{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Action\":\"lambda:UpdateFunctionCode\",\"Resource\":\"*\"}]}'\ncp ../menu/lambda_function.py . 2>/dev/null || echo 'copy lambda_function.py from Lesson 8.2'\nzip -qr src.zip app.py test_app.py requirements.txt buildspec.yml lambda_function.py && aws s3 cp src.zip s3://$B/\nID=$(aws codebuild start-build --project-name tiffingo-menu-ci --query build.id --output text)\nsleep 100; aws codebuild batch-get-builds --ids $ID --query 'builds[0].phases[].[phaseType,phaseStatus]' --output text",
     '<code>POST_BUILD SUCCEEDED</code> and a new Lambda version published. With a failing test, BUILD fails and POST_BUILD never deploys. In real projects, CodePipeline chains source → CodeBuild → deploy with an optional approval stage.'),
    (['[[Microsoft Entra ID]] → [[App registrations]] → [[New registration]] <code>gh-deployer</code> → [[Certificates &amp; secrets]] → [[Federated credentials]] → GitHub Actions, your repo, branch <code>main</code>.', 'Give it [[Contributor]] on <code>rg-devops</code>; add repo secrets <code>AZURE_CLIENT_ID</code>, <code>AZURE_TENANT_ID</code>, <code>AZURE_SUBSCRIPTION_ID</code>; append the deploy job.'],
     "az group create -n rg-devops -l centralindia\nAPP=tiffingo-ci-$RANDOM; az appservice plan create -g rg-devops -n plan-ci --is-linux --sku F1\naz webapp create -g rg-devops -p plan-ci -n $APP --runtime 'PYTHON:3.12'\naz webapp config appsettings set -g rg-devops -n $APP --settings SCM_DO_BUILD_DURING_DEPLOYMENT=true\nCID=$(az ad app create --display-name gh-deployer --query appId -o tsv); az ad sp create --id $CID\naz ad app federated-credential create --id $CID --parameters '{\"name\":\"gh-main\",\"issuer\":\"https://token.actions.githubusercontent.com\",\"subject\":\"repo:YOUR-USER/menu-ci:ref:refs/heads/main\",\"audiences\":[\"api://AzureADTokenExchange\"]}'\naz role assignment create --assignee $CID --role Contributor --scope $(az group show -n rg-devops --query id -o tsv)\ncat >> .github/workflows/ci.yml <<EOF\n  deploy:\n    needs: test\n    if: github.ref == 'refs/heads/main'\n    runs-on: ubuntu-latest\n    permissions: { id-token: write, contents: read }\n    steps:\n      - uses: actions/checkout@v4\n      - uses: azure/login@v2\n        with:\n          client-id: \\${{ secrets.AZURE_CLIENT_ID }}\n          tenant-id: \\${{ secrets.AZURE_TENANT_ID }}\n          subscription-id: \\${{ secrets.AZURE_SUBSCRIPTION_ID }}\n      - uses: azure/webapps-deploy@v3\n        with: { app-name: $APP }\nEOF\ngit add . && git commit -qm 'deploy job' && git push",
     'in Actions, <code>test</code> ✔ then <code>deploy</code> ✔; <code>https://APP.azurewebsites.net/</code> shows “5 thalis: Rs 675”. No password is stored anywhere — GitHub gets a short-lived token through OIDC.'),
    (['Grant the Cloud Build service account permission to deploy (the CLI on the right), create an Artifact Registry repo, and add build, push and deploy steps.', '[[Cloud Run]] then shows a new revision created by Cloud Build.'],
     "P=$(gcloud config get-value project); N=$(gcloud projects describe $P --format='value(projectNumber)')\nSA=$N-compute@developer.gserviceaccount.com\nfor r in run.admin iam.serviceAccountUser artifactregistry.writer logging.logWriter; do gcloud projects add-iam-policy-binding $P --member=serviceAccount:$SA --role=roles/$r --condition=None -q >/dev/null; done\ngcloud artifacts repositories create menu --repository-format=docker --location=asia-south1\nprintf 'FROM python:3.12-slim\\nWORKDIR /app\\nCOPY . .\\nRUN pip install -r requirements.txt\\nCMD exec gunicorn -b :$PORT app:app\\n' > Dockerfile\ncat >> cloudbuild.yaml <<'EOF'\n- id: build\n  name: gcr.io/cloud-builders/docker\n  args: ['build', '-t', 'asia-south1-docker.pkg.dev/$PROJECT_ID/menu/app:$BUILD_ID', '.']\n- id: push\n  name: gcr.io/cloud-builders/docker\n  args: ['push', 'asia-south1-docker.pkg.dev/$PROJECT_ID/menu/app:$BUILD_ID']\n- id: deploy\n  name: gcr.io/google.com/cloudsdktool/cloud-sdk\n  entrypoint: gcloud\n  args: ['run', 'deploy', 'tiffingo-ci', '--image', 'asia-south1-docker.pkg.dev/$PROJECT_ID/menu/app:$BUILD_ID', '--region', 'asia-south1', '--allow-unauthenticated']\nEOF\ngcloud builds submit --config cloudbuild.yaml --region asia-south1 .",
     'four steps succeed (test, build, push, deploy) and a Cloud Run URL serving “5 thalis: Rs 675”. A failing test stops at step <code>test</code> — nothing is deployed. Projects whose Cloud Build uses a different default service account: grant the same roles to that account.')),
    'Tests are the gate: red never reaches production. Add a manual approval stage and this becomes continuous delivery instead of continuous deployment.')

STEP4 = ('4 · Create infrastructure from code (IaC)', tri(
    (['[[CloudFormation]] → [[Create stack]] → upload the template on the right → [[Next]] → [[Submit]].', 'Change the template (e.g. add a tag) and [[Update]] → review the [[change set]] before executing.'],
     "cat > bucket.yaml <<'EOF'\nAWSTemplateFormatVersion: '2010-09-09'\nResources:\n  Reports:\n    Type: AWS::S3::Bucket\n    Properties:\n      VersioningConfiguration: { Status: Enabled }\n      Tags: [ { Key: app, Value: tiffingo } ]\nOutputs:\n  BucketName: { Value: !Ref Reports }\nEOF\naws cloudformation deploy --stack-name tiffingo-ci-bucket --template-file bucket.yaml\naws cloudformation describe-stacks --stack-name tiffingo-ci-bucket --query 'Stacks[0].[StackStatus,Outputs[0].OutputValue]' --output text",
     '<code>CREATE_COMPLETE</code> and the generated bucket name. Run deploy again with no change: “No changes to deploy” — the template is the truth.'),
    (['[[Deploy a custom template]] → [[Build your own template]] or use the CLI with the Bicep file on the right.', 'Run <code>what-if</code> first to preview creates and changes.'],
     "cat > main.bicep <<'EOF'\nparam location string = resourceGroup().location\nresource sa 'Microsoft.Storage/storageAccounts@2023-05-01' = {\n  name: 'tgreports${uniqueString(resourceGroup().id)}'\n  location: location\n  sku: { name: 'Standard_LRS' }\n  kind: 'StorageV2'\n  tags: { app: 'tiffingo' }\n}\noutput accountName string = sa.name\nEOF\naz deployment group what-if -g rg-devops --template-file main.bicep\naz deployment group create -g rg-devops --template-file main.bicep --query properties.outputs.accountName.value -o tsv",
     'what-if lists “+ Create” for the storage account; then the account name. Re-running what-if shows no changes.'),
    (['Cloud Shell has Terraform installed. Write the file on the right, then <code>terraform init</code>, <code>plan</code>, <code>apply</code>.', '(Infrastructure Manager runs the same Terraform as a managed service; Deployment Manager is retired.)'],
     "mkdir iac && cd iac\ncat > main.tf <<EOF\nprovider \"google\" {\n  project = \"$(gcloud config get-value project)\"\n  region  = \"asia-south1\"\n}\nresource \"google_storage_bucket\" \"reports\" {\n  name     = \"tiffingo-reports-$RANDOM\"\n  location = \"asia-south1\"\n  labels   = { app = \"tiffingo\" }\n  versioning { enabled = true }\n}\nEOF\nterraform init -input=false >/dev/null && terraform plan -input=false | tail -1\nterraform apply -auto-approve -input=false | tail -1",
     '<code>Plan: 1 to add, 0 to change, 0 to destroy.</code> then <code>Apply complete! Resources: 1 added</code>. Run plan again: “No changes”.')),
    'Commit these files next to the app and run plan in the pipeline — infrastructure changes get the same review and history as code.')

prac = practical(OWN_INTRO + ' You build the DevOps loop yourself: tests, a CI build in the cloud, automatic deployment only when tests pass, and infrastructure from code. Everything fits free tiers; the Azure path also needs a free GitHub account.', [SETUP_STEP, STEP1, STEP2, STEP3, STEP4],
    cleanup='<b>AWS:</b> <code>aws codebuild delete-project --name tiffingo-menu-ci</code>; <code>aws cloudformation delete-stack --stack-name tiffingo-ci-bucket</code> (empty the versioned bucket first if you uploaded files); <code>aws s3 rb s3://$B --force</code>; delete the role policies and <code>tiffingo-cb-role</code>; delete the Lambda function if you recreated it. '
            '<b>Azure:</b> <code>az group delete -n rg-devops --yes --no-wait</code>; <code>az ad app delete --id $CID</code>; delete the GitHub repo or its secrets. '
            '<b>Google Cloud:</b> <code>terraform destroy -auto-approve</code> (in iac/); <code>gcloud run services delete tiffingo-ci --region asia-south1 --quiet</code>; <code>gcloud artifacts repositories delete menu --location asia-south1 --quiet</code>; optionally remove the IAM bindings you added.')

mist = mistakes([
    ['Calling a CI server “DevOps”.', 'Tool-first thinking.', 'Change ownership and hand-offs (CALMS); tools support it.'],
    ['Long-lived cloud keys in pipeline secrets.', 'Easy setup.', 'IAM roles / OIDC federation — short-lived tokens.'],
    ['Slow, flaky pipelines.', 'Too many end-to-end tests.', 'Test pyramid; keep CI under 10 minutes.'],
    ['Console changes after IaC.', 'Quick fixes.', 'Change only through code; detect drift.'],
    ['Big-bang releases every month.', 'Fear of releasing.', 'Small batches, canary, feature flags.'],
    ['Agile as meetings only.', 'Ceremonies without delivery.', 'Ship working, deployed increments every sprint.']])

cert = table(['Exam / syllabus', 'What is asked'], [['C-DAC PGCP-BDA', 'DevOps on the cloud: lifecycle, Agile, CI/CD.'], ['AWS CLF-C02', 'CodeBuild, CodePipeline, CodeDeploy, CloudFormation; IaC and automation benefits.'], ['AZ-900', 'Azure DevOps, GitHub, ARM/Bicep; infrastructure as code.'], ['Google Cloud Digital Leader', 'DevOps and SRE ideas, Cloud Build, CI/CD, modernisation.']], minw=560) + \
    qx('1. Which AWS service compiles code and runs tests?', ['CodeBuild', 'CodeDeploy', 'CloudTrail', 'Config'], 0, 'CodeBuild.') + \
    qx('2. Which AWS service orchestrates source, build, test and deploy stages?', ['CodePipeline', 'CodeArtifact', 'Inspector', 'Athena'], 0, 'CodePipeline.') + \
    qx('3. Defining Azure resources in Bicep files is an example of…', ['infrastructure as code', 'Kanban', 'canary release', 'GitOps only'], 0, 'IaC.') + \
    qx('4. Every passing change goes to production automatically. This is…', ['continuous deployment', 'continuous delivery', 'continuous integration', 'waterfall'], 0, 'No manual gate.') + \
    qx('5. Which Agile method limits work in progress on a board?', ['Kanban', 'Scrum', 'Waterfall', 'Spiral'], 0, 'Kanban.') + \
    qx('6. Safest way for a pipeline to access the cloud?', ['root keys in secrets', 'short-lived credentials via roles/OIDC', 'password in YAML', 'public bucket'], 1, 'Federation.')

proj = miniproject('Mini project: from 12 days to 1 hour',
    'Design and build TiffinGo’s delivery system.',
    ['<b>Value stream:</b> map today’s 12-day path and mark wait vs work time.',
     '<b>Agile:</b> choose Scrum or Kanban per team (app vs platform) and justify.',
     '<b>Pipeline:</b> draw stages with tools in your cloud: source → CI → artifact → staging → gate → canary prod.',
     '<b>Build it:</b> complete practical steps 1–4 and add one more test.',
     '<b>Security:</b> show how the pipeline authenticates without stored keys.',
     '<b>Measure:</b> define how you will track the four DORA metrics.'],
    'A pipeline diagram, a working CI/CD run with screenshots, and a DORA tracking plan.', '8.1 + 8.2 + 8.3.')

assemble_v2(HERE, story_h2='Twelve days for a one-line fix', hook_html=hk,
    narration='At TiffinGo, developers, testers and operations worked in separate teams with separate queues. A one-line price correction needed 12 days to reach customers — almost all of it spent waiting.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='DevOps on the cloud: lifecycle, Agile and CI/CD',
    formal='<b>DevOps</b> is a set of cultural practices and tools that unify software development and IT operations so one team owns the full lifecycle — plan, code, build, test, release, deploy, operate, monitor — delivering small changes frequently and reliably. It builds on <b>Agile</b> methods (iterative, incremental delivery such as Scrum and Kanban) and is implemented through <b>CI/CD</b> pipelines (continuous integration, continuous delivery/deployment) and <b>infrastructure as code</b>, which cloud providers offer as managed services.',
    simple='Developers and operations working as one team, shipping small changes often, with an automatic pipeline that tests and deploys every change.',
    interview=['“DevOps is culture plus automation across the lifecycle. CI merges and tests every change; continuous delivery keeps it always releasable with a manual production gate; continuous deployment removes that gate.”', '“On AWS I use CodeBuild, CodePipeline, CodeDeploy and CloudFormation; on Azure, GitHub Actions or Azure Pipelines with Bicep; on Google Cloud, Cloud Build, Cloud Deploy and Terraform via Infrastructure Manager — with OIDC instead of stored keys.”'],
    terms_rows=[('DevOps', 'Dev + Ops as one team and lifecycle.'), ('Agile', 'Iterative, incremental delivery.'), ('Scrum / Kanban', 'Sprints / flow with WIP limits.'), ('CI', 'Merge + test often.'), ('Continuous delivery', 'Always releasable, manual prod.'), ('Continuous deployment', 'Automatic prod.'), ('IaC', 'Infrastructure from code.'), ('GitOps', 'Git as desired state.')],
    exam='Know AWS developer tools (CodeBuild, CodePipeline, CodeDeploy), IaC (CloudFormation, Bicep/ARM), the delivery vs deployment difference, and Agile basics.',
    picture_h2='The DevOps lifecycle and what it changes', picture_html=picture,
    after_picture=[('types', 'Types, one by one', 'Seven DevOps practices, one by one', TYPES)],
    how_h2='One commit through a CI/CD pipeline', how_intro='The same fix that took 12 days, now through a pipeline.', how_anim=PIPE,
    parts_h2='Six parts of every cloud pipeline', parts_html=parts, lv='',
    myth_rows=[('DevOps is a job title or a tool.', 'It is a way of working; tools support it.', 'CALMS.'), ('Releasing often is riskier.', 'Small frequent changes fail less and recover faster.', 'DORA.'), ('Continuous delivery means auto-deploy to prod.', 'That is continuous deployment.', 'Types 4–5.')],
    extra_secs=[('deep', 'Deep dive', 'DORA, pipeline security, test pyramid, 2026 tool notes', DEEP)],
    clouds_html=clouds, practical_html=prac, mistakes_html=mist, cert_html=cert, project_html=proj,
    can_now=['Explain the DevOps lifecycle and CALMS.', 'Compare Scrum and Kanban, and CI, continuous delivery and continuous deployment.', 'Trace one commit through a CI/CD pipeline.', 'Build CI, test-gated deployment and IaC on AWS, Azure or Google Cloud.', 'Measure delivery with DORA metrics.'],
    next_html='Module 9 — <a href="../../09-cloud-security/01-shared-responsibility-model/">9.1 Shared responsibility model</a>.',
    pre='<b>Before you start:</b> 8.1 (monitoring) and 8.2 (deployment strategies).')
