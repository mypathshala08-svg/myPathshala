import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
def cap(frames, steps, title, intro, panel, aria, hid, delay=5500):
    return anim_one('Animated', title, intro, panel, aria, cap_frames(frames, steps), [s[0] + '.' for s in steps], delay=delay, hid=hid)


hk = hook('Friday 8:40 pm. Customers tweet that TiffinGo orders are failing. The team finds out from Twitter, 25 minutes late, and spends another hour asking “what changed?”. What should have told them first?',
    'Monitoring. A cloud that runs by itself still needs someone — or something — watching. This lesson covers the seven tools of cloud operations: <b>metrics</b>, <b>logs</b>, <b>traces</b>, <b>alarms</b>, <b>dashboards</b>, <b>audit trails</b> and <b>service health</b>. You will watch one alarm fire step by step, learn what to watch (the four golden signals), and on <b>your own</b> account set up an email channel, write and search logs, build an alarm that really fires, and find out who changed what.',
    ['Metrics tell you <i>that</i> something is wrong; logs and traces tell you <i>why</i>.', 'The difference between monitoring the cloud and the cloud monitoring itself.', 'Why “alert on everything” is as bad as no alerts.'])

def story_scene():
    o = t(180, 12, 'Who noticed first?', 9, 'ink', bold=True)
    o += box(8, 28, 160, 74, 'red', rx=8) + t(88, 48, 'Without monitoring', 8.4, 'ink', bold=True) + t(88, 64, 'customers notice', 7, 'ink2') + t(88, 78, 'team guesses', 7, 'ink2') + t(88, 92, '85 minutes lost', 7.4, 'ink', bold=True)
    o += box(192, 28, 160, 74, 'green', rx=8) + t(272, 48, 'With monitoring', 8.4, 'ink', bold=True) + t(272, 64, 'alarm pages on-call', 7, 'ink2') + t(272, 78, 'audit shows the change', 7, 'ink2') + t(272, 92, 'fixed in 10 minutes', 7.4, 'ink', bold=True)
    o += t(180, 122, 'Same failure, different detection', 7.6, 'ink', bold=True)
    return o
scene_svg = scene('Left: without monitoring, customers notice first and 85 minutes are lost. Right: with monitoring, an alarm pages the on-call engineer and audit logs show the change; fixed in 10 minutes.', story_scene(), 'Find out <tspan font-weight="700" class="s-acc">before your customers do</tspan>.', h=132)
dialogue = '''R> Sir, nothing in the AWS console looked red. Why didn’t AWS warn us?
A> AWS watches its own hardware. Our app, our error rate, our database — watching those is our job. Shared responsibility again.
K> We had CPU graphs…
A> CPU was fine. The payment API was returning errors. We had no alarm on errors, no logs searched, and nobody checked who changed the config at 8:30.
R> So what do we set up?
A> Seven things. Let’s go one by one, then build them on our accounts.'''

# ------------------------------------------------------------------ picture
def pillfig():
    o = t(320, 16, 'The observability loop: collect → see → act → learn', 11, 'ink', bold=True)
    src = [('App', 'app'), ('VMs / containers', 'server'), ('Database', 'db'), ('Cloud APIs', 'cloud')]
    for i, (a, _) in enumerate(src):
        o += box(10, 30 + i * 40, 110, 32, 'card', rx=6) + t(65, 50 + i * 40, a, 7.6, 'ink', bold=True)
    o += arrow(122, 96, 150, 96)
    col = [('Metrics', 'numbers over time', 'blue'), ('Logs', 'event records', 'amber'), ('Traces', 'one request’s path', 'violet'), ('Audit trail', 'who did what', 'red')]
    for i, (a, b, tn) in enumerate(col):
        o += box(152, 30 + i * 40, 150, 32, tn, rx=6) + t(227, 44 + i * 40, a, 7.8, 'ink', bold=True) + t(227, 56 + i * 40, b, 6.6, 'ink2')
    o += arrow(304, 96, 332, 96)
    act = [('Dashboards', 'see', 'green'), ('Alarms', 'notify / auto-fix', 'amber'), ('Insights', 'search, correlate', 'blue')]
    for i, (a, b, tn) in enumerate(act):
        o += box(334, 36 + i * 44, 130, 36, tn, rx=6) + t(399, 52 + i * 44, a, 7.8, 'ink', bold=True) + t(399, 64 + i * 44, b, 6.6, 'ink2')
    o += arrow(466, 96, 494, 96)
    o += box(496, 60, 130, 72, 'violet', rx=8) + t(561, 84, 'People + automation', 7.8, 'ink', bold=True) + t(561, 100, 'on-call, runbooks,', 6.8, 'ink2') + t(561, 114, 'auto scaling, fixes', 6.8, 'ink2')
    o += t(320, 196, 'Service health (the provider’s own status) sits beside this loop: is it us, or is it them?', 7.4, 'ink2')
    return o
PILL = bigfig('Sources (app, VMs, database, cloud APIs) feed metrics, logs, traces and audit trail; these feed dashboards, alarms and insights; which drive people and automation.', pillfig(), h=206)

def goldfig():
    o = t(320, 16, 'What to watch: the four golden signals', 11, 'ink', bold=True)
    G = [('Latency', 'how long requests take', 'p99 checkout < 800 ms', 'blue'), ('Traffic', 'how much demand', 'orders per minute', 'green'), ('Errors', 'how many fail', '5xx rate < 1%', 'red'), ('Saturation', 'how full the system is', 'DB connections 80%', 'amber')]
    for i, (a, b, c, tn) in enumerate(G):
        x = 14 + i * 154
        o += box(x, 34, 146, 92, tn, rx=8) + t(x + 73, 58, a, 9, 'ink', bold=True) + t(x + 73, 78, b, 7, 'ink2') + t(x + 73, 104, c, 7, 'ink')
    o += t(320, 148, 'From Google’s SRE book. Watch these per service before CPU and memory.', 7.4, 'ink2')
    return o
GOLD = bigfig('Four boxes: latency, traffic, errors, saturation with TiffinGo examples.', goldfig(), h=158)

picture = ('  <p>Operations is a loop: collect signals, see them, act on them, and learn. Every cloud provides the same building blocks:</p>\n' + PILL +
           '\n  <p>And a short list of what is worth watching:</p>\n' + GOLD +
           '\n  <h3>Who monitors what (shared responsibility)</h3>\n' + table(['Layer', 'Provider watches', 'You watch'], [
               ['Data centre, hardware, hypervisor', 'yes — and posts it in service health', 'read service health'], ['Managed service internals (RDS engine, S3)', 'yes', 'its metrics, errors and limits for your use'],
               ['Your VMs’ OS, disks, memory', 'only host-level (CPU, network)', 'agent metrics: memory, disk space, processes'], ['Your application', 'no', 'everything: golden signals, logs, traces'], ['Changes to your account', 'records them (audit logs)', 'who changed what, and alerts on risky changes']], minw=620))

# ------------------------------------------------------------------ how: an alarm firing
RN = {'app': (4, 54, 50, 50, 'app', 'Payment API', 'errors ↑'), 'met': (66, 4, 62, 46, 'chart', 'Metric', '5xx count'), 'al': (66, 104, 62, 46, 'meter', 'Alarm', '> 20 in 5 min'),
      'sns': (142, 54, 60, 50, 'gear', 'Notify', 'SNS / action group'), 'on': (216, 4, 62, 46, 'phone', 'On-call', 'email / SMS / chat'), 'log': (216, 104, 62, 46, 'disk', 'Logs + audit', 'why?'), 'fix': (292, 54, 64, 50, 'shield', 'Fix', 'rollback')}
