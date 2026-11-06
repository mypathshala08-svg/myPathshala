import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from hivekit import tables
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return re.sub(r'; Query ID[^\n]*', '', open(CAP + n).read().rstrip())
BODY = body(HERE)

META = dict(
    module='10-administration-and-security', lesson='03-monitoring-and-logs', n='10.3',
    module_label='Module 10 · Administration and security',
    title='Monitoring, logs and the HiveServer2 web UI',
    desc='Monitor HiveServer2 with real Hive 4.2.1 outputs and screenshots: the web UI on port 10002 (sessions, open and closed queries, drilldowns with performance logging), enabling metrics and reading hs2_* counters and timers from /jmx, operation log levels, following a query ID through the server log and historic operation logs, log noise, thread dumps, and a security check where /jmx exposed a password that /conf hid.',
    og_desc='Real screenshots of the HiveServer2 web UI, metrics that were off by default, and a password the metrics page revealed. Monitoring Hive 4.2.1.',
    minutes=35, level='Intermediate → Advanced',
    lead='The last lesson of Module 10 looks at HiveServer2 from the operator’s chair: its <b>web UI</b>, its <b>metrics</b> and its <b>logs</b>. We run a small workload with a success, an error and a timeout, then read it back through each layer, with real screenshots, and finish with a security check that found a real exposure. <b>All outputs are real</b>, from Hive 4.2.1.',
    chips=['Real web UI screenshots', 'Metrics before and after', 'One query ID, all the logs', 'Runs in your browser (Python)'],
)

