import os
HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.dirname(HERE)
BODY = body(HERE)
rd = lambda f: open(os.path.join(UP, f)).read()

META = dict(
    module='11-yarn', lesson='02-the-life-of-a-yarn-application', n='11.2',
    module_label='Module 11 · YARN',
    title='The life of a YARN application',
    desc='The full lifecycle of a YARN application, traced on a real Hadoop 3.5.0 cluster: client getNewApplication and submit, RM state store (NEW_SAVING), ACCEPTED in 0.1 s, AM container localized and launched, AM registered after 5 s, allocate heartbeats, task containers, unregister and FINISHED at 35.6 s. Every RMApp, RMAppAttempt and container state from the ResourceManager and NodeManager logs, 33,224 MB-seconds of usage, a killed application and an impossible 3 GB request. Architecture diagram, two animations, Python state-machine simulation, quiz and interview scenarios.',
    og_desc='Follow one YARN application from Enter to FINISHED: 18 real state changes, 36 seconds, 33,224 MB-seconds.',
    minutes=28, level='Intermediate',
    lead='Every job on a Hadoop cluster, MapReduce or Spark, goes through the same lifecycle in YARN: it is submitted, gets an ApplicationMaster, asks for containers, runs and reports back. This lesson follows one real application through every state the ResourceManager and NodeManager log, then kills one and breaks one, so you can read any stuck or failed job.',
    chips=['Every state from the real RM log', 'Architecture diagram + 2 animations', 'Runs in your browser (Python)'],
)