RS = [dict(on=['app', 'met'], hot='met', move=(54, 79, 72, 30, 'datapoint'), head='Step 1 · The service emits a metric', text='Every minute the load balancer publishes how many 5xx errors the payment API', text2='returned. 8:31 pm: 3. 8:32 pm: 41.', svc='CloudWatch metrics · Azure Monitor metrics · Cloud Monitoring'),
      dict(on=['met', 'al'], hot='al', move=(97, 50, 97, 104, 'evaluate'), head='Step 2 · The alarm evaluates a rule', text='Rule: “5xx errors > 20 for 2 of the last 3 minutes”. Requiring 2 of 3 avoids', text2='paging people for a single blip.', svc='States: OK → ALARM (→ INSUFFICIENT_DATA if no data)'),
      dict(on=['al', 'sns'], hot='sns', move=(128, 127, 150, 90, 'ALARM'), head='Step 3 · State change triggers actions', text='OK → ALARM sends a message to a notification topic / action group, and can also', text2='run automation (scale out, restart, open a ticket).', svc='SNS topic · Azure action group · notification channel'),
      dict(on=['sns', 'on'], hot='on', move=(202, 66, 226, 30, 'page'), head='Step 4 · A human is told within a minute', text='Kabir (on call) gets an email/SMS/chat message with the alarm name, value and a', text2='link to the dashboard — at 8:34, before customers start tweeting.', svc='Route to people via chat, paging tools (PagerDuty, Opsgenie)'),
      dict(on=['on', 'log'], hot='log', move=(247, 50, 247, 104, 'search'), head='Step 5 · Logs and audit say why', text='Log search shows “payment key invalid”; the audit trail shows a config change at', text2='8:30 by a deploy pipeline. Root cause found in minutes, not hours.', svc='CloudWatch Logs Insights + CloudTrail · Log Analytics · Logs Explorer + Audit Logs'),
      dict(on=list(RN), hot='fix', move=(278, 127, 298, 90, 'rollback'), head='Step 6 · Fix, recover, learn', text='Rollback the config; errors drop; alarm returns to OK and sends “resolved”.', text2='Next day: blameless review and a new check in the pipeline.', svc='Measure MTTD and MTTR — detect and repair time')]
ALARM = flow_anim('One alarm, from metric to fix', 'What happens between “errors go up” and “problem solved”.', 'Alarm lifecycle', 'Animation: service emits error metric; alarm evaluates a rule; state change notifies; on-call engineer paged; logs and audit trail show the cause; rollback and recovery.', RN, RS, hid='alarmflow')