MAIN = '''# Read HiveServer2 metrics like a monitoring system (values from the lab)
metrics = {"hs2_succeeded_queries": 3, "hs2_failed_queries": 1, "hs2_open_sessions": 0,
           "api_compile_mean_s": 0.59, "hs2_executing_queries_mean_s": 21.04}

total = metrics["hs2_succeeded_queries"] + metrics["hs2_failed_queries"]
failure_rate = metrics["hs2_failed_queries"] / total
print(f"queries: {total}, failure rate: {failure_rate:.0%}")

alerts = []
if failure_rate > 0.05:
    alerts.append("failure rate above 5%")
if metrics["api_compile_mean_s"] > 2:
    alerts.append("slow compilation: check the metastore")
print("alerts:", alerts or "none")
'''
RUN = dict(
    heading='Run the code: from metrics to alerts',
    intro='<p>These programs turn the lab’s metrics and logs into the checks a monitoring system runs. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('failure_rate = metrics["hs2_failed_queries"] / total', 'Counters only grow; real systems compare increases over a time window, not totals since start.'),
        ('if metrics["api_compile_mean_s"] > 2:', 'Rising compile time often points at the metastore (Lesson 10.1), not the cluster.'),
    ],
    tasks=[
        dict(label='1 · Failure rate', hint='Press <b>Run</b>. 1 of 4 queries failed in our tiny workload: 25%, which would alert.', code=None),
        dict(label='2 · Predict first: rate over a window', hint='<b>Predict first:</b> counters were 3/1 at 10:00 and 103/2 at 10:05. What is the failure rate in those five minutes?',
             code='''before = {"ok": 3, "fail": 1}
after = {"ok": 103, "fail": 2}
d_ok, d_fail = after["ok"] - before["ok"], after["fail"] - before["fail"]
print(f"{d_fail / (d_ok + d_fail):.1%} in the window")
'''),
        dict(label='3 · Filter a log by query ID', hint='Keep only lines of one query, like the grep in Step 6.',
             code='''log = ["13:21:21 compactor.Worker: Processing compaction request null",
       "13:23:07 Driver: Compiling command(queryId=hive_A)",
       "13:23:07 Driver: Executing command(queryId=hive_A)",
       "13:23:10 compactor.Worker: Processing compaction request null",
       "13:23:47 Driver: Executing command(queryId=hive_A) has been interrupted after 39.983 seconds"]
for line in log:
    if "hive_A" in line:
        print(line)
'''),
        dict(label='4 · Compile or execute?', hint='Split a query’s time like the Performance Logging tab did.',
             code='''compile_ms, run_ms = 710, 3200
total = compile_ms + run_ms
print(f"compile {compile_ms / total:.0%} · execute {run_ms / total:.0%}")
'''),
        dict(label='5 · Spot the error', hint='This check scans JVM arguments for secrets but misses the real one. Fix the pattern.', expect='error',
             code='''args = ["-Xmx1G", "-Dhive.metastore.uris=thrift://metastore:9083", "-Djavax.jdo.option.ConnectionPassword=hivepw"]
leaks = [a for a in args if "secret" in a.lower()]          # bug
assert leaks, "search for 'password' (case-insensitive): the lab leaked ConnectionPassword"
print(leaks)
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: query profile, stages and threads',
    intro='<p>More pages of the HiveServer2 web UI in our lab. <b>Outputs are real</b>.</p>',
    items=[
        dict(title='1 · Base Profile of a query', cmd='http://localhost:10002/query_page.html?operationId=…   (Base Profile tab)', file='browser',
             output=capf('l103_profile.txt'),
             note='The query ID here is the same key used in the logs and in Tez. “Opened” is the time since the operation was opened; “Latency” is execution time.'),
        dict(title='2 · Stages and Query Plan tabs', cmd='Stages tab · Query Plan tab', file='browser',
             output=capf('l103_stages.txt'),
             note='The Tez stage is still labelled MAPRED. To see plans here, set hive.server2.webui.explain.output=true (it applies to future queries).'),
        dict(title='3 · Thread dump', cmd='curl -s http://localhost:10002/stacks | head\n# most frequent thread names', file='host',
             output=capf('l103_stacks.txt').split('\n  State')[0] + '\n…\n\n' + capf('l103_threads.txt'),
             note='When HiveServer2 hangs, two thread dumps a few seconds apart show which threads are stuck and where (for example waiting on the metastore). Our idle server had about 60 threads.'),
    ],
)

TRACE = dict(
    heading='One query through the monitoring layers',
    intro='<p>Follow the timed-out self-join through the UI, metrics and logs.</p>',
    code='''qid = "hive_20261029132307_55f4dbc1"
ui_state = "RUNNING"                        # web UI, Open Queries
ui_state = "TIMEDOUT"                       # Closed Queries after 40 s
metric_max_exec_s = 39.98                   # hs2_executing_queries max
log_line = "interrupted after 39.983 seconds"
print(qid, ui_state, metric_max_exec_s, log_line)
''',
    notes={2: 'Now :: The UI showed it live with a drilldown link.', 4: 'Trend :: The timer’s max came from this query.', 5: 'Detail :: The server log and historic operation log explain it.'},
)

WORKED_INTRO = 'Three monitoring tasks from real platform teams.'
EXAMPLES = [
    dict(level='b', tag='Operations · triage', title='Read the home page',
         problem='<p>From the web UI home page, decide whether the problem is the server or one query.</p>',
         inp='1 active session, 1 open query RUNNING for 16 s, recent queries 1–6 s',
         approach=['Few sessions and queries → server not overloaded.', 'One long query → drill into it.', 'Many queries from one user → runaway job.'],
         code='''sessions, open_queries, longest_open_s, recent_max_s = 1, 1, 16, 6
if open_queries > 50:
    print("server overloaded: check users and capacity")
elif longest_open_s > 5 * recent_max_s:
    print("one slow query: open its drilldown")
else:
    print("looks normal")
''', notes={4: 'Ratio :: 16 s against a recent maximum of 6 s points at one query.'},
         tryit='It was our deliberate self-join, which then timed out at 40 s.'),
    dict(level='i', tag='Platform · metrics', title='Choose what to chart',
         problem='<p>Pick six series for a HiveServer2 dashboard and the reason for each.</p>',
         inp='metric names from /jmx in the lab',
         approach=['Load: sessions and executing queries.', 'Health: failures.', 'Latency: compile and execution timers.'],
         code='''series = {"hs2_open_sessions": "connection load",
          "hs2_executing_queries (count)": "concurrency",
          "hs2_failed_queries (rate)": "errors",
          "api_compile (p95)": "planning / metastore health",
          "hs2_executing_queries (p95)": "user-facing latency",
          "java.lang:Memory HeapMemoryUsage": "memory pressure"}
for k, v in series.items():
    print(f"{k:34} {v}")
''', notes={5: 'Percentiles :: Means hide the slow tail; dashboards use p95/p99.'},
         tryit='All of these names appeared in our /jmx once metrics were enabled.'),
    dict(level='a', tag='Security · hardening', title='Audit monitoring endpoints',
         problem='<p>List the checks for a HiveServer2 security review of port 10002.</p>',
         inp='findings from Step 8',
         approach=['Authentication on the UI.', 'No secrets in JVM arguments.', 'Network restrictions and TLS.'],
         code='''checks = [
  ("UI requires login (SPNEGO/PAM)", False),
  ("no passwords in -D JVM arguments", False),
  ("/conf hides secrets (hive.conf.hidden.list)", True),
  ("TLS on the UI", False),
  ("port 10002 reachable only from admin/monitoring hosts", False)]
for c, ok in checks:
    print("PASS" if ok else "FAIL", c)
''', notes={4: 'Partial :: Hiding in /conf is not enough if /jmx shows the same value.'},
         tryit='Our lab fails four of five checks: fine for learning, never for production.'),
]

QUIZ = mix([
    dict(q='Beginner: On which port does the HiveServer2 web UI listen by default?', options=['10000', '10002', '9083', '8088'], answer=1,
         why='10000 is JDBC, 9083 the metastore, 8088 the YARN UI.'),
    dict(q='Beginner: What does the web UI home page show?', options=['Only configuration', 'Active sessions, open queries and recently closed queries', 'HDFS files', 'Metastore tables'], answer=1,
         why='With a drilldown link for each query.'),
    dict(q='Beginner: What links UI, logs and Tez for one query?', options=['The user name', 'The query ID', 'The table name', 'The port'], answer=1,
         why='hive_YYYYMMDDhhmmss_….'),
    dict(q='Intermediate: Why did /jmx show no hs2_* metrics at first?', options=['Wrong URL', 'hive.server2.metrics.enabled was false', 'JMX is disabled in Hive 4', 'No queries had run'], answer=1,
         why='27 JVM beans before, 122 beans after enabling metrics.'),
    dict(q='Intermediate: Which drilldown tab splits compile and execution time?', options=['Stages', 'Performance Logging', 'Base Profile', 'Query Plan'], answer=1,
         why='compile 710 ms, runTasks 3200 ms in our query.'),
    dict(q='Intermediate: What does the operation log level (hive.server2.logging.operation.level) control?', options=['Server log file size', 'How many log lines are sent to the client per query', 'Metrics', 'Audit'], answer=1,
         why='NONE 0, EXECUTION 118, VERBOSE 253 lines in our test.'),
    dict(q='Advanced: Why did /jmx reveal the metastore password while /conf did not?', options=['A bug in /conf', 'The password was a -D JVM argument, and JMX lists JVM arguments', 'Metrics store passwords', 'TLS was off'], answer=1,
         why='Keep secrets in hive-site.xml or a credential provider; protect the UI.'),
    dict(q='Advanced: The server log had 4,585 lines; how many belonged to our query?', options=['All', '32', '0', '4,000'], answer=1,
         why='Filter by query ID; ship logs to a central search system.'),
])

REVISION = [
    '<b>Web UI</b> :10002: sessions, open queries, last 25 closed queries (in memory), drilldown per query.',
    'Drilldown tabs: Base Profile, Stages, Query Plan (needs <code>hive.server2.webui.explain.output</code> = true), Performance Logging, Operation Log.',
    '<b>Metrics</b>: <code>hive.server2.metrics.enabled</code> = true → hs2_* counters, gauges, timers in <code>/jmx</code> (27 → 122 beans in lab).',
    'Key series: open sessions, executing queries, failed rate, compile and execution percentiles, heap.',
    '<b>Operation logs</b>: operation log level (<code>hive.server2.logging.operation.level</code>): NONE · EXECUTION · PERFORMANCE · VERBOSE; historic logs optional.',
    '<b>Server log</b>: log4j2 (console in Docker, file on clusters); filter by query ID; ship centrally; tune noisy loggers.',
    '<code>/stacks</code> for hangs; <code>/conf</code> hides <code>hive.conf.hidden.list</code> values.',
    '<b>Secure</b> the UI (SPNEGO/PAM, TLS, firewall); never pass secrets as -D flags (/jmx showed one).',
]
FAQ = [
    ('Is there a metastore web UI?', 'Not like HiveServer2’s. The metastore publishes metrics through JMX when <code>hive.metastore.metrics.enabled</code> (or <code>metastore.metrics.enabled</code>) is true, and logs to its own log. Monitor its call latency and error counts, since every engine depends on it.'),
    ('Where are Tez task logs?', 'On a YARN cluster: the YARN ResourceManager UI (port 8088) and <code>yarn logs -applicationId application_…</code>, or the Tez UI if installed. The application ID appears in the HiveServer2 log line “Submitting dag to TezSession … applicationId=…”. In our local-mode lab tasks log into HiveServer2’s own output.'),
    ('How long are closed queries kept in the UI?', 'The last <code>hive.server2.webui.max.historic.queries</code> (25) operations, in memory only. For history, keep historic operation logs, central logs, or a distribution’s query history service.'),
    ('Can I change log levels without a restart?', 'Yes: the UI’s “Configure logging” page and log4j2’s automatic reconfiguration let you raise a single logger (for example the metastore client) to DEBUG temporarily. Remember to set it back.'),
    ('What about Prometheus?', 'Hive does not ship a Prometheus endpoint itself; teams use the JMX exporter agent on the HiveServer2 JVM, or scrape /jmx and convert. Managed services (Cloudera, cloud providers) export metrics to their own monitoring.'),
]

PRACTICE_INTRO = 'Programs for monitoring checks, with the commands in each explanation.'
PROBLEMS = [
    dict(level='easy', title='Compile share', stmt='What share of the query was compilation?', inp='710 ms compile, 3,200 ms execution',
         code='''print(f"{710 / (710 + 3200):.0%}")
''', explain='18%: execution dominated, so plan reading (8.1) and execution tuning (8.4) are the next steps.'),
    dict(level='easy', title='Signal to noise', stmt='What share of log lines belonged to our query?', inp='32 of 4,585',
         code='''print(f"{32 / 4585:.2%}")
''', explain='0.70%: filter by query ID.'),
    dict(level='easy', title='Bean growth', stmt='How many beans did enabling metrics add?', inp='27 → 122',
         code='''print(122 - 27)
''', explain='95 HiveServer2 metric beans: counters, gauges and timers.'),
    dict(level='medium', title='Extract the query ID', stmt='Pull the query ID out of a log line.', inp='a real log line',
         code='''import re
line = "ql.Driver: Executing command(queryId=hive_20261029132307_55f4dbc1-e79b-48bd-8757-20647193bf39) has been interrupted after 39.983 seconds"
print(re.search(r"queryId=(hive_[0-9_a-f-]+)", line).group(1))
''', explain='Then: docker logs hiveserver2 | grep &lt;id&gt;, or search it in your log system.'),
    dict(level='medium', title='Heap alert', stmt='Alert when heap use exceeds 85% of max.', inp='147 MB of 1,024 MB',
         code='''used, mx = 147, 1024
print(f"{used / mx:.0%}", "ALERT" if used / mx > 0.85 else "ok")
''', explain='From java.lang:type=Memory HeapMemoryUsage in /jmx.'),
    dict(level='medium', title='Find secrets in arguments', stmt='Scan JVM arguments for anything password-like.', inp='arguments list',
         code='''args = ["-Xmx1G", "-Djavax.jdo.option.ConnectionPassword=hivepw", "-Dhive.server2.metrics.enabled=true"]
print([a.split("=")[0] for a in args if "password" in a.lower()])
''', explain='Print only the names, never the values, in reports.'),
    dict(level='business', title='Mean time to diagnose', stmt='Grepping files on 4 servers takes 20 minutes; central search takes 2. Saving over 30 incidents a year?', inp='illustrative',
         code='''print((20 - 2) * 30 / 60, "hours per year")
''', explain='9 hours of on-call time, plus faster recovery for users.'),
    dict(level='business', title='Retention', stmt='Logs of 4,585 lines in a few minutes. Estimate daily lines for one server.', inp='lab rate (illustrative extrapolation)',
         code='''lines, minutes = 4585, 5
print(round(lines / minutes * 60 * 24), "lines per day")
''', explain='About 1.3 million lines a day from a nearly idle lab server: budget log storage and tune noisy loggers.'),
]

SCN_INTRO = 'Monitoring questions check whether you can find problems before users do.'
SCENARIOS = (
    scn('Any company · Hive', 'Fresher', '“How do you see running Hive queries?”',
        'Explain how to find what is running on HiveServer2.',
        'do you know the web UI and commands?',
        '<p>Open the HiveServer2 web UI on port 10002: it lists active sessions, open queries with state and elapsed time, and recent closed queries, each with a drilldown. From Beeline, Hive 4 also has SHOW PROCESSLIST, and KILL QUERY to stop one.</p>', 'Only mentioning YARN.') +
    scn('Data platform', 'Mid-level', 'Users say Hive is slow',
        'Several users report slowness at the same time.',
        'can you separate server and query problems?',
        '''<ol>
          <li>Web UI: count open queries and sessions; look for one user or job with many queries.</li>
          <li>Metrics: compare executing queries, compile time and heap with normal days.</li>
          <li>Drill into the slowest query (compile vs execute), then logs by query ID.</li>
        </ol>''', 'Restarting HiveServer2 first.') +
    scn('Operations', 'Mid-level', 'Monitoring from zero',
        'There is no monitoring for HiveServer2. What do you set up first?',
        'can you prioritise?',
        '''<ul>
          <li>Enable HiveServer2 and metastore metrics; scrape JMX; chart sessions, failures, latency, heap.</li>
          <li>Central logs with query IDs; alerts on failure rate and memory.</li>
          <li>Secure the web UI; remove secrets from JVM arguments.</li>
        </ul>''', 'Only reading logs after complaints.') +
    scn('Architecture', 'Senior', 'Observability for a shared platform',
        'Design observability for Hive, the metastore and Tez on a 500-user platform.',
        'can you design end to end?',
        '''<ul>
          <li>Metrics: JMX exporters on HS2 and HMS, dashboards with percentiles, SLOs per user group.</li>
          <li>Logs: central search with query, session and application IDs; retention and noise control.</li>
          <li>Traces: query ID propagated to Tez/YARN; audit from Ranger; locked-down UIs.</li>
        </ul>''', 'One dashboard with CPU only.')
)
