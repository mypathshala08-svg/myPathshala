import os
HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.dirname(HERE)
BODY = body(HERE)
rd = lambda f: open(os.path.join(UP, f)).read()

META = dict(
    module='12-multiple-clusters-and-operations', lesson='06-troubleshooting-playbook', n='12.6',
    module_label='Module 12 · Multiple clusters and operations',
    title='Troubleshooting playbook',
    desc='A Hadoop troubleshooting playbook built from real failures: four incidents reproduced on a Hadoop 3.5.0 cluster (Connection refused on port 9000, NameNode safe mode, "No live nodes contain current block" with a single replica, a job stuck in ACCEPTED because of the queue\'s AM resource limit) plus 20+ real error messages from this course mapped to cause and first command. The method (symptom, scope, changes, evidence, hypothesis, smallest fix, verify, blameless postmortem), the layered checklist and key commands. Python symptom matcher, quiz and interview scenarios.',
    og_desc='Four real Hadoop incidents, each traced from the error message to the layer and the one command that confirms it.',
    minutes=30, level='Intermediate',
    lead='When a Hadoop cluster misbehaves, the error message usually names the layer that broke: the network, HDFS, YARN, the job or security. This lesson reproduces four real incidents on our lab, then turns every failure we met in this course into a playbook: a method, a layered checklist and a table from message to first command.',
    chips=['4 incidents reproduced', '20+ real messages mapped', 'Runs in your browser (Python)'],
)