# ------------------------------------------------------------------ types
def mapfig():
    o = t(320, 16, 'Seven tools of cloud operations', 11, 'ink', bold=True)
    items = [('1', 'Metrics', 'numbers over time', 'blue'), ('2', 'Logs', 'detailed event records', 'amber'), ('3', 'Traces', 'one request across services', 'violet'), ('4', 'Alarms & notifications', 'rules that wake people', 'red'),
             ('5', 'Dashboards', 'one screen to see health', 'green'), ('6', 'Audit trails', 'who did what, when', 'card'), ('7', 'Service health & advisors', 'provider status, best-practice tips', 'blue')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 12 + (i % 4) * 156; y = 32 + (i // 4) * 84
        o += box(x, y, 148, 70, tn, rx=8) + pin(x + 16, y + 16, n) + t(x + 80, y + 34, a, 8, 'ink', bold=True) + t(x + 78, y + 54, b, 6.4, 'ink2')
    o += t(320, 210, '1–3 are the three pillars of observability; 4–5 turn them into action; 6–7 cover changes and the provider side.', 7.4, 'ink2')
    return o
MAP = bigfig('Map of seven operations tools: metrics, logs, traces, alarms, dashboards, audit trails, service health and advisors.', mapfig(), h=222)

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

A1 = mk(['Measure', 'Store as time series', 'Graph and compare'], ['source|CPU, requests|errors, latency', 'time series|value + time|+ dimensions', 'use|graphs, alarms|percentiles'], ['blue', 'amber', 'green'],
        ['services and agents measure numbers every minute', 'each value is stored with a timestamp and labels', 'you graph them, compare, and alarm on them'],
        [('Measure', 'Services and agents emit numbers every minute (or second).', ''), ('Store', 'Each point = value + time + dimensions (instance, API).', ''), ('Use', 'Graphs, statistics (avg, p99) and alarms.', '')],
        'Metrics in action', 'Numbers over time.', 'Metrics', 'Animation: measure; store as time series; graph and compare.', 'k1anim')
T1 = vt(1, 'Metrics', 'blue',
    'A <b>metric</b> is a numeric measurement collected at regular intervals and stored as a time series — a value with a timestamp and dimensions (labels) such as instance ID or API name — used to observe trends, compute statistics (average, maximum, percentiles) and trigger alarms.',
    'A car’s dashboard gauges: speed, fuel, temperature — numbers that change over time and warn you before the engine overheats.',
    'TiffinGo watches orders per minute, checkout p99 latency, 5xx error count and database connections; CPU is only a supporting signal.',
    'Amazon CloudWatch metrics; Azure Monitor metrics; Google Cloud Monitoring; open source Prometheus + Grafana.', '', A1,
    'you need cheap, fast signals for trends, capacity and alarms.',
    'you need the details of a single event (who, which order) — that is a log.',
    'Numbers measured every minute, like CPU use or number of errors, kept so you can see trends.',
    [('Emit', 'Built-in for managed services.'), ('Agent', 'Memory, disk, app metrics need an agent.'), ('Custom', 'Your own business metrics.'), ('Aggregate', 'Avg, sum, max, p50/p90/p99.'), ('Retain', 'Fine detail short-term, rolled up long-term.')],
    [('time series', 'values recorded over time'), ('dimension', 'a label that splits a metric, e.g. by instance'), ('p99', '99th percentile — 99% of requests were faster than this')],
    table(['', 'Metrics', 'Logs'], [['Form', 'numbers', 'text / JSON events'], ['Cost per signal', 'low', 'higher (per GB)'], ['Answers', 'is something wrong?', 'what exactly happened?']], minw=420),
    ['Capacity planning', 'Alarms', 'SLO tracking'],
    'EC2 sends CPU, network and disk metrics by default, but not memory or disk space — those need the CloudWatch agent. Azure and Google behave the same way for guest-OS metrics.',
    'Averages hide pain: a 200 ms average can hide a 5-second p99. Alarm on percentiles for latency.')

A2 = mk(['Event happens', 'Write a record', 'Search later'], ['event|order failed|user login', 'log record|time, level|message, IDs', 'search|filter, query|patterns'], ['amber', 'blue', 'green'],
        ['something happens in the app or the platform', 'a timestamped record is written, ideally as JSON', 'logs are shipped centrally and searched with queries'],
        [('Event', 'Something happens in the app or platform.', ''), ('Record', 'A timestamped line (ideally structured JSON) is written.', ''), ('Search', 'Logs are centralised and queried.', '')],
        'Logs in action', 'The detailed diary.', 'Logs', 'Animation: event happens; record written; searched later.', 'k2anim')
T2 = vt(2, 'Logs', 'amber',
    'A <b>log</b> is a timestamped record of a discrete event written by an application, operating system or cloud service — for example an error, a request or a login — collected into a central store where it can be filtered, searched with queries and turned into metrics or alerts.',
    'A shop’s daily register: every sale, refund and complaint written down with the time, so you can check later exactly what happened.',
    'Searching logs for “payment key invalid” at 8:32 pm found the cause of TiffinGo’s outage in two minutes.',
    'CloudWatch Logs + Logs Insights; Azure Monitor Logs (Log Analytics, KQL); Google Cloud Logging (Logs Explorer); ELK/OpenSearch, Loki.', '', A2,
    'you need details of individual events for debugging, security or compliance.',
    'you log everything at debug level forever — costs grow fast and searches slow down.',
    'Written records of everything that happened, with the time, which you can search when something goes wrong.',
    [('Write', 'Structured JSON with request ID.'), ('Ship', 'Agent or built-in integration.'), ('Store', 'Log group / workspace / bucket.'), ('Query', 'Insights / KQL / Logging query.'), ('Retain', 'Set retention; archive old logs.')],
    [('structured log', 'log written as fields (JSON), easy to query'), ('retention', 'how long logs are kept'), ('KQL', 'Kusto Query Language used by Azure logs')],
    table(['', 'Application log', 'Audit log'], [['Written by', 'your code', 'the cloud platform'], ['Records', 'what the app did', 'who changed the account'], ['Use', 'debugging', 'security, compliance']], minw=420),
    ['Debugging', 'Security investigations', 'Compliance evidence'],
    'Logs are often one of the largest monitoring costs; teams cut them by sampling success logs, keeping errors, and setting short retention for debug logs.',
    'Put a request/trace ID in every log line — it lets you join logs from five services into one story.')

A3 = mk(['Request enters', 'Each hop timed', 'See the slow part'], ['request|checkout|trace ID created', 'spans|API, payment|DB, cache', 'waterfall|payment = 2.4 s|bottleneck'], ['violet', 'blue', 'red'],
        ['a request gets a unique trace ID at the front door', 'every service records a timed span with that ID', 'a waterfall view shows where time was spent'],
        [('Start', 'A request gets a trace ID at the front door.', ''), ('Spans', 'Each service records a timed span with that ID.', ''), ('Waterfall', 'The view shows which hop was slow or failed.', '')],
        'Traces in action', 'Follow one request.', 'Traces', 'Animation: request enters; each hop timed; slow part revealed.', 'k3anim')
T3 = vt(3, 'Distributed traces', 'violet',
    'A <b>distributed trace</b> records the path and timing of a single request as it travels through multiple services; it consists of <b>spans</b> (one per operation) linked by a shared trace ID, so engineers can see where latency or errors occur in a microservices system.',
    'Tracking a courier parcel: each hub scans it with the time, so you can see exactly where it waited two days.',
    'A trace of one slow checkout showed 2.4 s in the payment gateway call and 40 ms everywhere else — no point tuning the database.',
    'AWS X-Ray and CloudWatch Application Signals; Azure Application Insights; Google Cloud Trace; OpenTelemetry (vendor-neutral), Jaeger, Zipkin.',
    'Microservices are in Lesson 7.4.', A3,
    'requests cross several services and you need to find the slow or failing one.',
    'you have one simple app — logs and metrics may be enough.',
    'A record of one request’s journey through all services, showing how long each step took.',
    [('Instrument', 'SDK or OpenTelemetry auto-instrumentation.'), ('Propagate', 'Trace ID passed in headers.'), ('Sample', 'Keep a % of traces (all errors).'), ('Collect', 'Send to tracing backend.'), ('Analyse', 'Waterfall, service map.')],
    [('span', 'one timed operation inside a trace'), ('sampling', 'keeping only some traces to save cost'), ('OpenTelemetry', 'open standard for metrics, logs and traces')],
    table(['', 'Trace', 'Log'], [['Scope', 'one request across services', 'one event in one service'], ['Shows', 'timing and path', 'details and messages'], ['Best for', 'latency in microservices', 'errors and audit']], minw=420),
    ['Microservices', 'Serverless chains', 'API performance tuning'],
    'OpenTelemetry is supported by all three providers, so instrumenting once lets you send traces to X-Ray, Application Insights, Cloud Trace or an open-source backend.',
    'Trace sampling: keep 100% of errors and slow requests, sample the rest — that is where the cost/insight balance lies.')

A4 = mk(['Rule on a signal', 'State changes', 'Action runs'], ['rule|errors > 20|for 2 of 3 min', 'state|OK → ALARM|→ OK again', 'action|notify, scale|run automation'], ['red', 'amber', 'green'],
        ['a threshold or anomaly rule watches a metric or log', 'when the rule is breached the state changes', 'the change triggers notifications or automatic actions'],
        [('Rule', 'A threshold or anomaly rule on a metric or log query.', ''), ('State', 'OK → ALARM when breached; back to OK when healthy.', ''), ('Action', 'Notify people or run automation.', '')],
        'Alarms in action', 'Rules that wake people.', 'Alarms', 'Animation: rule on a signal; state changes; action runs.', 'k4anim')
T4 = vt(4, 'Alarms and notifications', 'red',
    'An <b>alarm</b> (alert) continuously evaluates a rule — a static threshold, anomaly band or log query — against a metric or log over an evaluation period, changes state when the rule is breached, and triggers <b>notifications</b> (email, SMS, chat, paging) or <b>automated actions</b> (scaling, restarts, runbooks).',
    'A smoke detector: silent most of the time, loud the moment smoke crosses a level — and it should not go off every time you make toast.',
    'TiffinGo’s “payment 5xx > 20 for 2 of 3 minutes” alarm now pages the on-call engineer and posts in the team chat (animation above).',
    'CloudWatch alarms + SNS; Azure Monitor alerts + action groups; Cloud Monitoring alerting policies + notification channels; PagerDuty, Opsgenie.', '', A4,
    'a condition needs human attention or an automatic response.',
    'nobody will act on it — non-actionable alerts cause alert fatigue and real alarms get ignored.',
    'Automatic rules that send a message (or fix something) when a number goes past a limit.',
    [('Choose signal', 'User-facing symptoms first.'), ('Threshold', 'Static, or anomaly detection.'), ('Window', 'M of N data points.'), ('Route', 'Severity → right channel.'), ('Runbook', 'Link what to do.')],
    [('threshold', 'the limit that triggers the alarm'), ('alert fatigue', 'people ignore alerts because there are too many'), ('runbook', 'step-by-step instructions for a known problem')],
    table(['', 'Symptom alarm', 'Cause alarm'], [['Example', 'checkout errors > 1%', 'CPU > 80%'], ['Pages people?', 'yes', 'usually not — ticket/dashboard'], ['False alarms', 'few', 'many']], minw=420),
    ['On-call operations', 'Auto scaling triggers', 'Budget and security alerts'],
    'Google’s SRE practice recommends paging on symptoms users feel (errors, latency) and sending cause-level signals to dashboards or tickets.',
    'Every paging alarm should have an owner, a runbook link and be reviewed monthly: delete the ones nobody acted on.')

A5 = mk(['Pick key signals', 'Arrange on one screen', 'Shared view'], ['signals|golden four|per service', 'layout|widgets|top: user impact', 'audience|on-call, managers|TV screen'], ['green', 'blue', 'amber'],
        ['choose the few signals that show health', 'arrange them with user impact at the top', 'everyone looks at the same truth during incidents'],
        [('Select', 'Choose the few signals that show health.', ''), ('Arrange', 'User impact first, then causes.', ''), ('Share', 'One view for on-call, managers and incidents.', '')],
        'Dashboards in action', 'One screen, one truth.', 'Dashboards', 'Animation: pick signals; arrange widgets; shared view.', 'k5anim')
T5 = vt(5, 'Dashboards', 'green',
    'A <b>dashboard</b> is a curated set of visualisations (graphs, numbers, log tables, alarm states) of key metrics and logs, arranged on one screen so that people can assess system health quickly and share the same view during operations and incidents.',
    'A railway station’s departure board: one glance tells you what is on time, delayed or cancelled.',
    'TiffinGo’s “Dinner rush” dashboard: orders/min, checkout p99, payment errors, DB connections, and the state of the 4 paging alarms — on the office TV every evening.',
    'CloudWatch dashboards; Azure dashboards and Workbooks, Managed Grafana; Cloud Monitoring dashboards; Grafana.', '', A5,
    'teams need a shared, quick view of health or business KPIs.',
    'it has 60 graphs nobody reads — keep 6–12 meaningful widgets.',
    'One screen with the most important graphs, so anyone can see quickly whether things are healthy.',
    [('Audience', 'On-call, business, exec.'), ('Top row', 'User impact (golden signals).'), ('Next', 'Dependencies and capacity.'), ('Annotate', 'Deploys and incidents.'), ('As code', 'Store dashboard JSON in Git.')],
    [('widget', 'one graph or number on a dashboard'), ('KPI', 'key performance indicator'), ('annotation', 'a marker on a graph, e.g. “deploy at 8:30”')],
    table(['', 'Dashboard', 'Alarm'], [['Needs someone looking', 'yes', 'no'], ['Purpose', 'understand', 'notify'], ['Best during', 'incidents, reviews', '24×7 detection']], minw=420),
    ['Operations rooms', 'Incident calls', 'Business reviews'],
    'Many teams keep dashboards as code (JSON/Terraform) so every new service gets the same standard dashboard automatically.',
    'Put deployment markers on graphs — most incidents start right after a change.')

A6 = mk(['Someone acts', 'Platform records', 'Investigate'], ['action|delete bucket|change policy', 'audit record|who, when, from where|what API', 'use|alerts, forensics|compliance'], ['card', 'blue', 'red'],
        ['a person or pipeline calls a cloud API', 'the platform records identity, time, IP and parameters', 'records are kept for security, forensics and audits'],
        [('Act', 'A user, role or pipeline calls a cloud API.', ''), ('Record', 'Platform records who, when, from where and what.', ''), ('Investigate', 'Search, alert on risky changes, prove compliance.', '')],
        'Audit trails in action', 'Who did what, when.', 'Audit trails', 'Animation: someone acts; platform records; investigation.', 'k6anim')
T6 = vt(6, 'Audit trails (activity logs)', 'card',
    'An <b>audit trail</b> is a platform-generated record of management (control-plane) actions in a cloud account — which identity called which API, when, from which IP and with what result — used for security investigations, change tracking, alerting on risky actions and compliance.',
    'The visitor register and CCTV at an office gate: who entered, when, and which room they went to.',
    'The audit trail showed the deploy role changed the payment secret at 8:30 pm — two minutes before errors started.',
    'AWS CloudTrail; Azure Activity Log (and Entra ID sign-in/audit logs); Google Cloud Audit Logs (Admin Activity, Data Access).', 'Identity is covered in Module 9.', A6,
    'always — enable it everywhere, store it centrally and protect it from deletion.',
    'you rely only on the default short history — export to long-term storage for investigations.',
    'Automatic records of who changed what in your cloud account, and when.',
    [('Enable', 'On by default for management events (90 days in AWS event history).'), ('Trail/export', 'To a bucket or workspace for long-term.'), ('Protect', 'Separate account, immutable storage.'), ('Alert', 'Root login, policy changes, deletes.'), ('Query', 'Investigate by user, resource, time.')],
    [('control plane', 'APIs that create/change resources'), ('data plane', 'using the resource itself, e.g. reading an object'), ('forensics', 'investigating what happened after an incident')],
    table(['', 'Management events', 'Data events'], [['Example', 'DeleteBucket, RunInstances', 'GetObject, PutObject'], ['Default', 'on', 'usually off (volume, cost)'], ['Use', 'change tracking', 'data access auditing']], minw=440),
    ['Security investigations', 'Change management', 'Compliance audits (ISO, SOC 2, RBI)'],
    'In many cloud breach investigations, attackers try to stop or delete audit logging first — which is why organisations send audit logs to a separate, locked-down account.',
    'Alert on a short list of high-risk events: root/owner sign-in, audit logging stopped, IAM policy attached with admin rights, public bucket created.')

A7 = mk(['Provider issue?', 'Check health', 'Advisors suggest'], ['symptom|errors in one AZ|is it us?', 'health|Region status|your resources', 'advisor|cost, security|reliability tips'], ['blue', 'amber', 'green'],
        ['when things break, first ask: is it us or the provider?', 'personal health dashboards show provider events affecting your resources', 'advisors recommend fixes for cost, security, reliability'],
        [('Ask', 'Is it our change or a provider event?', ''), ('Health', 'Personalised health shows events affecting your resources.', ''), ('Advise', 'Advisors recommend cost, security and reliability fixes.', '')],
        'Service health and advisors in action', 'Is it us or them?', 'Service health', 'Animation: question; check health; advisors suggest.', 'k7anim')
T7 = vt(7, 'Service health and advisors', 'blue',
    '<b>Service health</b> tools report the provider’s own operational events — outages, degradations and scheduled maintenance — personalised to the services and Regions you use; <b>advisors</b> continuously check your configuration and recommend improvements for cost, security, reliability and performance.',
    'The airline’s flight-status app (is the delay theirs?) plus a mechanic’s checklist that tells you which tyres to change.',
    'During one incident AWS Health showed an elevated-error event for a service in ap-south-1 — the team stopped debugging its own code and failed over instead.',
    'AWS Health Dashboard, Trusted Advisor; Azure Service Health, Resource Health, Advisor; Google Cloud Service Health / Personalized Service Health, Active Assist (Recommender).',
    'Right-sizing recommendations were used in Lesson 2.5.', A7,
    'every incident (first check) and weekly hygiene reviews.',
    'you treat advisor scores as the goal — they are hints, not a full architecture review.',
    'The provider’s own status page for your account, plus automatic tips to save money and be safer.',
    [('Subscribe', 'Health alerts to your channel.'), ('Check', 'First step in every incident.'), ('Review', 'Advisor weekly.'), ('Act', 'Ticket each accepted recommendation.'), ('Track', 'Scores over time.')],
    [('scheduled maintenance', 'planned provider work that may affect you'), ('personalised health', 'status filtered to your resources'), ('recommendation', 'a suggested change with expected benefit')],
    table(['', 'Public status page', 'Personalised health'], [['Scope', 'whole provider', 'your account’s resources'], ['Detail', 'general', 'specific resources, timelines'], ['Notifications', 'RSS / manual', 'alerts to your channels']], minw=440),
    ['Incident triage', 'Weekly operations review', 'Cost and security hygiene'],
    'The full set of Trusted Advisor checks is available only with Business support or higher; basic accounts see a core subset — check your plan before relying on it.',
    'Wire health events into the same channel as your alarms; during big provider incidents the public status page itself is sometimes slow to update.')

SUMMARY = table(['#', 'Tool', 'Answers', 'AWS', 'Azure', 'Google Cloud'], [
    ['1', 'Metrics', 'is something wrong?', 'CloudWatch metrics', 'Azure Monitor metrics', 'Cloud Monitoring'], ['2', 'Logs', 'what happened?', 'CloudWatch Logs', 'Log Analytics', 'Cloud Logging'], ['3', 'Traces', 'where is it slow?', 'X-Ray / Application Signals', 'Application Insights', 'Cloud Trace'],
    ['4', 'Alarms', 'who must act?', 'CloudWatch alarms + SNS', 'Alerts + action groups', 'Alerting policies + channels'], ['5', 'Dashboards', 'how healthy now?', 'CloudWatch dashboards', 'Dashboards / Workbooks', 'Monitoring dashboards'],
    ['6', 'Audit trails', 'who changed what?', 'CloudTrail', 'Activity Log', 'Cloud Audit Logs'], ['7', 'Health & advisors', 'is it them? what to improve?', 'Health, Trusted Advisor', 'Service Health, Advisor', 'Service Health, Recommender']], minw=680)
CHECK = ('  <h3>Check yourself: which tool?</h3>\n' +
    qx('A. Who deleted the production bucket last night?', ['Audit trail', 'Metrics', 'Traces', 'Dashboard'], 0, 'CloudTrail / Activity Log / Audit Logs.') +
    qx('B. Which of five services makes checkout slow?', ['Traces', 'Audit trail', 'Advisor', 'Budget'], 0, 'Distributed tracing.') +
    qx('C. Email the team when errors exceed 1% for 3 minutes.', ['Alarm + notification', 'Dashboard', 'Trace', 'Log retention'], 0, 'Alarm.') +
    qx('D. Is the Mumbai Region having a problem with our database service?', ['Service health', 'Traces', 'Logs Insights', 'Tags'], 0, 'Personalised health.'))

TYPES = ('  <p>Seven tools, each in the same pattern: definition, plain words, analogy, internal steps, animation, differences, where used, real-world example, TiffinGo scenario and an expert note.</p>\n'
         + challenge(['Why can a CPU graph look fine while customers see errors?', 'What is the first thing attackers often try to switch off?', 'Why page on symptoms rather than causes?'], 'types 1, 6 and 4') + MAP
         + jump(['Metrics', 'Logs', 'Traces', 'Alarms', 'Dashboards', 'Audit', 'Health']) + T1 + T2 + T3 + T4 + T5 + T6 + T7
         + '\n  <h3 style="margin-top:34px">All seven side by side</h3>\n' + SUMMARY + '\n' + CHECK)

parts = wwu([
    ('Monitoring agent', 'Software on VMs that sends OS metrics and logs.', 'Memory, disk space and app logs are not visible without it.', 'CloudWatch agent, Azure Monitor Agent, Ops Agent.'),
    ('Notification channel', 'Where alerts go.', 'An alarm nobody receives is useless.', 'SNS topic, action group, notification channel.'),
    ('Log retention', 'How long logs are kept.', 'Cost and compliance.', 'Never-expire by default in some services — set it.'),
    ('Tags / labels', 'Metadata on resources.', 'Filter dashboards and costs by app/team.', 'app=orders, env=prod.'),
    ('Runbook', 'What to do when an alarm fires.', 'Faster, calmer response.', 'Linked from the alarm description.'),
    ('SLO', 'A target like 99.9% successful checkouts.', 'Decides what to alarm on and when to slow releases.', 'Error budget.')])

DEEP = ('  <h3>SLI, SLO, SLA and error budgets</h3>\n  <p>An <b>SLI</b> is a measured indicator (e.g. % successful checkouts). An <b>SLO</b> is your internal target for it (99.9% per 30 days). An <b>SLA</b> is the contractual promise with penalties (Lesson 5.4). The <b>error budget</b> is 100% − SLO: 99.9% allows about 43 minutes of failures in 30 days. When the budget is spent, teams slow feature releases and fix reliability.</p>\n'
    '  <h3>MTTD, MTTA, MTTR</h3>\n' + table(['Measure', 'Meaning', 'Improved by'], [['MTTD', 'mean time to detect', 'symptom alarms, synthetic checks'], ['MTTA', 'mean time to acknowledge', 'good routing, on-call rota'], ['MTTR', 'mean time to restore', 'runbooks, rollbacks, logs + traces, audit trail']], minw=520) +
    '\n  <h3>Administering the cloud: daily, weekly, monthly</h3>\n  <ul><li><b>Daily:</b> alarms and incidents, failed backups, unusual spend, security findings.</li><li><b>Weekly:</b> advisor recommendations, patch status (Systems Manager / Update Manager / VM Manager), access reviews for new admins.</li><li><b>Monthly:</b> cost review by tag, quota headroom, alarm review (delete non-actionable ones), restore test of one backup.</li></ul>\n'
    '  <h3>Synthetic monitoring</h3>\n  <p>Real-user signals need real users. <b>Synthetic checks</b> (CloudWatch Synthetics canaries, Application Insights availability tests, Cloud Monitoring uptime checks) call your site from outside every minute, so you know it is down at 3 am even with no traffic.</p>\n'
    '  <h3>Monitoring costs to watch</h3>\n  <p>Custom metrics (per metric per month), log ingestion (per GB), log retention (per GB-month), high-resolution metrics and dashboards beyond free counts. Free tiers cover labs; production bills are dominated by log volume.</p>')

clouds = vendor_tabs('<p><b>AWS:</b> Amazon CloudWatch (metrics, Logs, Logs Insights, alarms, dashboards, Synthetics, Application Signals), AWS X-Ray, AWS CloudTrail, Amazon SNS, AWS Health Dashboard, Trusted Advisor, Systems Manager for administration.</p>',
    '<p><b>Azure:</b> Azure Monitor (metrics, Log Analytics with KQL, alerts, action groups, Workbooks), Application Insights, Activity Log, Service Health and Resource Health, Azure Advisor, Update Manager.</p>',
    '<p><b>Google Cloud:</b> Cloud Monitoring (metrics, uptime checks, alerting policies, dashboards), Cloud Logging (Logs Explorer, log-based metrics), Cloud Trace, Cloud Audit Logs, Personalized Service Health, Active Assist recommendations, VM Manager.</p>') + \
    cloud3([['Metrics + alarms', 'CloudWatch', 'Azure Monitor', 'Cloud Monitoring'], ['Logs + query', 'CloudWatch Logs Insights', 'Log Analytics (KQL)', 'Logs Explorer'], ['Tracing', 'X-Ray / Application Signals', 'Application Insights', 'Cloud Trace'], ['Audit', 'CloudTrail', 'Activity Log', 'Cloud Audit Logs'], ['Notifications', 'SNS', 'Action groups', 'Notification channels'], ['Health / advice', 'Health, Trusted Advisor', 'Service Health, Advisor', 'Service Health, Recommender']])

# ------------------------------------------------------------------ practical
MOCKQ.extend([
 (mock('aws', ['Amazon SNS', 'Topics', 'Create topic'], ['Dashboard', 'Topics', 'Subscriptions'], 'Topics',
       [('Type', '[x] Standard'), ('Name', 'ops-alerts'), ('Subscription · Protocol', '▾ Email'), ('Endpoint', 'you@example.com')], 'Create topic'),
  mock('az', ['Home', 'Monitor', 'Alerts', 'Action groups', 'Create'], ['Basics', 'Notifications', 'Actions', 'Tags'], 'Notifications',
       [('Action group name', 'ops-alerts'), ('Notification type', '▾ Email/SMS message/Push/Voice'), ('Email', 'you@example.com')], 'Review + create'),
  mock('gcp', ['Monitoring', 'Alerting', 'Edit notification channels'], ['Overview', 'Dashboards', 'Alerting', 'Uptime checks'], 'Alerting',
       [('Email', 'Add new'), ('Email address', 'you@example.com'), ('Display name', 'ops-alerts')], 'Save')),
 (mock('aws', ['CloudWatch', 'Logs', 'Logs Insights'], ['Dashboards', 'Alarms', 'Logs', 'Metrics'], 'Logs',
       [('Log group', 'tiffingo-orders'), ('Query', 'fields @timestamp, @message | filter level = "ERROR"')], 'Run query'),
  mock('az', ['Home', 'Monitor', 'Activity log'], ['Overview', 'Activity log', 'Alerts', 'Metrics', 'Logs'], 'Activity log',
       [('Timespan', '▾ Last 6 hours'), ('Resource group', '▾ rg-ops'), ('Event', 'Create or Update Virtual Network')], 'Download as CSV'),
  mock('gcp', ['Logging', 'Logs Explorer'], ['Logs Explorer', 'Log Analytics', 'Logs-based metrics', 'Log Router'], 'Logs Explorer',
       [('Query', 'logName:"tiffingo-orders" AND severity>=ERROR'), ('Results', '1 entry · payment key invalid')], 'Run query')),
 (mock('aws', ['CloudWatch', 'Alarms', 'Create alarm'], ['Dashboards', 'Alarms', 'Logs', 'Metrics'], 'Alarms',
       [('Metric', 'TiffinGo · PaymentErrors'), ('Condition', 'Greater than 20 · 1 of 1 datapoints · 1 minute'), ('Notification', 'In alarm → ops-alerts')], 'Create alarm'),
  mock('az', ['Home', 'Monitor', 'Alerts', 'Create alert rule'], ['Scope', 'Condition', 'Actions', 'Details'], 'Condition',
       [('Signal', 'Activity log · Delete Virtual Network'), ('Scope', 'rg-ops'), ('Action group', 'ops-alerts')], 'Review + create'),
  mock('gcp', ['Monitoring', 'Alerting', 'Create policy'], ['Overview', 'Dashboards', 'Alerting'], 'Alerting',
       [('Condition', 'Log match · severity=ERROR AND logName:tiffingo-orders'), ('Notification channel', 'ops-alerts'), ('Rate limit', '1 notification per 5 min')], 'Create policy')),
 (mock('aws', ['CloudTrail', 'Event history'], ['Dashboard', 'Event history', 'Trails', 'Lake'], 'Event history',
       [('Lookup attributes', '▾ Event name = CreateTopic'), ('User name / time / source IP', 'shown per event')], 'Download events'),
  mock('az', ['Home', 'Monitor', 'Activity log'], ['Overview', 'Activity log', 'Alerts'], 'Activity log',
       [('Filter', 'Operation = Delete Virtual Network'), ('Event initiated by', 'you@example.com')], 'JSON'),
  mock('gcp', ['Logging', 'Logs Explorer'], ['Logs Explorer', 'Log Router'], 'Logs Explorer',
       [('Query', 'logName:"cloudaudit.googleapis.com%2Factivity"'), ('protoPayload.authenticationInfo', 'principalEmail · methodName')], 'Run query')),
])

STEP1 = ('1 · Create an email notification channel', tri(
    (['[[Simple Notification Service]] → [[Topics]] → [[Create topic]] → [[Standard]], name <code>ops-alerts</code> → [[Create topic]].', '[[Create subscription]] → protocol [[Email]] → your address → open the email and click [[Confirm subscription]].'],
     'TOPIC=$(aws sns create-topic --name ops-alerts --query TopicArn --output text)\naws sns subscribe --topic-arn $TOPIC --protocol email --notification-endpoint you@example.com\n# confirm the email, then:\naws sns list-subscriptions-by-topic --topic-arn $TOPIC --query "Subscriptions[].[Endpoint,SubscriptionArn]" --output text',
     'your email with a real subscription ARN (not <code>PendingConfirmation</code>) after you click the link.'),
    (['[[Monitor]] → [[Alerts]] → [[Action groups]] → [[Create]]: resource group <code>rg-ops</code>, name <code>ops-alerts</code>.', '[[Notifications]] → type [[Email/SMS message/Push/Voice]] → tick Email → your address → [[Review + create]].'],
     'az group create -n rg-ops -l centralindia\naz monitor action-group create -g rg-ops -n ops-alerts --short-name opsalerts \\\n  --action email me you@example.com\naz monitor action-group show -g rg-ops -n ops-alerts --query "emailReceivers[].{name:name,email:emailAddress,status:status}" -o table',
     'the receiver listed with status <code>Enabled</code>; Azure sends a “you’ve been added to an action group” email.'),
    (['[[Monitoring]] → [[Alerting]] → [[Edit notification channels]] → [[Email]] → [[Add new]] → address + display name <code>ops-alerts</code> → [[Save]].'],
     'gcloud beta monitoring channels create --display-name=ops-alerts --type=email \\\n  --channel-labels=email_address=you@example.com\ngcloud beta monitoring channels list --format="table(name,displayName,labels.email_address)"',
     'a channel named <code>projects/…/notificationChannels/…</code> with your email.')),
    'Use a shared team address or chat integration in real life — not one person’s inbox.')

STEP2 = ('2 · Write logs and search them', tri(
    (['[[CloudWatch]] → [[Log groups]] → [[Create log group]] <code>tiffingo-orders</code>, retention [[1 day]].', 'After the CLI writes events: [[Logs Insights]] → select the group → run the query shown in the sketch.'],
     'aws logs create-log-group --log-group-name tiffingo-orders\naws logs put-retention-policy --log-group-name tiffingo-orders --retention-in-days 1\naws logs create-log-stream --log-group-name tiffingo-orders --log-stream-name api-1\nNOW=$(date +%s000)\ncat > events.json <<EOF\n[{"timestamp":$NOW,"message":"{\\"level\\":\\"INFO\\",\\"msg\\":\\"order placed\\",\\"order\\":\\"O-1\\"}"},\n {"timestamp":$NOW,"message":"{\\"level\\":\\"ERROR\\",\\"msg\\":\\"payment key invalid\\",\\"order\\":\\"O-2\\"}"}]\nEOF\naws logs put-log-events --log-group-name tiffingo-orders --log-stream-name api-1 --log-events file://events.json\nsleep 5; aws logs filter-log-events --log-group-name tiffingo-orders --filter-pattern \'{ $.level = "ERROR" }\' --query "events[].message" --output text',
     'only the ERROR line: <code>{"level":"ERROR","msg":"payment key invalid","order":"O-2"}</code> — a JSON filter on structured logs.'),
    (['Every Azure change is logged automatically: [[Monitor]] → [[Activity log]] → filter resource group <code>rg-ops</code>, last hour — you will see the action group you created.', '(Application logs go to a Log Analytics workspace — pay per GB — so the lab uses the free activity log.)'],
     'az monitor activity-log list --resource-group rg-ops --offset 1h \\\n  --query "[].{time:eventTimestamp,op:operationName.localizedValue,by:caller,status:status.value}" -o table',
     'rows like “Create or update action group … Succeeded” with your email as caller.'),
    (['[[Logging]] → [[Logs Explorer]] → after the CLI writes entries, run <code>logName:"tiffingo-orders" AND severity&gt;=ERROR</code>.'],
     'gcloud logging write tiffingo-orders \'{"msg":"order placed","order":"O-1"}\' --payload-type=json --severity=INFO\ngcloud logging write tiffingo-orders \'{"msg":"payment key invalid","order":"O-2"}\' --payload-type=json --severity=ERROR\nsleep 10; gcloud logging read \'logName:"tiffingo-orders" AND severity>=ERROR\' --limit=5 --format="value(timestamp,jsonPayload.msg)"',
     'one line with a timestamp and <code>payment key invalid</code>.')),
    'Structured (JSON) logs make queries exact: filter by field, not by guessing words.')

STEP3 = ('3 · Build an alarm that really fires', tri(
    (['[[CloudWatch]] → [[Alarms]] → [[Create alarm]] → metric <code>TiffinGo / PaymentErrors</code> (appears after the first put-metric-data) → Greater than 20, 1 of 1 data points, 1 minute → notify <code>ops-alerts</code>.', 'Push a high value with the CLI and wait 1–3 minutes for the email.'],
     'aws cloudwatch put-metric-data --namespace TiffinGo --metric-name PaymentErrors --value 3\naws cloudwatch put-metric-alarm --alarm-name payment-errors-high --namespace TiffinGo --metric-name PaymentErrors \\\n  --statistic Sum --period 60 --evaluation-periods 1 --threshold 20 --comparison-operator GreaterThanThreshold \\\n  --treat-missing-data notBreaching --alarm-actions $TOPIC --ok-actions $TOPIC\naws cloudwatch put-metric-data --namespace TiffinGo --metric-name PaymentErrors --value 41\nsleep 120; aws cloudwatch describe-alarms --alarm-names payment-errors-high --query "MetricAlarms[0].[StateValue,StateReason]" --output text',
     '<code>ALARM  Threshold Crossed: 1 datapoint [41.0 …] was greater than the threshold (20.0)</code> and an “ALARM” email. A few minutes later it returns to OK (missing data = not breaching) and sends “OK”.'),
    (['[[Monitor]] → [[Alerts]] → [[Create alert rule]] → scope <code>rg-ops</code> → condition [[Activity log]] signal “Delete Virtual Network” → action group <code>ops-alerts</code>.', 'Create and delete a test VNet to fire it (activity-log alerts are free).'],
     'SUB=$(az account show --query id -o tsv)\nAG=$(az monitor action-group show -g rg-ops -n ops-alerts --query id -o tsv)\naz monitor activity-log alert create -g rg-ops -n vnet-deleted --scope /subscriptions/$SUB/resourceGroups/rg-ops \\\n  --condition category=Administrative and operationName=Microsoft.Network/virtualNetworks/delete \\\n  --action-group $AG\naz network vnet create -g rg-ops -n test-vnet --address-prefixes 10.80.0.0/16\naz network vnet delete -g rg-ops -n test-vnet',
     'the alert rule JSON, then within ~5 minutes an email “Activity log alert vnet-deleted” showing who deleted <code>test-vnet</code>.'),
    (['[[Monitoring]] → [[Alerting]] → [[Create policy]] → condition [[Log match]] on <code>logName:"tiffingo-orders" AND severity=ERROR</code> → channel <code>ops-alerts</code> → notification rate limit 5 minutes.', 'Write another ERROR log line to fire it. Check current Cloud Monitoring alerting pricing — one policy for a few hours costs at most a few rupees.'],
     "P=$(gcloud config get-value project)\nCH=$(gcloud beta monitoring channels list --filter='displayName=ops-alerts' --format='value(name)')\ncat > policy.json <<EOF\n{\"displayName\":\"payment-errors\",\"combiner\":\"OR\",\n \"conditions\":[{\"displayName\":\"error log\",\"conditionMatchedLog\":{\"filter\":\"logName=\\\\\"projects/$P/logs/tiffingo-orders\\\\\" AND severity=ERROR\"}}],\n \"alertStrategy\":{\"notificationRateLimit\":{\"period\":\"300s\"}},\"notificationChannels\":[\"$CH\"]}\nEOF\ngcloud alpha monitoring policies create --policy-from-file=policy.json\ngcloud logging write tiffingo-orders '{\"msg\":\"payment key invalid\",\"order\":\"O-3\"}' --payload-type=json --severity=ERROR",
     'the policy created, then within a few minutes an incident email for <code>payment-errors</code>.')),
    'An alarm you have never seen fire is an alarm you cannot trust — always test the full path to the inbox.')

STEP4 = ('4 · Find out who changed what (audit trail)', tri(
    (['[[CloudTrail]] → [[Event history]] → lookup attribute [[Event name]] = <code>CreateTopic</code> or <code>PutMetricAlarm</code> → open an event: user, time, source IP, request parameters.'],
     'aws cloudtrail lookup-events --lookup-attributes AttributeKey=EventName,AttributeValue=PutMetricAlarm --max-results 3 \\\n  --query "Events[].[EventTime,Username,EventName]" --output table',
     'your user name and the time you created the alarm. Event history keeps 90 days of management events for free; create a trail to keep more.'),
    (['[[Monitor]] → [[Activity log]] → filter Operation = “Delete Virtual Network” → open the event → [[JSON]]: <code>caller</code>, <code>claims</code>, <code>httpRequest.clientIpAddress</code>.'],
     'az monitor activity-log list -g rg-ops --offset 1h \\\n  --query "[?contains(operationName.value,\'virtualNetworks/delete\')].{time:eventTimestamp,by:caller,status:status.value}" -o table',
     'the delete with your account as caller and status <code>Succeeded</code>.'),
    (['[[Logs Explorer]] → query <code>logName:"cloudaudit.googleapis.com%2Factivity"</code> → expand an entry → <code>protoPayload.authenticationInfo.principalEmail</code> and <code>methodName</code>.'],
     'gcloud logging read \'logName:"cloudaudit.googleapis.com%2Factivity" AND protoPayload.serviceName="monitoring.googleapis.com"\' \\\n  --limit=5 --format="table(timestamp,protoPayload.authenticationInfo.principalEmail,protoPayload.methodName)"',
     'your email and methods like <code>google.monitoring.v3.AlertPolicyService.CreateAlertPolicy</code>.')),
    'In real incidents this is step one after “what is broken”: “what changed just before?”')

prac = practical(OWN_INTRO + ' You will set up the full chain: notification channel → logs → an alarm that really fires → audit trail. Everything fits free tiers (Google alerting may cost a few rupees — clean up the same day).', [SETUP_STEP, STEP1, STEP2, STEP3, STEP4],
    cleanup='<b>AWS:</b> <code>aws cloudwatch delete-alarms --alarm-names payment-errors-high</code>; <code>aws logs delete-log-group --log-group-name tiffingo-orders</code>; <code>aws sns delete-topic --topic-arn $TOPIC</code> (the custom metric expires by itself). '
            '<b>Azure:</b> <code>az group delete -n rg-ops --yes --no-wait</code> (removes the action group and alert rule). '
            '<b>Google Cloud:</b> <code>gcloud alpha monitoring policies list --format="value(name)"</code> → <code>gcloud alpha monitoring policies delete &lt;name&gt;</code>; <code>gcloud beta monitoring channels delete &lt;name&gt;</code>; <code>gcloud logging logs delete tiffingo-orders</code>.')

mist = mistakes([
    ['Alarms only on CPU.', 'Default metrics are infrastructure.', 'Alarm on user symptoms: errors, latency, failed orders.'],
    ['Alert fatigue.', 'Every warning pages someone.', 'Page only actionable symptoms; others to dashboards/tickets.'],
    ['No memory/disk metrics on VMs.', 'Agent not installed.', 'Install CloudWatch agent / Azure Monitor Agent / Ops Agent.'],
    ['Logs kept forever (or not at all).', 'Default retention never set.', 'Set retention per log group; archive what compliance needs.'],
    ['Alarm never tested.', 'Created and forgotten.', 'Fire it on purpose (step 3); test after changes.'],
    ['Audit logs in the same account attackers can reach.', 'Default setup.', 'Central, locked-down log archive account/project.']])

cert = table(['Exam / syllabus', 'What is asked'], [['C-DAC PGCP-BDA', 'Administering and monitoring cloud services; monitoring tools.'], ['AWS CLF-C02', 'CloudWatch vs CloudTrail vs Config, SNS, AWS Health Dashboard, Trusted Advisor, X-Ray.'], ['AZ-900', 'Azure Monitor, Log Analytics, alerts, Application Insights, Service Health, Advisor.'], ['Google Cloud Digital Leader', 'Cloud Operations suite (Monitoring, Logging, Trace), SRE ideas, SLOs.']], minw=560) + \
    qx('1. Which AWS service records API calls made in an account?', ['CloudWatch', 'CloudTrail', 'X-Ray', 'Inspector'], 1, 'CloudTrail = audit.') + \
    qx('2. Which AWS service collects metrics and triggers alarms?', ['CloudWatch', 'CloudTrail', 'Artifact', 'Shield'], 0, 'CloudWatch.') + \
    qx('3. Which Azure service gives recommendations for cost, security and reliability?', ['Azure Advisor', 'Azure Arc', 'Azure DNS', 'Azure Bastion'], 0, 'Advisor.') + \
    qx('4. Which shows Azure outages affecting your resources?', ['Service Health', 'Cost Management', 'Policy', 'Blueprints'], 0, 'Service Health.') + \
    qx('5. Which tool shows where time is spent in a request across microservices?', ['Distributed tracing', 'Audit log', 'Budget alert', 'Tagging'], 0, 'Tracing.') + \
    qx('6. EC2 memory utilisation in CloudWatch requires…', ['nothing', 'the CloudWatch agent', 'CloudTrail', 'a bigger instance'], 1, 'Guest-OS metrics need the agent.')

proj = miniproject('Mini project: TiffinGo “dinner rush” operations pack',
    'Design and build the monitoring for TiffinGo’s order service.',
    ['<b>SLO:</b> define one SLI and SLO for checkout (e.g. 99.9% success per 30 days) and its error budget.',
     '<b>Signals:</b> list the four golden signals with exact metric names in your cloud.',
     '<b>Alarms:</b> 3 paging alarms (symptoms) and 3 ticket-level alarms (causes), each with a runbook line.',
     '<b>Dashboard:</b> build a 6-widget dashboard (CloudWatch / Workbook / Monitoring) with your custom metric from step 3.',
     '<b>Audit:</b> list 5 high-risk audit events to alert on.',
     '<b>Review:</b> write a one-page blameless review of the 8:30 pm outage using the timeline from the animation.'],
    'An SLO, alarm list with runbooks, a dashboard screenshot and an incident review.', '7.2 (availability) + 5.4 (SLAs) + 8.1.')

assemble_v2(HERE, story_h2='Customers noticed first', hook_html=hk,
    narration='On a Friday evening TiffinGo’s payments started failing. Nobody on the team knew until customers complained online; it took more than an hour to find a configuration change made minutes earlier.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Administering and monitoring cloud services',
    formal='<b>Cloud monitoring</b> is the continuous collection and analysis of metrics, logs, traces and events from cloud resources and applications to detect problems, understand behaviour and trigger responses; <b>cloud administration</b> is the ongoing management of those resources — configuration, access, patching, capacity, cost and change control — using provider tools such as Amazon CloudWatch and CloudTrail, Azure Monitor and Activity Log, and Google Cloud Monitoring, Logging and Audit Logs.',
    simple='Watching your cloud systems with numbers, records and alarms, so you find and fix problems before customers notice — and keeping track of every change.',
    interview=['“Monitoring uses metrics to detect, logs and traces to explain, alarms to act, dashboards to see, and audit trails to know who changed what. In AWS that is CloudWatch, X-Ray and CloudTrail; in Azure, Azure Monitor, Application Insights and Activity Log; in Google Cloud, Cloud Monitoring, Logging, Trace and Audit Logs.”', '“I alarm on user-facing symptoms — the four golden signals — and keep cause metrics on dashboards to avoid alert fatigue.”'],
    terms_rows=[('Metric', 'Number over time.'), ('Log', 'Timestamped event record.'), ('Trace', 'One request across services.'), ('Alarm', 'Rule that notifies/acts.'), ('Audit trail', 'Who did what, when.'), ('Golden signals', 'Latency, traffic, errors, saturation.'), ('SLO', 'Internal reliability target.'), ('MTTR', 'Mean time to restore.')],
    exam='CLF-C02 favourite: <b>CloudWatch</b> (performance metrics, alarms) vs <b>CloudTrail</b> (API activity, who did what). AZ-900: Azure Monitor, Log Analytics, Service Health, Advisor.',
    picture_h2='The observability loop and what to watch', picture_html=picture,
    after_picture=[('types', 'Types, one by one', 'Seven tools of cloud operations, one by one', TYPES)],
    how_h2='One alarm, from metric to fix', how_intro='Step by step, the path that should have warned TiffinGo first.', how_anim=ALARM,
    parts_h2='Six things that make monitoring work', parts_html=parts, lv='',
    myth_rows=[('The provider monitors my app.', 'It monitors its infrastructure; your app is yours.', 'Responsibility table.'), ('More alerts = safer.', 'Non-actionable alerts get ignored.', 'Type 4.'), ('CPU tells me if users are happy.', 'Errors and latency do.', 'Golden signals.')],
    extra_secs=[('deep', 'Deep dive', 'SLOs and error budgets, MTTx, admin routines, synthetics, costs', DEEP)],
    clouds_html=clouds, practical_html=prac, mistakes_html=mist, cert_html=cert, project_html=proj,
    can_now=['Explain metrics, logs, traces, alarms, dashboards, audit trails and service health.', 'Choose what to monitor with the four golden signals and SLOs.', 'Trace an alarm from metric to fix.', 'Set up notifications, logs, a firing alarm and audit queries on AWS, Azure or Google Cloud.', 'Answer CloudWatch vs CloudTrail questions confidently.'],
    next_html='<a href="../02-deploying-an-application-on-the-cloud/">8.2 Deploying an application on the cloud</a>.',
    pre='<b>Before you start:</b> Module 7 (architecture) and Lesson 5.4 (SLAs).')
