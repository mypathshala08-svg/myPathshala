import os
HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.dirname(HERE)
BODY = body(HERE)
rd = lambda f: open(os.path.join(UP, f)).read()

META = dict(
    module='12-multiple-clusters-and-operations', lesson='04-monitoring-and-alerts', n='12.4',
    module_label='Module 12 · Multiple clusters and operations',
    title='Monitoring and alerts',
    desc='Monitor Hadoop clusters with real metrics: a 60-line Python monitor reads NameNode JMX and the YARN REST API of two Hadoop 3.5.0 clusters, then we break them on purpose. A stopped DataNode raised a stale alert only after 296 s (metric lag), replication 4 on 3 DataNodes, safe mode on DR, a job stuck behind the AM limit, and 7 under-replicated job staging files that never clear (a real false alert). What to monitor in HDFS and YARN, Prometheus and Grafana, alert design with durations, severities and runbooks, canary jobs. Python rule engine, quiz and interview scenarios.',
    og_desc='We broke two Hadoop clusters on purpose and watched a tiny monitor catch it: one alert came 5 minutes late, one never went away.',
    minutes=28, level='Intermediate',
    lead='A cluster fails quietly unless something is watching. This lesson builds a small monitor over the metrics every Hadoop daemon already publishes, breaks a real cluster in four ways, and uses what we saw, including a late alert and a false one, to design alerts that people trust.',
    chips=['Real monitor on 2 clusters', 'Late and false alerts caught live', 'Runs in your browser (Python)'],
)