RUN = dict(
    heading='A symptom matcher for real error messages',
    intro='<p>The first step of every incident is reading the message. This matcher holds a few playbook rules (a pattern, the layer, the likely cause and the first command) and applies them to real messages from our lab.</p>',
    code='''import re
RULES = [
    (r"Connection refused",              "network", "wrong port or daemon down",       "getent hosts; jps"),
    (r"UnknownHostException",            "network", "name not resolvable",             "getent hosts <name>"),
    (r"in safe mode",                    "HDFS",    "NameNode is read-only",           "hdfs dfsadmin -safemode get"),
    (r"No live nodes contain",           "HDFS",    "every replica's DataNode is down", "hdfs fsck <path> -locations"),
    (r"AM resource limit exceeded",      "YARN",    "queue's ApplicationMaster limit",  "yarn application -status"),
    (r"Java heap space",                 "job",     "task heap too small",             "yarn logs (attempt)"),
    (r"cannot authenticate via",         "security","no Kerberos ticket",              "klist"),
]

def diagnose(message):
    for pattern, layer, cause, first in RULES:
        if re.search(pattern, message, re.IGNORECASE):
            return layer, cause, first
    return "unknown", "not in the playbook yet", "read the full log; add a rule"

messages = [
    "Call From namenode/172.22.0.2 to namenode:9000 failed on connection exception: java.net.ConnectException: Connection refused",
    "Cannot create directory /incident_b. Name node is in safe mode.",
    "No live nodes contain current block",
    "Application is added to the scheduler and is not yet activated. Queue's AM resource limit exceeded.",
    "Illegal partition for chai (4)",
]
for m in messages:
    layer, cause, first = diagnose(m)
    print(f"{layer:8} | {cause:32} | {first}")
''',
    anno=[
        ('    (r"AM resource limit exceeded",      "YARN",    "queue\'s ApplicationMaster limit",  "yarn application -status"),', 'Each rule is one playbook row: a clue in the message, the layer, the likely cause and the command that confirms it.'),
        ('    return "unknown", "not in the playbook yet", "read the full log; add a rule"', 'A message with no rule is a gap in the playbook. After the incident, add a rule.'),
    ],
    tasks=[
        dict(label='1 · Match the messages', hint='Press <b>Run</b>. Which message is not in the playbook yet? Which lesson had it?', code=None),
        dict(label='2 · Add a rule', hint='Add a rule for “Illegal partition” (Lesson 9.2): layer job, cause “partitioner returned a wrong number”, first command “yarn logs”. Run again.',
             code='''import re
RULES = [(r"Illegal partition", "job", "partitioner returned a wrong number", "yarn logs")]
m = "java.io.IOException: Illegal partition for chai (4)"
for pattern, layer, cause, first in RULES:
    if re.search(pattern, m):
        print(layer, "|", cause, "|", first)
'''),
        dict(label='3 · The AM limit', hint='<b>Predict first:</b> the default queue may use 10% of 6,144 MB for ApplicationMasters, rounded up to a multiple of 256 MB. How many 512 MB AMs fit? What if the percent is 0.3?',
             code='''import math
cluster, am = 6144, 512
for pct in [0.1, 0.3]:
    limit = math.ceil(cluster * pct / 256) * 256
    print(f"percent {pct}: AM limit {limit} MB -> {limit // am} AM(s) can run")
'''),
        dict(label='4 · Scope first', hint='Given failures per node, decide the scope: one node or the whole cluster?',
             code='''failures = {"worker1": 0, "worker2": 14, "worker3": 0}
bad = [n for n, f in failures.items() if f > 0]
scope = "one node: " + bad[0] if len(bad) == 1 else ("cluster-wide" if len(bad) == len(failures) else "several nodes")
print(scope)
'''),
        dict(label='5 · Spot the error', hint='This timeline parser crashes on the incident log. Fix it so lines without a time are skipped.',
             code='''log = ["06:05 report missing", "note: nothing failed", "06:09 AM limit found"]
for line in log:
    hh, mm = line.split()[0].split(":")
    print(int(hh) * 60 + int(mm), line)
''', expect='error'),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run it on your PC: four incidents on purpose',
    intro='<p>Run this on your PC in the <code>mr-lab</code> folder with the Module 8 lab running. It creates each incident, prints the exact message, and puts things back: it leaves safe mode, restarts the DataNode it stopped and kills the two sleep jobs. It takes about 3 minutes.</p>',
    items=[
        dict(title='Four incidents and their messages', file='trouble_lab.sh',
             cmd=rd('lab/trouble_lab.sh') + '\n# Run on your PC, in the mr-lab folder:\n#   bash trouble_lab.sh',
             output=rd('tx126.txt').strip(),
             note='Real output. The DataNode holding the single replica depends on placement (worker2 in our run). The diagnostics line is cut at 200 characters; the full line also prints the AM partition and resource numbers.'),
    ],
)

TRACE = dict(
    heading='Walking the layers in order',
    intro='<p>A checklist in dependency order: stop at the first layer that fails. Watch <code>layer</code> and <code>ok</code>.</p>',
    code='''checks = [("network", True), ("HDFS", True), ("YARN", False), ("job", True)]
found = None
for layer, ok in checks:
    if not ok:
        found = layer
        break
print("first broken layer:", found)
''',
    notes={3: 'Order :: Network first, then HDFS, YARN and the job: each depends on the layers before it.',
           5: 'Stop :: The first failing layer is where to dig; later layers may only fail because of it.'},
)

WORKED_INTRO = 'Four incidents from different industries, each diagnosed from its message.'
EXAMPLES = [
    dict(level='b', tag='Diagnose · network', title='An analyst at a hospital network gets “UnknownHostException”',
         problem='<p>A notebook in the hospital analytics team fails with <code>java.net.UnknownHostException: nn-records</code>. Other users can read HDFS. What layer is it, and what is the first check?</p>',
         inp='message + scope: one user',
         approach=['UnknownHost: the name itself does not resolve (not “refused”).',
                   'Scope is one user, so the cluster is fine; look at that client.',
                   'Compare the client\'s fs.defaultFS with a working user\'s.'],
         code='''working = "hdfs://nn-patients:8020"
broken = "hdfs://nn-records:8020"
print("same?", working == broken, "| fix the client config:", broken, "->", working)
''', notes={2: 'Config :: A copied notebook kept an old NameNode name.'},
         tryit='Lesson 7.2 saw the same message when a federated NameNode was down; there, every user was affected.'),
    dict(level='i', tag='Diagnose · HDFS', title='A telecom ingest job fails at midnight: safe mode',
         problem='<p>After planned maintenance on a telecom operator\'s cluster, the CDR ingest fails with “Name node is in safe mode.” <code>hdfs dfsadmin -report</code> shows 38 of 40 DataNodes live and the NameNode reports 99.7% of blocks. The threshold is 99.9%. What do you do?</p>',
         inp='38/40 live · 99.7% reported · threshold 99.9%',
         approach=['Safe mode is waiting for block reports.',
                   'Two DataNodes are missing: start them, don\'t force safe mode off.',
                   'Check what forcing would mean: some blocks have no live replica yet.'],
         code='''blocks = 50_000_000
reported = 0.997
print(f"{blocks * (1 - reported):,.0f} blocks not reported yet; threshold needs {blocks * 0.999:,.0f}")
''', notes={2: 'Gap :: 150,000 blocks are waiting for the two missing DataNodes.'},
         tryit='Once the two DataNodes start and report, safe mode ends by itself after the extension period (30 s by default).'),
    dict(level='i', tag='Diagnose · YARN', title='An e-commerce team\'s jobs wait in ACCEPTED',
         problem='<p>During a sale, 6 small jobs in the <code>analytics</code> queue sit in ACCEPTED. The queue has 200 GB, maximum-am-resource-percent 0.1 and each ApplicationMaster uses 4 GB. 5 are running. Why do the rest wait, and what is a safe change?</p>',
         inp='200 GB · AM 10% · 4 GB per AM',
         approach=['AM budget = 10% of the queue.',
                   'Count how many AMs fit.',
                   'Raise the percent for many small jobs, or wait.'],
         code='''queue_gb, pct, am_gb = 200, 0.1, 4
budget = queue_gb * pct
print(f"AM budget {budget:.0f} GB -> {int(budget // am_gb)} AMs; with 0.3: {int(queue_gb * 0.3 // am_gb)} AMs")
''', notes={2: 'Budget :: 20 GB of AMs means 5 jobs at a time, however idle the rest is.'},
         tryit='Many tiny jobs need a higher AM percent; few large jobs don\'t. Our lab showed the same message with 768 MB of AM budget.'),
    dict(level='a', tag='Diagnose · data', title='A bank\'s report fails with Java heap space only on month end',
         problem='<p>A bank\'s reconciliation job succeeds every day but fails on the last day of the month with <code>Error: Java heap space</code> in one reduce task. Daily data is 40 GB; month-end adds a 25× spike for one account type. What is the likely cause and the first command?</p>',
         inp='one reducer · month end · 25× one key',
         approach=['Only one reduce task fails: think skew (Lesson 8.5).',
                   'A reducer holding all values of one hot key in memory runs out of heap.',
                   'First: the failed attempt\'s log and the reduce input records per task.'],
         code='''normal = 40 / 50                      # GB per reducer, 50 reducers
hot = normal + 25 * 0.4               # one key grows 25x (0.4 GB on normal days)
print(f"normal reducer {normal:.1f} GB, hot reducer {hot:.1f} GB")
''', notes={2: 'Skew :: One reducer gets 13 times the normal input.'},
         tryit='Fix the code (stream instead of collecting) or split the hot key (salting, Lesson 9.2); raising the heap only moves the limit.'),
]

QUIZ = mix([
    dict(q='What is the first step when an incident starts?', options=['Restart the NameNode', 'Write down the exact message, time and scope', 'Add more nodes', 'Delete the job output'], answer=1,
         why='Evidence first; a restart can hide it.'),
    dict(q='“Connection refused” to namenode:9000 most likely means…', options=['The disk is full', 'Nothing listens on that port: wrong port or daemon down', 'The user has no permission', 'The file is missing'], answer=1,
         why='The host answered and refused; our NameNode listens on 8020.'),
    dict(q='In safe mode, what still works?', options=['Writes only', 'Reads', 'Nothing', 'Deletes'], answer=1,
         why='Our lab: mkdir failed while cat of menu.csv worked.'),
    dict(q='Why did the read of /incident_c.csv fail?', options=['Wrong permissions', 'Its only replica was on the stopped DataNode', 'Safe mode', 'The file was deleted'], answer=1,
         why='It was written with replication 1.'),
    dict(q='A job sits in ACCEPTED with “Queue\'s AM resource limit exceeded” while the cluster is half empty. The cause?', options=['Not enough memory in the cluster', 'The queue\'s ApplicationMaster budget is used up', 'The NameNode is down', 'The jar is missing'], answer=1,
         why='10% of 6,144 MB → 768 MB; one 512 MB AM was running.'),
    dict(q='Which order does the layered checklist follow?', options=['Job, YARN, HDFS, network', 'Network, HDFS, YARN, job, security', 'Security first, always', 'Any order'], answer=1,
         why='Each layer depends on the ones before it.'),
    dict(q='What makes a postmortem blameless?', options=['It is never written down', 'It looks at what the system allowed, not who to punish', 'Only managers write it', 'It skips the timeline'], answer=1,
         why='People share facts openly when they are not blamed.'),
    dict(q='“PipeMapRed … subprocess failed with code 1”: where is the real error?', options=['In the NameNode log', 'In the task\'s stderr (yarn logs -log_files stderr)', 'In the client output', 'In fsck'], answer=1,
         why='Lesson 9.8: the Python NameError was only in stderr.'),
])

REVISION = [
    'Method: <b>symptom → scope → recent changes → evidence → hypothesis → smallest safe fix → verify → postmortem</b>.',
    'Layers in order: <b>network/DNS → HDFS → YARN → job → security</b>; stop at the first broken one.',
    'Connection refused = host reached, port wrong or daemon down; UnknownHost = the name doesn\'t resolve.',
    'Safe mode: reads work, writes fail; find why before forcing <code>-safemode leave</code>.',
    '“No live nodes contain current block”: every replica\'s DataNode is down; <code>fsck -locations</code>.',
    'ACCEPTED on an idle cluster: check <code>yarn application -status</code> diagnostics (AM limit, queue limits).',
    'Job errors: <code>yarn logs</code> of the failed attempt gives the exception and line (Lesson 11.5).',
    'Blameless postmortem: timeline, root cause, detection gap, tracked actions; add a playbook rule and an alert.',
]
FAQ = [
    ('How do you troubleshoot a Hadoop cluster problem?', 'Record the exact error and time, establish the scope (one job, user, node, queue or the whole cluster) and what changed recently. Then check the layers in order: network and name resolution, HDFS (NameNode state, safe mode, DataNodes, blocks with dfsadmin -report and fsck), YARN (yarn node -list -all, application status and queue limits), the job (yarn logs of the failed attempt) and security (klist, permissions). Apply the smallest safe fix, verify with the same command, and write a postmortem.'),
    ('Why is my YARN application stuck in ACCEPTED?', 'The scheduler has accepted it but cannot start its ApplicationMaster. Common causes are the queue\'s AM resource limit (maximum-am-resource-percent, 10% by default), the queue or user limit being used up, no NodeManager with enough free memory, or node labels that no node matches. yarn application -status shows the diagnostics, e.g. “Queue\'s AM resource limit exceeded.”'),
    ('What does “Name node is in safe mode” mean?', 'The NameNode is read-only: it serves reads but refuses changes to the namespace. It enters safe mode at startup until enough DataNodes have reported their blocks (99.9% by default), or when an administrator turns it on. Check with hdfs dfsadmin -safemode get and find out why before leaving it by hand.'),
    ('What does “Could not obtain block” or “No live nodes contain current block” mean?', 'The client could not read any replica of a block, usually because the DataNodes holding all replicas are down or unreachable. Use hdfs fsck &lt;path&gt; -files -blocks -locations to see where the replicas are, bring those DataNodes back, and check that important data has replication 3.'),
    ('What is a blameless postmortem?', 'A written review after an incident that records the timeline, impact, root cause, why detection was late and the follow-up actions, without blaming individuals. It assumes people acted reasonably with the information they had and focuses on changing the system so the incident can\'t repeat.'),
]

PRACTICE_INTRO = 'Diagnosis exercises using the real messages and numbers from our lab.'
PROBLEMS = [
    dict(level='easy', title='Name the layer', stmt='For each message, print the layer: network, HDFS, YARN or job.', inp='4 real messages',
         code='''msgs = {"Connection refused": "network", "Name node is in safe mode.": "HDFS",
        "Queue's AM resource limit exceeded.": "YARN", "Error: Java heap space": "job"}
for m, layer in msgs.items():
    print(f"{layer:8} <- {m}")
''', explain='The clue word in each message names its layer.'),
    dict(level='easy', title='How late was the alert?', stmt='The DataNode stopped at 10:21:12 and the stale alert appeared at 10:26:08 (Lesson 12.4). How many seconds is the detection gap?', inp='two times',
         code='''from datetime import datetime
a, b = datetime.strptime("10:21:12", "%H:%M:%S"), datetime.strptime("10:26:08", "%H:%M:%S")
print((b - a).seconds, "s")
''', explain='296 s: the stale-node count is recomputed on the NameNode\'s heartbeat check.'),
    dict(level='easy', title='AM budget', stmt='What is 10% of 6,144 MB, rounded up to a multiple of 256 MB?', inp='6,144 MB · 0.1 · 256',
         code='''import math
print(math.ceil(6144 * 0.1 / 256) * 256, "MB")
''', explain='768 MB, the AM limit our scheduler reported.'),
    dict(level='medium', title='Replicas left', stmt='Given each block\'s replica nodes and the stopped node, list blocks that become unreadable.', inp='3 blocks · worker2 stopped',
         code='''blocks = {"blk_1": ["worker2"], "blk_2": ["worker1", "worker2", "worker3"], "blk_3": ["worker2", "worker3"]}
down = {"worker2"}
print([b for b, nodes in blocks.items() if set(nodes) <= down])
''', explain='Only blk_1 (replication 1) is lost from view; the others still have a live replica.'),
    dict(level='medium', title='Build a timeline', stmt='Turn incident notes into minutes since the first event, skipping lines without a time.', inp='incident notes',
         code='''notes = ["06:05 report missing", "checked dashboards", "06:09 AM limit found", "06:16 stuck job killed", "06:48 report delivered"]
t0 = None
for n in notes:
    first = n.split()[0]
    if ":" not in first:
        continue
    h, m = map(int, first.split(":"))
    t0 = t0 if t0 is not None else h * 60 + m
    print(f"+{h * 60 + m - t0:3d} min  {n[6:]}")
''', explain='Diagnosed in 4 minutes, mitigated in 11, delivered in 43: the timeline of a postmortem.'),
    dict(level='medium', title='Is it the cluster or the job?', stmt='A job failed on 4 attempts on 4 different nodes with the same exception. Is the cause the nodes or the job/data?', inp='4 attempts, 4 nodes, 1 exception',
         code='''attempts = [("worker1", "NumberFormatException"), ("worker2", "NumberFormatException"),
            ("worker3", "NumberFormatException"), ("worker1", "NumberFormatException")]
nodes = {n for n, _ in attempts}
errors = {e for _, e in attempts}
print("job or data" if len(errors) == 1 and len(nodes) > 1 else "look at the nodes")
''', explain='The same error on different nodes points at the code or the data (Lesson 11.5), not at a machine.'),
    dict(level='business', title='Cost of restarting first', stmt='A NameNode restart costs 12 minutes of safe mode during which 300 analysts can\'t write. Diagnosing first takes 5 minutes and needs no restart. Compare lost analyst-minutes.', inp='12 min × 300 vs 5 min × 1',
         code='''print("restart first:", 12 * 300, "analyst-minutes lost; diagnose first:", 5, "engineer-minutes")
''', explain='3,600 analyst-minutes vs 5: “just restart” is expensive even when it works.'),
    dict(level='advanced', title='A tiny rule engine with priorities', stmt='Some messages match several rules (a Java heap space inside a failed Streaming task). Return the most specific rule (longest pattern).', inp='rules + message',
         code='''import re
rules = {"Java heap space": "task heap too small", "subprocess failed": "streaming script crashed", "failed": "something failed"}
msg = "PipeMapRed.waitOutputThreads(): subprocess failed with code 1"
hits = [p for p in rules if re.search(p, msg)]
best = max(hits, key=len)
print(best, "->", rules[best])
''', explain='“subprocess failed” beats the generic “failed”: specific rules first, generic ones as a fallback.'),
]

SCN_INTRO = 'Troubleshooting questions test method more than memory. Interviewers want to hear how you think under pressure.'
SCENARIOS = '''    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Method · basics</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>“A user says HDFS is down. What do you do?”</h4>
      <p class="scn__situation">A classic open question.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> method before action.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Get the exact message and time; check the scope: can I and other users list HDFS?</li>
          <li>Check the NameNode (jps, web UI, <code>hdfs dfsadmin -report</code>, <code>-safemode get</code>) and the DataNodes.</li>
          <li>If only that user fails, look at their client config and network (Connection refused, UnknownHost); if everyone fails, it's the NameNode or safe mode.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">YARN · queues</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>Jobs stuck in ACCEPTED, cluster 40% used</h4>
      <p class="scn__situation">The business is waiting for a report.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> queue limits, not “add nodes”.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li><code>yarn application -status</code> diagnostics: e.g. “Queue's AM resource limit exceeded” or user limit reached.</li>
          <li>Scheduler REST/UI for that queue: AM limit vs AM used, capacity vs used, user limits.</li>
          <li>Mitigate (kill or move a stuck job), then fix: raise maximum-am-resource-percent for queues with many small jobs, add an alert for long ACCEPTED times.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">HDFS · data</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>fsck reports missing blocks after a rack power failure</h4>
      <p class="scn__situation">One rack of 20 nodes went down; it's back now, but 30 blocks are still missing.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> calm recovery, not deleting data.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li><code>hdfs fsck / -list-corruptfileblocks</code> to list the files; <code>-locations</code> shows where replicas should be.</li>
          <li>Check that all DataNodes of the rack really came back (dfsadmin -report), with all their disks mounted; missing disks are a common cause.</li>
          <li>Only for blocks that are truly gone: restore from DR/backup (Lesson 12.2) or re-ingest; never run <code>fsck -delete</code> first.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Operations · culture</span><span class="scn__tag scn__tag--level">Lead</span></div>
      <h4>“The same incident happened three times this quarter”</h4>
      <p class="scn__situation">A director asks why.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> postmortems that lead to change.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Each time it was mitigated but the root-cause action wasn't owned or finished: track postmortem actions like product work.</li>
          <li>Add detection (an alert), prevention (a quota, a config check in CI) and a playbook rule, so the fourth time is short or impossible.</li>
          <li>Keep reviews blameless so people report near-misses early.</li>
        </ul>
      </div></details>
    </article>
'''