RUN = dict(
    heading='Simulate the application and attempt state machines',
    intro='<p>A small model of YARN\'s RMApp and RMAppAttempt state machines. Each event moves an object to its next state, exactly as the lines in the ResourceManager log say. Run it and compare with our real log.</p>',
    code='''APP = {("NEW", "START"): "NEW_SAVING", ("NEW_SAVING", "APP_NEW_SAVED"): "SUBMITTED",
       ("SUBMITTED", "APP_ACCEPTED"): "ACCEPTED", ("ACCEPTED", "ATTEMPT_REGISTERED"): "RUNNING",
       ("RUNNING", "ATTEMPT_UNREGISTERED"): "FINAL_SAVING", ("FINAL_SAVING", "APP_UPDATE_SAVED"): "FINISHING",
       ("FINISHING", "ATTEMPT_FINISHED"): "FINISHED"}
ATTEMPT = {("NEW", "START"): "SUBMITTED", ("SUBMITTED", "ATTEMPT_ADDED"): "SCHEDULED",
           ("SCHEDULED", "CONTAINER_ALLOCATED"): "ALLOCATED_SAVING", ("ALLOCATED_SAVING", "ATTEMPT_NEW_SAVED"): "ALLOCATED",
           ("ALLOCATED", "LAUNCHED"): "LAUNCHED", ("LAUNCHED", "REGISTERED"): "RUNNING",
           ("RUNNING", "UNREGISTERED"): "FINAL_SAVING", ("FINAL_SAVING", "ATTEMPT_UPDATE_SAVED"): "FINISHING",
           ("FINISHING", "CONTAINER_FINISHED"): "FINISHED"}
state = {"app": "NEW", "attempt": "NEW"}

def fire(obj, event, time):
    table = APP if obj == "app" else ATTEMPT
    new = table[(state[obj], event)]          # an event that isn't allowed here raises KeyError
    print(f"{time}  {obj:7} {state[obj]:>16} -> {new:16} on {event}")
    state[obj] = new

for t, obj, ev in [("06:25:43", "app", "START"), ("06:25:43", "app", "APP_NEW_SAVED"), ("06:25:43", "app", "APP_ACCEPTED"),
                   ("06:25:43", "attempt", "START"), ("06:25:43", "attempt", "ATTEMPT_ADDED"),
                   ("06:25:43", "attempt", "CONTAINER_ALLOCATED"), ("06:25:43", "attempt", "ATTEMPT_NEW_SAVED"),
                   ("06:25:43", "attempt", "LAUNCHED"), ("06:25:48", "attempt", "REGISTERED"),
                   ("06:25:48", "app", "ATTEMPT_REGISTERED"), ("06:26:19", "attempt", "UNREGISTERED"),
                   ("06:26:19", "attempt", "ATTEMPT_UPDATE_SAVED"), ("06:26:19", "app", "ATTEMPT_UNREGISTERED"),
                   ("06:26:19", "app", "APP_UPDATE_SAVED"), ("06:26:25", "attempt", "CONTAINER_FINISHED"),
                   ("06:26:25", "app", "ATTEMPT_FINISHED")]:
    fire(obj, ev, t)
''',
    anno=[
        ('    new = table[(state[obj], event)]          # an event that isn\'t allowed here raises KeyError', 'A state machine only accepts certain events in each state. YARN logs “Can\'t handle this event at current state” in that case.'),
        ('                   ("06:25:43", "attempt", "LAUNCHED"), ("06:25:48", "attempt", "REGISTERED"),', 'The 5-second gap: the MRAppMaster JVM starting up on worker2.'),
        ('                   ("06:25:48", "app", "ATTEMPT_REGISTERED"), ("06:26:19", "attempt", "UNREGISTERED"),', 'Between these two lines the RM logs nothing about the app: the AM runs its own tasks.'),
    ],
    tasks=[
        dict(label='1 · Replay the log', hint='Press <b>Run</b> and compare each line with the real RM log in Part 4. How many state changes in total?', code=None),
        dict(label='2 · MB-seconds', hint='<b>Predict first:</b> an AM of 512 MB for 36 s, one map of 512 MB for 21 s, one reduce of 512 MB for 7 s. How many MB-seconds? Our real run reported 33,224.',
             code='''containers = [("AM", 512, 36.2), ("map", 512, 21.1), ("reduce", 512, 7.5)]
total = sum(mb * s for _, mb, s in containers)
for name, mb, s in containers:
    print(f"{name:7} {mb} MB x {s:5.1f} s = {mb * s:8,.0f} MB-s")
print(f"total {total:,.0f} MB-seconds")
'''),
        dict(label='3 · Wait in ACCEPTED', hint='Given submit and launch times (from the RM REST API), compute how long each app waited for its ApplicationMaster and flag waits over 60 s.',
             code='''apps = {"big (FIFO)": (0.0, 0.6), "small (FIFO)": (15.0, 135.4), "small (capacity)": (15.0, 15.1)}
for name, (started, launched) in apps.items():
    wait = launched - started
    print(f"{name:17} waited {wait:6.1f} s", "<- stuck in ACCEPTED" if wait > 60 else "")
'''),
        dict(label='4 · A second attempt', hint='Simulate an AM that crashes on attempt 1 with max-attempts = 2. Then set it to 1. What is the application\'s final state each time?',
             code='''max_attempts = 2
crashes = {1: True, 2: False}           # attempt 1 crashes, attempt 2 works
for n in range(1, max_attempts + 1):
    if crashes.get(n):
        print(f"appattempt_..._00000{n}: FAILED")
        continue
    print(f"appattempt_..._00000{n}: FINISHED -> application FINISHED")
    break
else:
    print("no attempts left -> application FAILED")
'''),
        dict(label='5 · Spot the error', hint='This code tries to move an application from ACCEPTED straight to FINISHED. Find the missing event and fix the order.',
             code='''APP = {("ACCEPTED", "ATTEMPT_REGISTERED"): "RUNNING", ("RUNNING", "ATTEMPT_UNREGISTERED"): "FINAL_SAVING"}
state = "ACCEPTED"
for event in ["ATTEMPT_UNREGISTERED"]:
    state = APP[(state, event)]
print(state)
''', expect='error'),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run it on your PC: watch, kill and break an application',
    intro='<p>Use the Module 8 lab (Lesson 8.1). Copy <code>app_states.py</code> and <code>lifecycle_lab.sh</code> into the namenode container (<code>docker cp … lab8-namenode-1:/tmp/mr/</code>) and run the script there. It runs ItemRevenue on <code>orders_x30.csv</code> while polling the ResourceManager, kills a second run, and asks for an impossible container. The RM and NM logs are read from your PC with <code>docker logs</code>.</p>',
    items=[
        dict(title='Poll the ResourceManager', file='app_states.py',
             cmd=rd('lab/app_states.py') + '\n# Used by lifecycle_lab.sh:  python3 /tmp/mr/app_states.py application_<id>',
             output=rd('tx112.txt').strip().split('== 2.')[0].strip(),
             note='Real output of the first part of lifecycle_lab.sh. The NEW, NEW_SAVING and SUBMITTED states pass in under 0.1 s, so the poller first sees ACCEPTED; the RM log below has them all.'),
        dict(title='Watch, kill, break', file='lifecycle_lab.sh',
             cmd=rd('lab/lifecycle_lab.sh') + '\n# Run:  docker exec lab8-namenode-1 bash /tmp/mr/lifecycle_lab.sh',
             output=rd('tx112.txt').strip(),
             note='Real output. The InvalidResourceRequestException line is cut at 250 characters by the script; the full message also names the requested and the maximum resources.'),
        dict(title='Every state change in the daemon logs', file='Terminal (your PC)',
             cmd='# In the mr-lab folder, after lifecycle_lab.sh (use your own application id):\napp=application_1792643020992_0136; id=${app#application_}\ndocker logs lab8-resourcemanager-1 2>&1 | grep "$app\\|appattempt_$id" | grep "State change"\ndocker logs lab8-worker2-1 2>&1 | grep "container_${id}_01_000001 transitioned"\n# worker2 is the AM host shown by yarn application -status',
             output=rd('tx112b.txt').strip(),
             note='Real log lines, with the date and log level trimmed for width. Your AM may run on another worker; check “AM Host” first.'),
    ],
)

TRACE = dict(
    heading='A container\'s life on the NodeManager',
    intro='<p>The NodeManager keeps its own small state machine for each container. Follow the ApplicationMaster\'s container <code>_000001</code> through the five transitions we saw in the worker2 log.</p>',
    code='''events = ["INIT", "RESOURCES_LOCALIZED", "CONTAINER_LAUNCHED", "EXITED", "CLEANED_UP"]
nxt = {"NEW": "LOCALIZING", "LOCALIZING": "SCHEDULED", "SCHEDULED": "RUNNING",
       "RUNNING": "EXITED_WITH_SUCCESS", "EXITED_WITH_SUCCESS": "DONE"}
state = "NEW"
log = []
for ev in events:
    state = nxt[state]
    log.append(state)
print(" -> ".join(["NEW"] + log))
''',
    notes={7: 'LOCALIZING :: The jar and job.xml are copied from HDFS staging to the worker.',
           8: 'RUNNING :: The AM JVM is started; registration with the RM follows.',
           9: 'DONE :: Exit code 0 gives EXITED_WITH_SUCCESS; logs are then aggregated.'},
)

WORKED_INTRO = 'Four lifecycle problems from different organisations: billing, waiting, retries and kills.'
EXAMPLES = [
    dict(level='b', tag='Chargeback · bank', title='Bill a department for its jobs',
         problem='<p>A bank charges departments ₹5 per GB-hour of YARN memory (an illustrative internal rate). The risk team ran 40,000 jobs last month, each about like ours: 33,224 MB-seconds. What is the bill?</p>',
         inp='40,000 × 33,224 MB-s · ₹5 per GB-hour',
         approach=['Total MB-seconds = jobs × MB-s per job.',
                   'Convert: GB-hours = MB-s / 1024 / 3600.',
                   'Multiply by the rate.'],
         code='''mb_s = 40_000 * 33_224
gb_h = mb_s / 1024 / 3600
print(f"{mb_s:,} MB-s = {gb_h:.2f} GB-hours -> Rs {gb_h * 5:,.0f}")
''', notes={2: 'Units :: 1 GB-hour = 1024 MB held for 3600 s.'},
         tryit='Small jobs are cheap but not free: the ApplicationMaster alone is more than half of each job\'s MB-seconds here.'),
    dict(level='i', tag='Accounting · lab run', title='Where did our 33,224 MB-seconds go?',
         problem='<p>Our app started at 1792650343192 ms and finished at 1792650379385 ms. The AM held 512 MB all the time. How many MB-seconds were the task containers, and how many seconds of 512 MB containers is that?</p>',
         inp='start/finish in ms · total 33,224 MB-s · AM 512 MB',
         approach=['Elapsed = finish − start.',
                   'AM share = 512 × elapsed.',
                   'Task share = total − AM share; divide by 512.'],
         code='''elapsed = (1792650379385 - 1792650343192) / 1000
am = 512 * elapsed
tasks = 33_224 - am
print(f"elapsed {elapsed:.1f} s, AM {am:,.0f} MB-s, tasks {tasks:,.0f} MB-s = {tasks / 512:.1f} s of a 512 MB container")
''', notes={3: 'Remainder :: About 29 s: the map (about 21 s) plus the reduce (about 7.5 s).'},
         tryit='Check with the poll output: one task container from +6.0 to +27.1 s and another from +28.1 s to the end.'),
    dict(level='i', tag='Retries · e-commerce', title='Will the sale-day ETL survive an AM crash?',
         problem='<p>An e-commerce ETL runs 3 hours. The node running its ApplicationMaster has a 5% chance of failing during that time; a new attempt lands on another node with the same 5% chance. With <code>max-attempts</code> = 1 vs 2, what is the chance the application FAILS because of AM crashes?</p>',
         inp='p(AM node fails) = 0.05 per attempt',
         approach=['With 1 attempt, failure probability = p.',
                   'With 2 attempts, both must fail: p × p.',
                   'Compare.'],
         code='''p = 0.05
for attempts in (1, 2):
    print(f"max-attempts={attempts}: fails {p ** attempts * 100:.2f}% of the time")
''', notes={2: 'Independence :: Assumes the retry runs on a different node.'},
         tryit='Retries help, but they restart the AM: MapReduce recovers finished tasks, many other frameworks start over.'),
    dict(level='a', tag='Operations · telecom', title='Kill or wait?',
         problem='<p>At 02:00 a telecom\'s billing job is stuck: RUNNING for 3 h with 4 of 400 maps left, each retrying. The next job in the queue must finish by 06:00 and needs 3.5 h on the full queue. The stuck job holds 30% of the queue. Should on-call kill it now, or wait until 03:00?</p>',
         inp='deadline 06:00 · next job 3.5 h at 100%, longer with less',
         approach=['Runtime of the next job scales with the share it gets.',
                   'Compute finish time if started at 02:00 with 70% vs at 03:00 with 100%.',
                   'Compare with the deadline.'],
         code='''def finish(start_h, share):
    return start_h + 3.5 / share
for label, start, share in [("kill now, start 02:00 at 100%", 2, 1.0),
                            ("start now beside it at 70%", 2, 0.7), ("wait, start 03:00 at 100%", 3, 1.0)]:
    f = finish(start, share)
    print(f"{label:30} done at {int(f):02d}:{int(f % 1 * 60):02d}", "OK" if f <= 6 else "LATE")
''', notes={1: 'Model :: Simplified: speed proportional to the share of the queue.'},
         tryit='A kill releases all containers at once (our killed app went to 0 MB immediately). The stuck job can be rerun later with its bad input fixed.'),
]

QUIZ = mix([
    dict(q='What does ACCEPTED mean for a YARN application?', options=['It is running its tasks', 'The scheduler admitted it to a queue; its ApplicationMaster may not be running yet', 'It has finished successfully', 'The client has uploaded its jar'], answer=1,
         why='Our app was ACCEPTED at +0.1 s but RUNNING only at +5.0 s, after the AM registered.'),
    dict(q='Which event moves an application from ACCEPTED to RUNNING?', options=['The first map task starts', 'The ApplicationMaster registers with the ResourceManager', 'The client calls submitApplication', 'The jar is localized'], answer=1,
         why='RM log: “ACCEPTED to RUNNING on event = ATTEMPT_REGISTERED”.'),
    dict(q='What are the _SAVING states (NEW_SAVING, FINAL_SAVING)?', options=['Writes to HDFS output', 'Writes to the ResourceManager state store so the RM can recover', 'Checkpoints of the ApplicationMaster', 'Log aggregation'], answer=1,
         why='A restarted or failed-over RM rebuilds its applications from the state store.'),
    dict(q='Which container runs the ApplicationMaster of the first attempt?', options=['container_…_01_000000', 'container_…_01_000001', 'The last container allocated', 'A container on the ResourceManager host'], answer=1,
         why='Container 1 of attempt 01; task containers follow from _000002.'),
    dict(q='What happens during LOCALIZING?', options=['The scheduler picks a node', 'The NodeManager copies the job\'s files (jar, job.xml) from HDFS to the node', 'The AM asks for containers', 'Logs are moved to HDFS'], answer=1,
         why='Local resources from the ContainerLaunchContext are downloaded before launch.'),
    dict(q='Who starts the map and reduce task containers?', options=['The ResourceManager', 'The ApplicationMaster, by calling startContainers on NodeManagers', 'The client', 'The JobHistory Server'], answer=1,
         why='The RM only grants containers; the AM launches them.'),
    dict(q='A MapReduce job whose tasks failed ends with which RM state and final status?', options=['KILLED / KILLED', 'FINISHED / FAILED', 'RUNNING / FAILED', 'FINISHED / SUCCEEDED'], answer=1,
         why='The AM unregistered normally (FINISHED) but reported a failed job.'),
    dict(q='Our app reported 33,224 MB-seconds. What does that measure?', options=['Bytes read from HDFS', 'Memory held by all its containers multiplied by how long they held it', 'Shuffle traffic', 'Heap used by the AM'], answer=1,
         why='It is YARN\'s usage meter, used for chargeback and capacity planning.'),
])

REVISION = [
    'Client: <code>getNewApplication</code> → stage jar/conf in HDFS → <code>submitApplication</code> (with the AM\'s ContainerLaunchContext).',
    'App states: NEW → NEW_SAVING → SUBMITTED → ACCEPTED → RUNNING → FINAL_SAVING → FINISHING → FINISHED (or FAILED, KILLED).',
    'Attempt states: … SCHEDULED → ALLOCATED → LAUNCHED → RUNNING (on REGISTERED) …; container: NEW → LOCALIZING → SCHEDULED → RUNNING → EXITED_WITH_SUCCESS → DONE.',
    'Lab: ACCEPTED +0.1 s, RUNNING +5.0 s (AM JVM start), FINISHED +35.6 s; 33,224 MB-seconds, 64 vcore-seconds.',
    'The AM registers, sends <b>allocate</b> heartbeats with locality preferences, and launches tasks with <b>startContainers</b>; tasks report to the AM.',
    'An application can have several attempts (<code>yarn.resourcemanager.am.max-attempts</code>, default 2).',
    'Kill: <code>yarn application -kill</code> frees all containers at once; too-big requests fail with InvalidResourceRequestException.',
]
FAQ = [
    ('What are the steps when a YARN application is submitted?', 'The client asks the ResourceManager for a new application ID, uploads the application\'s files (for MapReduce the jar, job.xml and splits) to a staging directory in HDFS, and submits an ApplicationSubmissionContext. The ResourceManager saves it, the scheduler admits it to a queue and allocates a container for the ApplicationMaster, and a NodeManager localizes the files and launches it. The ApplicationMaster registers, requests further containers through allocate calls, launches its tasks on NodeManagers, and unregisters with a final status when the work is done.'),
    ('What is the difference between an application and an application attempt in YARN?', 'An application is the whole submission. An attempt is one run of its ApplicationMaster. If the ApplicationMaster fails, the ResourceManager can start a new attempt with a new AM container, up to yarn.resourcemanager.am.max-attempts (2 by default). Attempt IDs look like appattempt_&lt;cluster timestamp&gt;_&lt;app number&gt;_000001.'),
    ('Why is my YARN application stuck in ACCEPTED?', 'ACCEPTED means the application is queued but its ApplicationMaster container has not been started. Common causes: the queue is at capacity, the queue\'s limit for ApplicationMasters (maximum-am-resource-percent) is reached, no NodeManager has enough free memory, or NodeManagers are unhealthy or lost. Check the queue and node pages in the ResourceManager UI and the application\'s diagnostics.'),
    ('What is the difference between state and final status of a YARN application?', 'State is the ResourceManager\'s lifecycle state (for example RUNNING or FINISHED). Final status is the outcome reported by the application: SUCCEEDED, FAILED, KILLED or UNDEFINED while running. An application can be in state FINISHED with final status FAILED, for example a MapReduce job whose tasks failed.'),
    ('What are MB-seconds in YARN?', 'The aggregate resource allocation of an application: for every container, its memory in MB multiplied by the seconds it was allocated, summed. vcore-seconds are the same for virtual cores. They appear in yarn application -status and the REST API and are used for chargeback and capacity planning.'),
]

PRACTICE_INTRO = 'Lifecycle exercises built on the real states and numbers from our lab.'
PROBLEMS = [
    dict(level='easy', title='Count the state changes', stmt='The RM log showed 7 application transitions and 10 attempt transitions; the NM log 5 for the AM container. How many in total?', inp='7 + 10 + 5',
         code='''print(7 + 10 + 5, "state changes for one 36-second job")
''', explain='22 logged transitions, all without anyone typing a command after submit.'),
    dict(level='easy', title='Time to register', stmt='The attempt was LAUNCHED at 06:25:43 and RUNNING at 06:25:48. How long did the AM take to start?', inp='two timestamps',
         code='''from datetime import datetime
f = "%H:%M:%S"
print((datetime.strptime("06:25:48", f) - datetime.strptime("06:25:43", f)).seconds, "s")
''', explain='5 s: mostly JVM start-up and reading the job configuration.'),
    dict(level='easy', title='Average memory held', stmt='33,224 MB-seconds over 36.2 seconds. What was the average memory held?', inp='33,224 MB-s · 36.2 s',
         code='''print(round(33224 / 36.2), "MB on average")
''', explain='About 918 MB: the 512 MB AM plus one 512 MB task container most of the time.'),
    dict(level='medium', title='Parse a state line', stmt='Extract object, from-state, to-state and event from a real RM log line.', inp='one log line',
         code='''import re
line = "06:25:48 RMAppImpl:921 - application_1792643020992_0136 State change from ACCEPTED to RUNNING on event = ATTEMPT_REGISTERED"
m = re.search(r"(\\S+) State change from (\\S+) to (\\S+) on event = (\\S+)", line)
print(m.groups())
''', explain='The four parts you need to build a timeline of any application from the RM log.'),
    dict(level='medium', title='Queue wait report', stmt='Given (startedTime, launchTime) in ms for three apps, print each app\'s wait for its AM in seconds.', inp='3 apps from the RM REST API',
         code='''apps = {"0136": (1792650343192, 1792650343300), "0137": (1792650380000, 1792650380050), "0138": (1792650400000, 1792650460500)}
for a, (s, l) in apps.items():
    print(a, f"{(l - s) / 1000:.1f} s")
''', explain='The first two started at once; the third waited a minute in ACCEPTED (illustrative times).'),
    dict(level='medium', title='Allowed transitions', stmt='Using a transition table, check whether ACCEPTED → FINISHED is allowed directly.', inp='small table',
         code='''allowed = {"ACCEPTED": {"RUNNING", "FAILED", "KILLED", "FINAL_SAVING"}, "RUNNING": {"FINAL_SAVING", "KILLED", "FAILED"}}
print("FINISHED" in allowed["ACCEPTED"])
''', explain='False: an app must pass through RUNNING (or fail/be killed). In YARN an ACCEPTED app can also be killed.'),
    dict(level='business', title='Cost of idle ApplicationMasters', stmt='A team submits 3,000 tiny jobs a day; each holds a 1,536 MB AM for 40 s. How many GB-hours a day are spent on AMs alone, and at ₹0.05 per GB-hour what does that cost per month?', inp='3,000 × 1,536 MB × 40 s',
         code='''gb_h = 3000 * 1536 * 40 / 1024 / 3600
print(f"{gb_h:.0f} GB-hours a day, Rs {gb_h * 0.05 * 30:,.0f} a month")
''', explain='About 50 GB-hours a day, ₹75 a month (illustrative), and the AMs also block queue slots. Batching jobs or uber mode for tiny jobs helps.'),
    dict(level='advanced', title='Rebuild a timeline', stmt='From a list of (time, object, from, to) log entries, print how long each state lasted for the application.', inp='app transitions from the RM log',
         code='''from datetime import datetime
log = [("06:25:43", "NEW"), ("06:25:43", "NEW_SAVING"), ("06:25:43", "SUBMITTED"), ("06:25:43", "ACCEPTED"),
       ("06:25:48", "RUNNING"), ("06:26:19", "FINAL_SAVING"), ("06:26:19", "FINISHING"), ("06:26:25", "FINISHED")]
t = lambda s: datetime.strptime(s, "%H:%M:%S")
for (a, s1), (b, _) in zip(log, log[1:]):
    print(f"{s1:12} {(t(b) - t(a)).seconds:3d} s")
''', explain='ACCEPTED 5 s, RUNNING 31 s, FINISHING 6 s (waiting for the AM container to exit). The log has 1-second resolution, so the fast states show 0.'),
]

SCN_INTRO = 'The YARN application lifecycle is asked in Hadoop, Spark and platform-engineering interviews.'
SCENARIOS = '''    <article class="scn">
      <div class="scn__head"><span class="scn__tag">YARN · basics</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>“What happens when you run hadoop jar?”</h4>
      <p class="scn__situation">The classic “walk me through it” question.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> the roles of client, RM, AM and NM.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>The client gets an application ID, uploads the jar, configuration and splits to HDFS staging, and submits to the ResourceManager.</li>
          <li>The RM allocates a container for the MRAppMaster; a NodeManager localizes the files and launches it; the AM registers.</li>
          <li>The AM requests containers (preferring nodes with the data), launches map and reduce tasks via NodeManagers, tracks them, then unregisters; logs are aggregated.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Troubleshooting · queues</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>Jobs sit in ACCEPTED for 30 minutes every morning</h4>
      <p class="scn__situation">The cluster dashboard shows 40% free memory at the same time.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> AM limits and queue limits, not just total capacity.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Free memory may belong to other queues; the submitting queue can be at its capacity or user limit.</li>
          <li>The queue's maximum-am-resource-percent may be reached by many small jobs, so no new AM can start.</li>
          <li>Check queue usage in the RM scheduler page, raise the AM share or queue capacity, or batch small jobs.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Reliability · attempts</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>“The node running the ApplicationMaster died. Is the job lost?”</h4>
      <p class="scn__situation">A follow-up on fault tolerance.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> application attempts and recovery.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>The RM notices the AM container is gone and starts a new attempt on another node, up to yarn.resourcemanager.am.max-attempts (default 2).</li>
          <li>The MapReduce AM can recover completed tasks from the previous attempt's history; other frameworks may restart the work.</li>
          <li>With RM HA and the state store, even an RM failover keeps the application.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Platform · cost</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>Design chargeback for a shared Hadoop cluster</h4>
      <p class="scn__situation">Five departments share one cluster and finance wants a monthly split.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> knowing where YARN usage data comes from.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Each finished application has memorySeconds and vcoreSeconds in the RM REST API (and the timeline/history servers).</li>
          <li>Collect them per queue or user daily, convert to GB-hours and vcore-hours, and price both.</li>
          <li>Reserve capacity costs separately; idle reserved capacity is a policy choice, not just usage.</li>
        </ul>
      </div></details>
    </article>
'''