RUN = dict(
    heading='An alert rule engine over real snapshots',
    intro='<p>These snapshots are the prod numbers our monitor printed during the lab, one per check. The engine applies the same rules as <code>monitor.py</code>, plus one improvement: a rule can require its condition to hold for several checks in a row before it fires.</p>',
    code='''snapshots = [   # prod, from tx124 (time, stale DataNodes, under-replicated blocks, pending apps)
    ("10:21:11", 0, 0, 0), ("10:26:08", 1, 0, 0), ("10:26:16", 1, 1, 0),
    ("10:26:17", 1, 1, 0), ("10:26:52", 1, 8, 1), ("10:31:08", 0, 7, 0),
]
rules = [   # (name, test, checks in a row needed, severity)
    ("stale DataNode", lambda s: s[1] > 0, 1, "WARN"),
    ("under-replicated", lambda s: s[2] > 0, 1, "WARN"),
    ("app waiting", lambda s: s[3] > 0, 1, "WARN"),
]
streak = {name: 0 for name, _, _, _ in rules}
for snap in snapshots:
    fired = []
    for name, test, need, sev in rules:
        streak[name] = streak[name] + 1 if test(snap) else 0
        if streak[name] >= need:
            fired.append(f"{sev} {name}")
    print(snap[0], fired or "ok")
''',
    anno=[
        ('    ("stale DataNode", lambda s: s[1] > 0, 1, "WARN"),', 'Each rule is a test on one snapshot plus how many checks in a row it must hold. 1 = fire at once.'),
        ('        streak[name] = streak[name] + 1 if test(snap) else 0', 'A streak counter per rule: the basis of “for 5 minutes” rules in Prometheus and other tools.'),
        ('    ("10:21:11", 0, 0, 0), ("10:26:08", 1, 0, 0), ("10:26:16", 1, 1, 0),', 'Real values from our run. The stale DataNode appeared at 10:26:08, 296 s after the stop.'),
    ],
    tasks=[
        dict(label='1 · Run the rules', hint='Press <b>Run</b>. Which alert is still firing at 10:31:08, after everything was fixed?', code=None),
        dict(label='2 · Add a duration', hint='<b>Predict first:</b> make “app waiting” need 2 checks in a row. Does it still fire?',
             code='''snapshots = [("10:21:11", 0), ("10:26:17", 0), ("10:26:52", 1), ("10:31:08", 0)]   # (time, pending apps)
need, streak = 2, 0
for t, pending in snapshots:
    streak = streak + 1 if pending > 0 else 0
    print(t, "WARN app waiting" if streak >= need else "ok")
'''),
        dict(label='3 · Severity by count', hint='One dead DataNode is a WARN; three or more is CRIT (a rack may be gone). Write the function.',
             code='''def severity(dead):
    if dead == 0:
        return "ok"
    return "CRIT" if dead >= 3 else "WARN"
for d in [0, 1, 3]:
    print(d, "dead ->", severity(d))
'''),
        dict(label='4 · How late is the alert?', hint='A DataNode is stale after 30 s, the stale count is refreshed every 300 s, and we scrape every 15 s. What is the worst-case delay?',
             code='''stale_after, recount_every, scrape_every = 30, 300, 15
worst = stale_after + recount_every + scrape_every
print("worst case:", worst, "s   our lab:", 296, "s")
'''),
        dict(label='5 · Spot the error', hint='This rule computes disk use from the JMX numbers but crashes on a new cluster that reports no capacity yet. Guard against it.',
             code='''jmx = {"CapacityUsed": 0, "CapacityTotal": 0}
used = 100 * jmx["CapacityUsed"] / jmx["CapacityTotal"]
print(f"{used:.1f}% used")
''', expect='error'),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run it on your PC: a monitor for two clusters, and four incidents',
    intro='<p>You need the Module 8 lab (prod) and the Lesson 7.2 federation lab (dr) running, with the lab8 workers joined to the dr network as in Lesson 12.2 (<code>join_clusters.sh</code>). <code>monitor.py</code> runs on <code>lab8-worker1-1</code> because that machine can reach both clusters. The lab script stops a DataNode, changes replication, enters safe mode, starts two big jobs, then undoes everything. It takes about 15 minutes, mostly waiting for the stale count to refresh.</p>',
    items=[
        dict(title='The monitor', file='monitor.py',
             cmd=rd('lab/monitor.py') + '\n# Copy it to the worker and run one check:\n#   docker cp monitor.py lab8-worker1-1:/tmp/monitor.py\n#   docker exec lab8-worker1-1 python3 /tmp/monitor.py 1',
             output=rd('tx124.txt').strip().split('== 1.')[0].strip(),
             note='Real output of one check on a healthy fleet. Each line is one cluster; ALERT lines appear only when a rule fires.'),
        dict(title='Break the clusters and watch', file='monitor_lab.sh',
             cmd=rd('lab/monitor_lab.sh') + '\n# Run on your PC, in the folder that has monitor.py:\n#   bash monitor_lab.sh',
             output=rd('tx124.txt').strip(),
             note='Real output. Your delays will differ: the stale count depends on where the NameNode is in its 5-minute heartbeat check when the DataNode stops. The 7 under-replicated blocks at the end are staging files of the killed jobs; delete /tmp/hadoop-yarn/staging/hadoop/.staging/* (when no job is running) to clear them.'),
    ],
)

TRACE = dict(
    heading='A “for 3 checks” rule step by step',
    intro='<p>Watch the streak counter grow and reset. The rule fires only when the condition held for 3 checks in a row, so one bad reading is ignored.</p>',
    code='''values = [91, 85, 92, 93, 94, 88]
need = 3
streak = 0
for v in values:
    streak = streak + 1 if v > 90 else 0
    print(v, "ALERT" if streak >= need else "ok")
''',
    notes={5: 'Streak :: Grows while the value is above 90, resets to 0 on a good reading.',
           6: 'Fire :: Only the 3rd high reading in a row (94) fires.'},
)

WORKED_INTRO = 'Four monitoring problems from different domains: designing thresholds, measuring alert noise, forecasting capacity and checking an SLA with a canary.'
EXAMPLES = [
    dict(level='b', tag='Thresholds · HDFS', title='WARN and CRIT for disk use at a hospital',
         problem='<p>A hospital records cluster has 600 TB of HDFS. Data grows 2 TB a day. The team wants a WARN with at least 2 weeks to react and a CRIT with at least 3 days. What usage percentages should the thresholds be?</p>',
         inp='600 TB · +2 TB/day · WARN 14 days · CRIT 3 days',
         approach=['Space needed for N days = growth × N.',
                   'Threshold = (capacity − that space) / capacity.',
                   'Round down to a simple number.'],
         code='''cap, growth = 600, 2
for name, days in [("WARN", 14), ("CRIT", 3)]:
    pct = 100 * (cap - growth * days) / cap
    print(f"{name} at {pct:.1f}% used ({days} days of growth left)")
''', notes={3: 'Thresholds :: Derived from growth and reaction time, not copied from a blog.'},
         tryit='Double the growth to 4 TB/day. The WARN threshold drops to about 91%: faster growth needs earlier warnings.'),
    dict(level='i', tag='Noise · on-call', title='How much does a noisy alert cost a payments team?',
         problem='<p>An “under-replicated blocks &gt; 0” rule fires about 30 times a week because of job staging files (like our 7 blocks). Each page wakes someone for 15 minutes. A duration rule (“for 2 hours”) would cut it to 1 per week. How many hours of sleep per month does the fix save?</p>',
         inp='30 pages/week → 1 · 15 min each',
         approach=['Pages saved per week × minutes each.',
                   'Convert to hours per month (about 4.3 weeks).',
                   'Compare with the cost of fixing the cause.'],
         code='''saved = (30 - 1) * 15 * 4.3 / 60
print(f"about {saved:.0f} hours of interrupted sleep saved per month")
''', notes={1: 'Noise :: Every false page also teaches people to ignore the next real one.'},
         tryit='Better still, fix the cause: set mapreduce.client.submit.file.replication to 3 and the alert stops firing at all.'),
    dict(level='i', tag='Forecast · telecom', title='When will the call-records cluster be full?',
         problem='<p>A telecom cluster used 412, 431, 449 and 470 TB on four Mondays in a row. Total capacity is 700 TB. Fit a straight line and estimate in how many weeks it reaches 85%.</p>',
         inp='4 weekly readings · 700 TB · target 85%',
         approach=['Weekly growth = average difference between readings.',
                   'Space left to 85% = 0.85 × 700 − latest.',
                   'Weeks = space left / growth.'],
         code='''used = [412, 431, 449, 470]
growth = (used[-1] - used[0]) / (len(used) - 1)
left = 0.85 * 700 - used[-1]
print(f"growing {growth:.1f} TB/week; 85% reached in about {left / growth:.0f} weeks")
''', notes={2: 'Trend :: The slope of the line, here (470 − 412) / 3 weeks.'},
         tryit='A forecast alert (“full in under 8 weeks”) becomes a purchase ticket instead of a midnight page.'),
    dict(level='a', tag='SLA · canary', title='Is the canary telling us something?',
         problem='<p>An e-commerce canary job normally takes 60–75 s. Tonight its last six runs took 70, 68, 140, 150, 160 and 72 s. The rule is: CRIT if the median of the last 3 runs is at least twice the normal maximum. When does it fire, and does a single slow run fire it?</p>',
         inp='6 canary durations · normal max 75 s',
         approach=['Slide a window of 3 runs.',
                   'Take the median (robust to one outlier).',
                   'Compare with 2 × 75 = 150 s.'],
         code='''runs = [70, 68, 140, 150, 160, 72]
for i in range(2, len(runs)):
    median = sorted(runs[i - 2:i + 1])[1]
    print(f"run {i + 1}: median {median} s", "CRIT" if median >= 150 else "ok")
''', notes={3: 'Median :: One slow run cannot move the median of three; two can.'},
         tryit='It fires at runs 5 and 6, never for the single slow run 3. With the rule “median above 120 s” it fires already at run 4. Choosing the threshold is a trade-off between speed and false alarms.'),
]

QUIZ = mix([
    dict(q='Where does a Hadoop daemon publish its metrics as JSON?', options=['In hdfs-site.xml', 'At the /jmx path of its web port', 'Only in its log files', 'In the fsimage'], answer=1,
         why='e.g. http://namenode:9870/jmx; our monitor.py reads only that and the YARN REST API.'),
    dict(q='Our DataNode stopped. How long until the stale alert appeared?', options=['3 s', '296 s', '30 s', '10 min 30 s'], answer=1,
         why='Stale after 30 s, but the NameNode recounts stale nodes on its 5-minute heartbeat check.'),
    dict(q='When is a DataNode declared dead by default?', options=['After 3 s', 'After 10 min 30 s without heartbeats', 'After 30 s', 'Never automatically'], answer=1,
         why='Our monitor still showed live=3 and dead=0 minutes after the stop.'),
    dict(q='Which metric means data cannot be read right now?', options=['UnderReplicatedBlocks', 'MissingBlocks', 'NumStaleDataNodes', 'FilesTotal'], answer=1,
         why='Under-replicated blocks still have at least one copy; missing blocks have none.'),
    dict(q='Why did 7 under-replicated blocks remain after every fix?', options=['A disk was failing', 'Staging files of killed jobs were written with replication 10 on a 3-DataNode cluster', 'Safe mode was still on', 'The monitor was buggy'], answer=1,
         why='mapreduce.client.submit.file.replication defaults to 10.'),
    dict(q='A second job waited with only 50% of memory used. What held it?', options=['HDFS was full', 'The queue limit on ApplicationMaster resources', 'A dead DataNode', 'Safe mode'], answer=1,
         why='“Queue\'s AM resource limit exceeded” (Lesson 12.6).'),
    dict(q='What does “for 5 minutes” add to an alert rule?', options=['It makes the alert fire faster', 'The condition must hold that long before firing, which removes short blips', 'It repeats the alert every 5 minutes', 'Nothing'], answer=1,
         why='The streak counter in our Python engine is the same idea.'),
    dict(q='What does a canary job detect that single metrics often miss?', options=['The NameNode version', 'Whether the whole path (write, read, run a job) works and how fast', 'Disk serial numbers', 'Configuration files'], answer=1,
         why='Black-box check: green metrics with a slow canary still means users suffer.'),
])

REVISION = [
    'Every daemon exposes metrics at <code>/jmx</code> (JSON); YARN also at <code>/ws/v1/cluster/metrics</code>. Collectors: Prometheus + JMX exporter, Ambari, Cloudera Manager; dashboards in Grafana.',
    'HDFS signals: missing/corrupt blocks, dead/stale DataNodes, under-replicated blocks, capacity %, safe mode, NameNode heap/GC, RPC queue time, checkpoint age.',
    'YARN signals: unhealthy/lost NodeManagers, pending apps, queue usage, AM failures; plus job SLAs and host health.',
    'Lab: stale alert after 296 s (30 s + 5-minute recount); replication 4 → 1 under-replicated; safe mode → CRIT; job waiting at 50% memory (AM limit).',
    'False alert: staging files with replication 10 left 7 under-replicated blocks forever. Fix the cause, not the alert.',
    'Good alerts: symptom-based, WARN vs CRIT, durations, runbook and owner; know each metric\'s lag.',
    'Add black-box canary jobs and forecast alerts for capacity.',
]
FAQ = [
    ('How do you monitor a Hadoop cluster?', 'Collect the metrics every daemon publishes (JMX over HTTP at /jmx, the YARN REST API, metrics2 sinks) with a collector such as Prometheus with the JMX exporter, Ambari Metrics or Cloudera Manager, plus host metrics and logs. Show them on dashboards, and alert on rules such as missing blocks, dead DataNodes, capacity above a threshold, safe mode, unhealthy NodeManagers and late jobs, each with a severity, a duration and a runbook.'),
    ('What is the difference between a stale and a dead DataNode?', 'A DataNode is stale when the NameNode has not received a heartbeat for 30 seconds (dfs.namenode.stale.datanode.interval); clients avoid it for reads and writes. It is dead after about 10 minutes 30 seconds without heartbeats, and only then does the NameNode start re-replicating its blocks. In our lab the stale count metric itself was refreshed every 5 minutes, so the alert came after 296 seconds.'),
    ('What is the difference between under-replicated and missing blocks?', 'An under-replicated block has fewer copies than its target but at least one, so data is still readable and HDFS will copy it again. A missing block has no live copy at all; reads fail until a DataNode holding it comes back. Missing blocks should page someone immediately; under-replicated blocks are usually a warning.'),
    ('How do you avoid alert fatigue?', 'Alert only on symptoms that need a human, use durations so short blips do not fire, separate WARN (daytime ticket) from CRIT (page), attach a runbook to every alert, review noisy alerts weekly and fix their cause, and send everything else to dashboards. Our staging-file alert is an example: fix mapreduce.client.submit.file.replication instead of muting it.'),
    ('What is a canary job?', 'A small synthetic job run on a schedule, for example every 10 minutes, that writes a file, reads it back and runs a tiny MapReduce or Spark job. Its success and duration are monitored. It detects problems users would feel, such as a full queue or slow storage, even when every individual metric looks healthy.'),
]

PRACTICE_INTRO = 'Monitoring exercises using the real numbers from our lab.'
PROBLEMS = [
    dict(level='easy', title='How full is HDFS?', stmt='The JMX bean shows CapacityUsed and CapacityTotal. Compute the percentage used and print a WARN above 80%.', inp='used 4,769 MB of 800,000 MB',
         code='''used, total = 4769, 800000
pct = 100 * used / total
print(f"{pct:.1f}% used", "WARN" if pct > 80 else "ok")
''', explain='0.6% used, like our lab: no warning.'),
    dict(level='easy', title='Under or missing?', stmt='Classify each block by its live replicas: 0 = missing, below target = under-replicated, else ok.', inp='target 3; live 3, 2, 0, 1',
         code='''target = 3
for live in [3, 2, 0, 1]:
    print(live, "missing" if live == 0 else "under-replicated" if live < target else "ok")
''', explain='Only the block with 0 live copies is unreadable.'),
    dict(level='easy', title='Staging files', stmt='Each job leaves 2 staging files (job.jar, job.split), one block each, wanting 10 replicas on a 3-DataNode cluster. How many under-replicated blocks after 4 killed jobs?', inp='4 jobs × 2 blocks',
         code='''print(4 * 2, "under-replicated blocks")
''', explain='8 in this model. Our lab showed 8 while two jobs ran and 7 after the fixes; the exact count depends on which staging files each job writes (job.jar, job.split, extra jars), but the cause is the same.'),
    dict(level='medium', title='Parse a JMX reply', stmt='Read the JSON of a NameNode bean and print live, stale and missing values.', inp='a JSON string',
         code='''import json
reply = '{"beans": [{"NumLiveDataNodes": 3, "NumStaleDataNodes": 1, "MissingBlocks": 0}]}'
b = json.loads(reply)["beans"][0]
print("live", b["NumLiveDataNodes"], "stale", b["NumStaleDataNodes"], "missing", b["MissingBlocks"])
''', explain='The same parsing monitor.py does, one bean at a time.'),
    dict(level='medium', title='Alert delay', stmt='Our alert appeared 296 s after the stop; stale is defined at 30 s. How much of the delay came from the metric refresh and scraping?', inp='296 s, 30 s',
         code='''print(296 - 30, "s of lag beyond the 30 s definition")
''', explain='266 s: most of the delay was metric lag, not the definition.'),
    dict(level='medium', title='Dedupe alerts', stmt='The same alert fired at every check. Print it only when it starts and when it clears.', inp='a list of states',
         code='''states = [False, True, True, True, False, True]
prev = False
for i, s in enumerate(states):
    if s != prev:
        print(f"check {i}:", "FIRING" if s else "RESOLVED")
    prev = s
''', explain='Alert managers send “firing” and “resolved” notifications, not one per check.'),
    dict(level='business', title='Is a monitoring tool worth it?', stmt='A paid tool costs ₹6 lakh a year. Last year the team had 3 outages of 4 hours each that earlier alerts would have cut to 1 hour. One hour of outage costs ₹2 lakh. Worth it?', inp='₹6 lakh · 3 × 3 hours saved · ₹2 lakh/hour',
         code='''saved = 3 * (4 - 1) * 2
print(f"saves Rs {saved} lakh vs costs Rs 6 lakh")
''', explain='₹18 lakh saved against ₹6 lakh (illustrative), before counting staff time.'),
    dict(level='advanced', title='Multi-cluster rules', stmt='Apply the same rules to every cluster in a dict and print alerts with the cluster name, like monitor.py.', inp='prod and dr snapshots',
         code='''fleet = {"prod": {"missing": 0, "safemode": False, "stale": 1},
         "dr": {"missing": 0, "safemode": True, "stale": 0}}
for name, m in fleet.items():
    if m["missing"]: print("CRIT", name, "missing blocks")
    if m["safemode"]: print("CRIT", name, "safe mode")
    if m["stale"]: print("WARN", name, m["stale"], "stale DataNode(s)")
''', explain='One rule set, many clusters: label every metric with its cluster (Lesson 12.1).'),
]

SCN_INTRO = 'Monitoring questions are about judgement: what deserves a page, and what you do when one arrives.'
SCENARIOS = '''    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Basics · metrics</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>“Name five metrics you would alert on for HDFS”</h4>
      <p class="scn__situation">A standard question for Hadoop admin and data engineer roles.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> that you know which metrics mean data risk.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Missing and corrupt blocks (page immediately), dead DataNodes, capacity used %, safe mode, under-replicated blocks trend.</li>
          <li>NameNode heap and GC pauses, RPC queue time, time since the last checkpoint.</li>
          <li>Read them from the NameNode /jmx endpoint with a collector such as Prometheus.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Operations · noise</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>The under-replicated-blocks alert fires every night and nobody looks any more</h4>
      <p class="scn__situation">You join a team where on-call engineers mute this alert.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> root-cause thinking over muting.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Find which files are under-replicated with <code>hdfs fsck / | grep -i "under replicated"</code>; often they are job staging files with replication 10 on a small cluster.</li>
          <li>Fix the cause: mapreduce.client.submit.file.replication ≤ DataNodes, clean old staging folders.</li>
          <li>Change the rule to “growing for 30 minutes” and keep missing blocks as the page.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Incident · latency</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>All metrics are green but analysts say jobs are slow</h4>
      <p class="scn__situation">Dashboards show healthy nodes and 60% disk use.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> black-box monitoring and queue awareness.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Check pending applications and queue usage: a full queue or AM limit keeps jobs in ACCEPTED while memory looks free.</li>
          <li>Check NameNode RPC queue time and GC pauses, which slow every client.</li>
          <li>Add a canary job with a duration alert so this is caught before users report it.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Design · fleet</span><span class="scn__tag scn__tag--level">Architect</span></div>
      <h4>Design monitoring for 12 clusters in three regions</h4>
      <p class="scn__situation">Each business unit ran its own scripts until now.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> standardisation and ownership.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>One Prometheus per region scraping all daemons via the JMX exporter, every metric labelled with cluster and role, central Grafana and Alertmanager.</li>
          <li>One shared rule set with severities and runbooks; routing by cluster owner; SLOs for key pipelines with canaries.</li>
          <li>Capacity forecasts and a weekly noise review; test alerts with planned drills like the ones in this lesson.</li>
        </ul>
      </div></details>
    </article>
'''
