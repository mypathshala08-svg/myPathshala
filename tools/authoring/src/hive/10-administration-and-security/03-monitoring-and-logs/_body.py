import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return re.sub(r'; Query ID[^\n]*', '', open(CAP + n).read().rstrip())

def opbox(x, y, label, sub='', tone='card', w=128, h=26):
    o = box(x, y, w, h, tone) + t(x + w / 2, y + (11 if sub else 16), label, 7.2, 'ink', bold=True)
    if sub:
        o += t(x + w / 2, y + 21, sub, 6.4, 'ink2', mono=True)
    return o

def fig(src, w, h, alt, caption):
    return f'''  <figure style="margin:18px 0">
    <img src="{src}" width="{w}" height="{h}" loading="lazy" alt="{alt}" style="max-width:100%;height:auto;border:1px solid var(--line);border-radius:8px">
    <figcaption class="muted" style="font-size:.9em;margin-top:6px">{caption}</figcaption>
  </figure>
'''

# ---------------------------------------------------------------- story
sc = (box(10, 12, 180, 128, 'card') + t(100, 30, 'HiveServer2 :10002', 8.8, bold=True) +
      ''.join(t(22, 52 + k * 16, s, 7.2, 'ink2', anchor='start', mono=True) for k, s in enumerate(['/        sessions, queries', 'query_page  drilldown', '/jmx      metrics', '/conf     configuration', '/stacks   thread dump'])) +
      arrow(194, 76, 232, 76, 'acc', 2) +
      box(236, 12, 180, 128, 'card') + t(326, 30, 'Logs', 8.8, bold=True) +
      ''.join(t(248, 52 + k * 16, s, 7.2, 'ink2', anchor='start', mono=True) for k, s in enumerate(['HiveServer2 log', 'operation logs (Beeline)', 'historic operation logs', 'Tez / YARN task logs', 'grep by queryId'])) +
      arrow(420, 76, 452, 76, 'acc', 2) +
      box(456, 12, 174, 128, 'amber') + t(543, 30, 'Found in the lab', 8.8, bold=True) +
      ''.join(t(468, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([('metrics off by default', 'ink'), ('Query Plan tab empty', 'ink'), ('compactor log noise', 'ink'), ('/conf hides password …', 'green'), ('… /jmx shows it', 'red')])))
scene_svg = scene('HiveServer2’s web UI on port 10002 shows sessions, queries, metrics, configuration and threads; logs come from the server, the operations and the Tez tasks. The lab found several surprises, including a password visible through the metrics endpoint.', sc,
                  'You cannot run what you cannot <tspan font-weight="700" class="s-acc">see</tspan>.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Is Hive slow right now, or is it just my query?”</h2>
  <div class="story">
    <p class="narration">Monday, 10 a.m. Three analysts message Riya at once: queries are slow. Lesson 8.5 taught her to read one query’s plan and errors. Now she needs the view from the server: who is connected, what is running, how long things take, and where the logs are.</p>

{scene_svg}

R> Sir, is there a dashboard for HiveServer2?
A> Every HiveServer2 has a small <b>web UI</b> on port <b>10002</b>: live sessions and queries, a drilldown per query with timings, a metrics dump, the configuration and a thread dump. Behind it are <b>metrics</b> you can export to monitoring systems, and three kinds of <b>logs</b>: the server log, the per-query operation logs and the Tez task logs.
K> Then we just open it?
A> Open it and you will find, as we did, that metrics are off by default in this build, the plan tab needs a setting, the logs are full of background noise, and the metrics page showed our metastore password to anyone. All outputs and screenshots are real, from Hive 4.2.1.
  </div>
</section>
'''

lv = '''
LEVELS> Monitoring at three levels
L1> A car dashboard
      <ul>
        <li>The web UI is HiveServer2’s dashboard: how many people are connected and which queries are running now.</li>
        <li><b>Metrics</b> are the gauges: counts and timings you can chart over days.</li>
        <li><b>Logs</b> are the trip recorder: what exactly happened, line by line, when something went wrong.</li>
      </ul>
L2> Where each piece lives
      <ul>
        <li>Web UI: <code>http://hs2-host:10002/</code> (<code>hive.server2.webui.port</code>); <code>/jmx</code>, <code>/conf</code>, <code>/stacks</code>, <code>/logs</code>, drilldown <code>query_page.html?operationId=…</code>.</li>
        <li>Metrics: <code>hive.server2.metrics.enabled=true</code> (and <code>hive.metastore.metrics.enabled</code>); reporters JMX and JSON file, scraped by Prometheus or similar.</li>
        <li>Logs: HiveServer2 log (log4j2), operation logs streamed to Beeline (<code>hive.server2.logging.operation.level</code>), historic operation logs, Tez/YARN task logs.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>Without metrics enabled, <code>/jmx</code> had 27 JVM beans and no <code>hs2_*</code>; with them, 122 beans including session, query and compile timers.</li>
        <li>The drilldown’s Performance Logging tab split a 3.9 s query into 0.71 s compile and 3.2 s execution; the Query Plan tab needed <code>hive.server2.webui.explain.output=true</code>.</li>
        <li><code>/conf</code> hid the database password, but <code>/jmx</code> printed it in the JVM arguments, with no login. Operation level VERBOSE sent 253 log lines to Beeline vs 118 at EXECUTION.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Monitoring HiveServer2</h2>
''' + def_block(
    '<b>Monitoring</b> HiveServer2 combines its built-in <b>web UI</b> (port 10002 by default), which lists active sessions, open and recently closed queries with per-query drilldowns (profile, stages, plan, performance log, operation log) and exposes configuration, thread dumps and JMX metrics; <b>metrics</b> (enabled with <code>hive.server2.metrics.enabled</code>) such as open sessions, submitted, succeeded and failed queries and compilation and execution timers, published through JMX or JSON reporters; and <b>logs</b>: the server log, per-operation logs returned to clients and optionally kept as historic logs, and the execution engine’s task logs, all correlated by the query ID.',
    'HiveServer2 has a web page that shows who is connected and what is running, numbers (metrics) that monitoring tools can collect, and logs that explain what happened to each query. Together they tell you whether the server, or one query, is the problem.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Web UI', 'HiveServer2’s built-in pages on port 10002.'),
    ('Drilldown', 'Per-query page: profile, stages, plan, perf log, operation log.'),
    ('JMX', 'Java Management Extensions: where metrics are exposed (/jmx).'),
    ('Metric', 'A count, gauge or timer, e.g. hs2_failed_queries.'),
    ('Operation log', 'Per-query log streamed to the client (Beeline INFO lines).'),
    ('Historic operation log', 'Operation logs kept on the server after a query ends.'),
    ('Query ID', 'hive_YYYYMMDDhhmmss_…: the key that links UI, logs and Tez.'),
    ('Thread dump', 'What every server thread is doing right now (/stacks).'),
]) + '''

  <h3>What to look at for which question</h3>
''' + table(['Question', 'Look at', 'Lab example'], [
    ['Who is connected? What runs now?', 'Web UI home: Active Sessions, Open Queries', '1 session, 1 RUNNING query'],
    ['Why was this query slow?', 'Drilldown: Performance Logging, Operation Log', 'compile 0.71 s, runTasks 3.2 s'],
    ['Is the server getting worse over days?', 'Metrics: hs2_* counters and timers, charted', 'hs2_executing_queries mean 21 s'],
    ['Why did it fail?', 'Operation log, server log by queryId, task logs', '“interrupted after 39.983 seconds”'],
    ['Is the server stuck?', '/stacks thread dump, JVM memory in /jmx', '63–75 threads; heap 147 MB of 1 GB'],
], minw=720) + lv + '''
EXAM> “How do you monitor HiveServer2?” Use the HS2 web UI (port 10002) for live sessions and queries with drilldowns, enable metrics (hive.server2.metrics.enabled) and scrape JMX into a monitoring system (open sessions, failed queries, latency), and correlate logs by query ID across the HS2 log, operation logs and Tez/YARN logs. Secure the UI.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Monitoring settings (Hive 4.2.1 lab)</h2>
''' + table(['Setting', 'Lab value', 'Purpose'], [
    ['<code>hive.server2.webui.port</code>', '10002', 'Web UI port (0 disables it)'],
    ['<code>hive.server2.webui.max.historic.queries</code>', '25', 'Closed queries kept in the UI'],
    ['<code>hive.server2.webui.explain.output</code>', 'false', 'Show EXPLAIN in the Query Plan tab'],
    ['<code>hive.server2.metrics.enabled</code>', 'false (we set true)', 'Publish hs2_* metrics'],
    ['<code>hive.server2.logging.operation.level</code>', 'EXECUTION', 'NONE · EXECUTION · PERFORMANCE · VERBOSE'],
    ['<code>hive.server2.historic.operation.log.enabled</code>', 'false (we set true)', 'Keep operation logs after a query'],
    ['<code>hive.server2.webui.use.spnego / use.pam / use.ssl</code>', 'false', 'Protect the web UI'],
    ['<code>hive.conf.hidden.list</code>', 'passwords …', 'Values hidden from /conf and SET'],
], minw=700) + '''
WARN> The web UI and <code>/jmx</code> have <b>no login</b> unless you enable SPNEGO or PAM, and they reveal queries, users and configuration. In our lab <code>/jmx</code> even showed the metastore password, because it was passed as a <code>-D</code> JVM argument. Restrict port 10002 to administrators, and keep secrets in <code>hive-site.xml</code> or a credential provider, never on the command line.
</section>
'''

FIGS = fig('ui-home.webp', 900, 1081, 'HiveServer2 web UI home page with one active session, one running query and four closed queries', 'Real screenshot: the HiveServer2 web UI of our lab while the 40-second query was running. One session, one open query, four closed ones (three FINISHED, one ERROR).') + fig('ui-perf.webp', 900, 825, 'Performance Logging tab of a query drilldown showing compile-time metadata calls and perf-logger timings', 'Real screenshot: the Performance Logging tab of a query’s drilldown: metastore calls and every compile phase with its time in milliseconds.')

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>A morning with the HiveServer2 web UI, metrics and logs</h2>
  <p>All outputs are real, from Hive 4.2.1. The lab maps HiveServer2’s port 10002 to the host; screenshots were taken with a headless browser.</p>
''' + FIGS + stepper([
    ('Step 1 · Who is connected, and what is running?',
     code('text', 'http://localhost:10002/  (page text)', "-- while SELECT COUNT(*) FROM orders_big_txt a JOIN orders_big_txt b … was running", capf('l103_home.txt')),
     'The home page lists <b>active sessions</b> (user, IP, operation count, active and idle time), <b>open queries</b> with state and a drilldown link, and the <b>last 25 closed queries</b> (<code>hive.server2.webui.max.historic.queries</code>) with their final state: FINISHED, ERROR, and later TIMEDOUT for our self-join, which hit a 40-second query timeout. This list lives in memory and is empty after a restart.'),
    ('Step 2 · Drill into one query',
     code('text', 'query_page.html?operationId=… · Performance Logging (selected rows)', "-- SELECT a.city, COUNT(*) AS pairs FROM orders a JOIN orders b ON … GROUP BY a.city", capf('l103_perf.txt')),
     'The 3.9-second query spent <b>0.71 s compiling</b> (702 ms semantic analysis, of which Calcite join-ordering transformations took about 360 ms) and <b>3.2 s running tasks</b>. The first rows are metastore calls during compilation (getTable 29 ms, column statistics 66 ms). This tab answers “was it planning or execution?” without reading any log. The Stages tab labelled the Tez stage <code>Stage-1:MAPRED</code>, an old name; the Query Plan tab said “Set configuration hive.server2.webui.explain.output to true to view future query plans”.'),
    ('Step 3 · Metrics are off until you switch them on',
     code('bash', 'host', "curl -s http://localhost:10002/jmx     # default configuration\n\n# restart HiveServer2 with -Dhive.server2.metrics.enabled=true\ncurl -s http://localhost:10002/jmx     # 122 beans now", capf('l103_jmx_before.txt')),
     'With the defaults of this image, <code>/jmx</code> had only <b>27 JVM beans</b> (heap 147 MB of 1,024 MB, garbage collection, threads) and <b>no hs2_* metrics</b>. After enabling <code>hive.server2.metrics.enabled</code> it published 122 beans, including HiveServer2’s own counters and timers. Most tutorials show the metric names but not that they may be disabled.'),
    ('Step 4 · The numbers after a small workload',
     code('bash', 'host', "# workload: 3 successful queries, 1 error (no_such_table), 1 query timed out after 40 s\ncurl -s http://localhost:10002/jmx | python3 -c '…select hs2_* and api_* beans…'", capf('l103_jmx_after.txt')),
     'Counters (<code>hs2_succeeded_queries 3</code>, <code>hs2_failed_queries 1</code>, <code>cumulative_connection_count 4</code>), gauges (<code>hs2_open_sessions 0</code> now) and timers: compilation averaged 0.59 s (max 1.58 s); execution averaged 21 s, pulled up by the 40-second timeout. A monitoring system scrapes these every minute and alerts on trends: rising failures, rising compile time (often a metastore problem), too many open sessions.'),
    ('Step 5 · Operation logs: what Beeline receives',
     code('sql', 'Beeline (--silent=false)', "SET hive.server2.logging.operation.level=NONE;       -- then EXECUTION, PERFORMANCE, VERBOSE\nSELECT city, COUNT(*) FROM customers GROUP BY city;", capf('l103_levels.txt')),
     'The INFO lines you see in Beeline (Lesson 8.4’s Tez summary, counters, Lesson 8.5’s errors) are the <b>operation log</b>. NONE sends nothing; EXECUTION is the default; VERBOSE doubled the volume to 253 lines. PERFORMANCE gave the same 118 lines as EXECUTION for this query. With <code>hive.server2.historic.operation.log.enabled=true</code> the server keeps a copy after the query ends.'),
    ('Step 6 · Follow one query through the server log',
     code('bash', 'host', "docker logs hiveserver2 | grep 'hive_20261029132307_55f4dbc1-…'      # in our Docker lab: stdout\n\n# the kept (historic) operation log of the same query, last lines:\ntail -2 /tmp/hive/operation_logs_historic/…/hive_20261029132307_55f4dbc1-…", capf('l103_qidlog.txt') + '\n\n' + capf('l103_hist.txt').split('\n', 1)[1]),
     'The <b>query ID</b> ties everything together: compile (0.466 s), execute, the Tez DAG and application ID, and the end, “interrupted after 39.983 seconds” (our query timeout). The historic operation log on disk ends with “FAILED: Operation cancelled”. In this Docker image the server log goes to the console (the UI’s Local logs page returned 404); on clusters it is a file such as <code>/var/log/hive/hiveserver2.log</code>.'),
    ('Step 7 · Noise, and how to cut through it',
     code('bash', 'host', "docker logs hiveserver2 | wc -l\ndocker logs hiveserver2 | grep -c 'compactor.Worker: Processing compaction request null'\ndocker logs hiveserver2 | grep -c 'hive_20261029132307_55f4dbc1-…'", capf('l103_noise.txt')),
     'In a few minutes the server log had <b>4,585 lines</b>, including a compaction worker announcing every ~11 seconds that it had nothing to do (Module 7’s compactor running inside HiveServer2). Only <b>32</b> lines belonged to the query we cared about. Search by query ID or session ID, ship logs to a central system (ELK, Splunk, Loki), and tune noisy loggers through the UI’s Configure logging page or log4j2.'),
    ('Step 8 · What the UI reveals: a security check',
     code('bash', 'host · no login', "curl -s http://localhost:10002/conf | grep -c hivepw          # the configuration page\ncurl -s http://localhost:10002/conf | grep hive.conf.hidden.list\ncurl -s http://localhost:10002/jmx  | … Runtime InputArguments …   # the metrics page", capf('l103_conf.txt') + ' …\n\n' + capf('l103_leak.txt')),
     'The configuration page correctly <b>hides</b> the metastore password (<code>hive.conf.hidden.list</code>). But the metastore password reached HiveServer2 as a <code>-D</code> JVM argument, and <code>/jmx</code> lists all JVM arguments: anyone who can open port 10002 can read it. Fix: keep secrets in <code>hive-site.xml</code> or a Hadoop credential provider (<code>hadoop.security.credential.provider.path</code>), enable SPNEGO/PAM and TLS on the UI, and firewall the port.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('Active Sessions: hive 127.0.0.1  1 op', W), ('Open Queries: … orders_big_txt … RUNNING', Y), ('Closed: FINISHED · ERROR · FINISHED · FINISHED', W), ('later: TIMEDOUT after 40 s', RD)], size=7.2),
    term([('compile                    710 ms', W), ('semanticAnalyze            702 ms', W), ('Calcite Postjoin ordering  191 ms', W), ('runTasks                  3200 ms', G)], size=7.4),
    term([('/jmx default: 27 beans, no hs2_*', RD), ('metrics.enabled=true: 122 beans', G), ('hs2_succeeded_queries   3', G), ('hs2_failed_queries      1', Y), ('api_compile mean 0.59 s', W)], size=7.4),
    term([('grep <queryId>: 32 of 4,585 lines', G), ('compactor.Worker … null: 21 lines', Y), ('… interrupted after 39.983 seconds', RD), ('FAILED: Operation cancelled', RD)], size=7.2),
    term([('/conf: password hidden (0 hits)', G), ('/jmx InputArguments:', W), ('-Djavax.jdo.option.Connection', RD), ('  Password=hivepw', RD)], size=7.4),
]
def layers(hi):
    o = ''
    for k, (a, b, tone) in enumerate([('Web UI', 'now', 'blue'), ('Metrics', 'trends', 'violet'), ('Logs', 'details', 'green')]):
        o += opbox(20 + k * 112, 54, a, b, 'acc' if k == hi else tone, 100, 30)
    return o
B1 = [
    t(180, 22, 'The UI shows the present', 9.4, bold=True) + layers(0) + t(180, 112, 'sessions · open and recent queries', 8, 'ink2', mono=True) + cap('In memory: gone after a restart.', '', 'blue', y=140, h=34),
    t(180, 22, 'Drilldown: planning or execution?', 9.4, bold=True) + layers(0) + fill(40, 104, 40, 10, 'violet', rx=2) + fill(80, 104, 180, 10, 'green', rx=2) + t(60, 128, 'compile', 7, 'ink2', mono=True) + t(170, 128, 'runTasks', 7, 'ink2', mono=True) + cap('0.71 s vs 3.2 s in our query.', '', 'green', y=140, h=34),
    t(180, 22, 'Metrics show trends', 9.4, bold=True) + layers(1) + t(180, 112, 'counters · gauges · timers via JMX', 8, 'ink2', mono=True) + cap('Off by default in this build.', '', 'amber', y=140, h=34),
    t(180, 22, 'Logs explain one event', 9.4, bold=True) + layers(2) + t(180, 112, 'filter by query ID', 8, 'ink2', mono=True) + cap('Ship logs to a central search system.', '', 'green', y=140, h=34),
    t(180, 22, 'Monitoring endpoints are sensitive', 9.4, bold=True) + layers(1) + cap('Authenticate the UI; no secrets in -D flags.', '', 'amber', y=140, h=34),
]
see_caps = ['The home page showed a running query and recent ones.',
            'The drilldown split a query into compile and run time.',
            'Metrics appeared only after enabling them.',
            'One query ID found 32 relevant lines among thousands.',
            '/jmx exposed a password that /conf hid.']
behind_caps = ['HiveServer2 keeps live and recent operations in memory.',
               'The perf logger times every phase of each query.',
               'Metric reporters publish counters and timers through JMX.',
               'Every log line of a query carries its ID.',
               'JMX lists JVM arguments verbatim.']
two = anim_two('Monitoring', 'Now, trends and details', 'Real lab outputs', 'What each layer tells you', see, B1, see_caps, behind_caps)

# ---- scenario 1: everything slow
e1 = (t(180, 22, '10:00 · “Everything is slow”', 9.4, bold=True) + t(180, 56, 'is it the server or a few queries?', 8.4, 'ink2') + cap('Start with the web UI.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Open Queries: 60 RUNNING', 9.4, bold=True) + t(180, 56, 'normally 10; one user has 40 of them', 8.2, 'red') + cap('A scheduled job gone wrong.', '', 'amber', y=150, h=34))
e3 = (t(180, 22, 'Drilldown one of them', 9.4, bold=True) + t(180, 56, 'compile 0.5 s · runTasks 20 min', 8.2, 'ink', mono=True) + cap('Execution, not planning.', '', 'blue', y=150, h=34))
e4 = (t(180, 22, 'Act', 9.4, bold=True) + t(180, 56, "KILL QUERY 'id' · contact the owner", 8.2, 'ink', mono=True) + cap('Lesson 8.5 tools.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Prevent', 9.4, 'acc', bold=True) + t(180, 56, 'alert: open queries per user · query timeouts', 8, 'ink2') + cap('Metrics turn incidents into alerts.', '', 'green', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Is it the server or one user?',
              'A typical triage with the web UI. (Numbers illustrative; pages as in our lab.)',
              'Server triage', 'The web UI showed one user’s runaway job; the drilldown located the time in execution; the queries were killed and alerts added', [e1, e2, e3, e4, e5],
              ['Users report slowness.',
               'Open Queries reveals a runaway job.',
               'Drilldown shows where time goes.',
               'Kill and inform.',
               'Alert next time.'],
              hid='scenario-triage')

# ---- scenario 2: dashboards and alerts
m1 = (t(180, 22, 'Build a Hive dashboard', 9.4, bold=True) + t(180, 56, 'for the platform on-call team', 8.4, 'ink2') + cap('Metrics, not screenshots.', '', 'blue', y=150, h=34))
m2 = (t(180, 22, 'Enable and export', 9.4, bold=True) + t(180, 56, 'metrics.enabled=true → JMX → Prometheus exporter', 7.8, 'ink', mono=True) + cap('Scrape every 30–60 s.', '', 'green', y=150, h=34))
m3 = (t(180, 22, 'Charts', 9.4, bold=True) + t(180, 56, 'open sessions · executing queries · failed rate · compile p95', 7.4, 'ink2', mono=True) + cap('Plus JVM heap and GC time.', '', 'green', y=150, h=34))
m4 = (t(180, 22, 'Alerts', 9.4, bold=True) + t(180, 56, 'failed rate > 5% · heap > 85% · HMS errors', 8, 'ink2') + cap('Page someone only for real trouble.', '', 'amber', y=150, h=34))
m5 = (t(180, 22, 'Same for the metastore', 9.4, 'acc', bold=True) + t(180, 56, 'hive.metastore.metrics.enabled', 8.2, 'ink2', mono=True) + cap('Its latency affects every engine.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'A monitoring dashboard for Hive',
              'Turning metrics into dashboards and alerts. (Typical setup; metric names from our lab.)',
              'Metrics pipeline', 'Enable HiveServer2 and metastore metrics, scrape JMX, chart key counters and timers, and alert on failure rates and memory', [m1, m2, m3, m4, m5],
              ['The team needs a dashboard.',
               'Enable metrics and scrape JMX.',
               'Chart the key series.',
               'Alert on real problems.',
               'Include the metastore.'],
              hid='scenario-dashboard')

# ---- scenario 3: securing the UI
u1 = (t(180, 22, 'Security scan finds port 10002 open', 9.4, bold=True) + t(180, 56, 'no login, reachable from the office network', 8.2, 'red') + cap('As in our Step 8.', '', 'amber', y=150, h=34))
u2 = (t(180, 22, 'Remove secrets from the command line', 9.4, bold=True) + t(180, 56, 'hive-site.xml (600) or a credential store', 8.2, 'ink2') + cap('JMX shows JVM arguments.', '', 'green', y=150, h=34))
u3 = (t(180, 22, 'Authenticate the UI', 9.4, bold=True) + t(180, 56, 'webui.use.spnego (Kerberos) or use.pam', 8.2, 'ink', mono=True) + cap('Plus webui.use.ssl.', '', 'green', y=150, h=34))
u4 = (t(180, 22, 'Network', 9.4, bold=True) + t(180, 56, 'only admin hosts and the monitoring scraper', 8.2, 'ink2') + cap('Firewall or security groups.', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'Re-test', 9.4, 'acc', bold=True) + t(180, 56, 'curl /jmx /conf as an outsider', 8.2, 'ink2') + cap('Verify, do not assume.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Locking down the web UI',
              'Remediating the exposure we found. (Typical hardening steps.)',
              'UI hardening', 'Remove secrets from JVM arguments, authenticate and encrypt the web UI, restrict the network, and re-test', [u1, u2, u3, u4, u5],
              ['The UI is open to everyone.',
               'Move secrets out of -D flags.',
               'Require authentication and TLS.',
               'Restrict network access.',
               'Test again from outside.'],
              hid='scenario-harden')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Now, trends and details</h2>
  <p>Left: real outputs. Right: what each monitoring layer tells you.</p>
''' + two + '''
  <p>Three live scenarios follow: server triage, a metrics dashboard, and locking down the UI.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Monitoring at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'on-call', 11, 'green', bold=True) + t(60, 58, 'triage', 7.4, 'ink2'),
    '1. On-call triage',
    'The web UI’s open queries and drilldowns are the first stop when users report slowness.',
    ['Complaint', '*web UI', 'Cause']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'SLOs', 12, 'blue', bold=True) + t(60, 58, 'dashboards', 7.4, 'ink2'),
    '2. Service levels',
    'Query success rate and latency percentiles from metrics are reported against agreed service levels.',
    ['Metrics', '*dashboard', 'SLO report']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'capacity', 10, 'violet', bold=True) + t(60, 58, 'planning', 7.4, 'ink2'),
    '3. Capacity planning',
    'Trends in sessions, concurrent queries and heap use show when to add HiveServer2 instances.',
    ['Trends', '*forecast', 'More servers']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'logs', 12, 'acc', bold=True) + t(60, 58, 'central', 7.4, 'ink2'),
    '4. Central log search',
    'HiveServer2, metastore and Tez logs are shipped to ELK, Splunk or Loki and searched by query ID.',
    ['Logs', '*search', 'Root cause']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'audit', 11, 'acc', bold=True) + t(60, 58, 'security', 7.4, 'ink2'),
    '5. Security reviews',
    'Monitoring endpoints are checked in security scans, since they reveal queries, users and configuration.',
    ['Scan', '*hardening', 'Closed ports']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> troubleshooting queries (<a href="../../08-optimisation/05-troubleshooting-slow-queries/">8.5</a>), security (<a href="../02-authorization-and-security/">10.2</a>) and the metastore (<a href="../01-metastore-administration/">10.1</a>).</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
