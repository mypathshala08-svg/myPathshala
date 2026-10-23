import os
HERE = os.path.dirname(os.path.abspath(__file__))
BODY = body(HERE).replace('{{PLAYGROUND}}', playground(dict(
    title='Two NameNodes, one in charge',
    intro='<p>An HA cluster with an active and a standby NameNode. Upload a file, then stop the active NameNode and watch the standby take over.</p>',
    racks=2, nodes=3, features=['upload', 'ha', 'fail'],
    preload=[dict(name='exam_results.csv', sizeMB=300)],
    **{'try': [
        dict(text='Upload a file so the cluster is busy.', on='upload-done'),
        dict(text='Press <b>Stop active NameNode</b>.', on='nn-stop'),
        dict(text='Watch the Event log: the standby becomes <b>ACTIVE</b> a few seconds later.', on='nn-failover'),
    ]},
)))
rd = lambda f: open(os.path.join(HERE, f)).read()
tx = lambda f: rd(f).strip()

META = dict(
    module='07-hdfs-advanced', lesson='01-namenode-high-availability', n='7.1',
    module_label='Module 7 · HDFS advanced',
    title='NameNode high availability (QJM and ZooKeeper)',
    desc='HDFS NameNode high availability on a real Hadoop 3.5.0 cluster with 2 NameNodes, 3 JournalNodes and ZooKeeper: kill the active NameNode while a client writes (failover in about 10 s, 12 of 12 writes succeed), freeze it and watch the JournalNodes reject the old active (“IPC\'s epoch 7 is less than the last promised epoch 8”), and lose the JournalNode majority. QJM, ZKFC, fencing, epochs, split-brain, haadmin. Playground, Python simulations, quiz and interview scenarios.',
    og_desc='Crash the NameNode, freeze it, starve it of JournalNodes: watch HDFS HA keep exactly one boss.',
    minutes=30, level='Advanced',
    lead='One NameNode means one machine whose failure stops the whole file system. HA runs a standby NameNode that follows every change through a quorum of JournalNodes, and ZooKeeper promotes it automatically. This lesson builds a real HA cluster in Docker, breaks it three different ways, and shows from the logs how Hadoop prevents two NameNodes from ever being active at once.',
    chips=['Real failover on a 9-container cluster', 'Split-brain prevented live', 'Runs in your browser (Python)'],
)

RUN = dict(
    heading='A quorum journal with epochs, in Python',
    intro='<p>Three JournalNodes each remember the highest epoch they have promised. A NameNode becomes the writer by getting a majority to promise its new epoch; an edit is accepted only by JNs that have not promised a higher one. Run it to replay our zombie test.</p>',
    code='''jns = {"jn1": 7, "jn2": 7, "jn3": 7}          # last promised epoch on each JournalNode
log = []

def become_active(name):
    epoch = max(jns.values()) + 1
    ok = [j for j in jns if jns[j] < epoch]
    if len(ok) >= 2:                          # majority of 3
        for j in ok:
            jns[j] = epoch
        print(f"{name} is ACTIVE with epoch {epoch}")
        return epoch
    print(f"{name} could not get a majority")

def write(name, epoch, edit):
    accepted = [j for j in jns if epoch >= jns[j]]
    if len(accepted) >= 2:
        log.append(edit)
        print(f"{name} wrote {edit!r} (accepted by {len(accepted)} JNs)")
    else:
        print(f"{name} REJECTED: epoch {epoch} is less than promised {max(jns.values())}")

e1 = 7                                        # nn1 was active with epoch 7, then froze
e2 = become_active("nn2")                     # nn2 takes over
write("nn2", e2, "mkdir /results")
write("nn1", e1, "delete /results")           # the zombie wakes up
print("edit log:", log)
''',
    anno=[
        ('    epoch = max(jns.values()) + 1', 'A new writer always asks for a higher epoch than any JournalNode has seen. Our lab epochs went 7 → 8.'),
        ('    accepted = [j for j in jns if epoch >= jns[j]]', 'A JournalNode refuses any write whose epoch is lower than what it promised: “IPC\'s epoch 7 is less than the last promised epoch 8”.'),
        ('    if len(accepted) >= 2:', 'A write needs a majority (2 of 3). That is why losing two JournalNodes stopped the whole cluster.'),
    ],
    tasks=[
        dict(label='1 · The zombie is rejected', hint='Press <b>Run</b>. Then add a second failover back to nn1 and write again with the new epoch.', code=None),
        dict(label='2 · How long is the outage?', hint='<b>Predict first:</b> failover time ≈ ZooKeeper session timeout + fencing + transition. Our ZKFC log shows 1 s for fence + transition.',
             code='''session_timeout_s = 10
fence_and_transition_s = 1
print("expected failover ~", session_timeout_s + fence_and_transition_s, "s (real lab: kill 15:44:25, active 15:44:36)")
'''),
        dict(label='3 · Majority sizes', hint='How many JournalNodes can fail for 3, 5 and 7 JNs? Why are even numbers pointless?',
             code='''for n in [3, 4, 5, 6, 7]:
    majority = n // 2 + 1
    print(f"{n} JNs: majority {majority}, can lose {n - majority}")
'''),
        dict(label='4 · Client failover', hint='A client tries nn1, then nn2. A dead address costs the 20 s connect timeout; a standby answers at once with StandbyException. Compute the extra delay for each case.',
             code='''connect_timeout = 20
cases = {"nn1 crashed (no reply)": connect_timeout, "nn1 is standby (fast error)": 0.05}
for case, wasted in cases.items():
    print(f"{case:30} extra delay before trying nn2: {wasted} s")
'''),
        dict(label='5 · Spot the error', hint='This check says the cluster is safe with 2 of 4 JournalNodes alive. Fix the majority test.',
             code='''alive, total = 2, 4
safe = alive >= total / 2
print("can write:", safe)
assert not safe, "2 of 4 is not a majority"
''', expect='error'),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run it on your PC: build and break an HA cluster',
    intro='<p>Create a folder <code>hdfs-ha-lab</code> with four files from the lesson\'s lab: <code>config</code> (the HA settings shown in Part 4), <code>docker-compose.yaml</code>, <code>nn.sh</code> and <code>zk.sh</code> (ZooKeeper runs from the jars inside the Hadoop image, so no extra image is needed). Start it with <code>docker compose -p lab7 up -d --scale datanode=3</code>, wait a minute, then run the three experiments. It needs about 4 GB of free RAM.</p>',
    items=[
        dict(title='Lab files: compose, NameNode start script, ZooKeeper', file='docker-compose.yaml',
             cmd=rd('lab/docker-compose.yaml') + '\n# ---- nn.sh ----\n' + rd('lab/nn.sh') + '\n# ---- zk.sh ----\n' + rd('lab/zk.sh') + '\n# Start:  docker compose -p lab7 up -d --scale datanode=3',
             output='''lab7-datanode-1 Up About a minute
lab7-datanode-2 Up About a minute
lab7-datanode-3 Up About a minute
lab7-jn1-1 Up About a minute
lab7-jn2-1 Up About a minute
lab7-jn3-1 Up About a minute
lab7-nn1-1 Up About a minute
lab7-nn2-1 Up About a minute
lab7-zk-1 Up About a minute
$ docker exec lab7-nn1-1 hdfs haadmin -getAllServiceState
nn1:8020                                           active
nn2:8020                                           standby''',
             note='Real output. The config file with all HA properties is in Part 4, step 1, plus <code>dfs.namenode.http-address</code> for both NameNodes, <code>dfs.journalnode.edits.dir</code>, <code>dfs.namenode.name.dir</code> and <code>dfs.replication=3</code>.'),
        dict(title='Experiment 1: crash the active during writes', file='ha_failover.sh',
             cmd=rd('ha_failover.sh') + '\n# Run:  bash ha_failover.sh   (then: docker start lab7-nn1-1)',
             output=tx('tx_failover.txt'), note='Real output: about 10 s to fail over, one slow write, 12 of 12 writes succeeded.'),
        dict(title='Experiment 2: freeze the active (zombie)', file='zombie.sh',
             cmd=rd('zombie.sh') + '\n# Run:  bash zombie.sh   (then: docker start lab7-nn1-1)',
             output=tx('tx_zombie.txt'), note='Real output: the JournalNodes refuse epoch 7 after promising epoch 8, and the old active shuts down.'),
        dict(title='Experiment 3: lose the JournalNode majority', file='jn_quorum.sh',
             cmd=rd('jn_quorum.sh') + '\n# Run:  bash jn_quorum.sh   then restore with:  bash restore.sh',
             output=tx('tx_jnquorum.txt'), note='Real output: with 1 of 3 JournalNodes, both NameNodes stop after the 20 s quorum timeout. restore.sh starts JNs, then NameNodes; all files were intact.'),
    ],
)

TRACE = dict(
    heading='An election in ZooKeeper',
    intro='<p>Two ZKFCs try to create the same ephemeral lock znode. The first wins; when its session expires the znode vanishes and the other wins.</p>',
    code='''znodes = {}
def try_lock(who):
    if "lock" not in znodes:
        znodes["lock"] = who
        return who + " is ACTIVE"
    return who + " stays standby"

print(try_lock("nn1"))
print(try_lock("nn2"))
del znodes["lock"]                 # nn1's session expired
print(try_lock("nn2"))
''',
    notes={3: 'Ephemeral :: The lock exists only while its owner\'s session lives.',
           9: 'Expiry :: After 10 s without contact, ZooKeeper deletes nn1\'s lock.'},
)

WORKED_INTRO = 'Three HA calculations: failover time, JournalNode sizing, and what an hour of NameNode downtime costs. Each runs live and is traced in memory.'
EXAMPLES = [
    dict(level='b', tag='Timing · failover', title='How long does a crash failover take?',
         problem='<p>From our ZKFC log: crash at 15:44:25, “Checking for any old active” at 15:44:34, “Successfully transitioned” at 15:44:35. Split the outage into detection and takeover.</p>',
         inp='15:44:25 · 15:44:34 · 15:44:35',
         approach=['Convert times to seconds.',
                   'Detection = check time − crash.',
                   'Takeover = transition − check.'],
         code='''to_s = lambda t: sum(int(x) * m for x, m in zip(t.split(":"), [3600, 60, 1]))
crash, check, done = to_s("15:44:25"), to_s("15:44:34"), to_s("15:44:35")
print("detection:", check - crash, "s   takeover:", done - check, "s   total:", done - crash, "s")
''', notes={2: 'Detection :: Almost all of it is the ZooKeeper session timeout.'},
         tryit='Lowering the session timeout speeds failover but risks false failovers during GC pauses or network blips.'),
    dict(level='i', tag='Sizing · JournalNodes', title='3 or 5 JournalNodes?',
         problem='<p>Each JournalNode is down for maintenance or failure about 1% of the time, independently. Estimate the chance that a majority is unavailable with 3 and with 5 JNs.</p>',
         inp='p(down) = 0.01',
         approach=['Majority lost when more than n/2 JNs are down at once.',
                   'Sum binomial probabilities.',
                   'Compare.'],
         code='''from math import comb
p = 0.01
for n in [3, 5]:
    need_down = n // 2 + 1
    lost = sum(comb(n, k) * p**k * (1 - p)**(n - k) for k in range(need_down, n + 1))
    print(f"{n} JNs: majority lost {lost:.6%} of the time")
''', notes={4: 'Quorum :: 2 of 3 or 3 of 5 must be down to stop writes.'},
         tryit='5 JNs are about 30 times safer here, but each edit must reach more nodes. Most clusters use 3; very large ones use 5.'),
    dict(level='a', tag='Cost · downtime', title='What does an hour without the NameNode cost?',
         problem='<p>Without HA, a NameNode hardware failure took 55 minutes to recover. 300 analysts and 40 production jobs depend on HDFS. Analyst time costs ₹900/hour; each delayed job costs ₹15,000 in penalties. HA hardware (an extra server and 3 JournalNodes) costs ₹6 lakh. How many such failures pay for HA?</p>',
         inp='55 min · 300 × ₹900/h · 40 × ₹15,000 · ₹6 lakh',
         approach=['Cost per outage = people + jobs.',
                   'Divide HA cost by outage cost.',
                   'Round up.'],
         code='''import math
outage = 300 * 900 * 55 / 60 + 40 * 15000
print(f"one outage costs about Rs {outage:,.0f}")
print("HA pays for itself after", math.ceil(600000 / outage), "outage(s)")
''', notes={2: 'Outage cost :: People waiting plus jobs missing deadlines.'},
         tryit='And HA also allows patching without downtime, which happens far more often than hardware failures.'),
]

QUIZ = mix([
    dict(q='In an HA pair, how many NameNodes serve client requests at a time?', options=['Exactly one, the active', 'Both, sharing load', 'None, JournalNodes do', 'Whichever is closer'], answer=0,
         why='One active; standbys only follow edits (Observers can serve reads in Hadoop 3).'),
    dict(q='What do JournalNodes store?', options=['Data blocks', 'The shared edit log of namespace changes', 'ZooKeeper locks', 'User passwords'], answer=1,
         why='The active writes each edit to them; the standby tails them.'),
    dict(q='With 3 JournalNodes, how many must accept an edit?', options=['1', '2', '3', 'Any'], answer=1,
         why='A majority. In our lab, 2 of 3 alive was fine; 1 of 3 stopped both NameNodes.'),
    dict(q='What triggered the automatic failover after we killed nn1?', options=['A DataNode', 'nn1\'s ZooKeeper session expiring, so nn2\'s ZKFC took the lock', 'The client', 'A cron job'], answer=1,
         why='About 10 s, the session timeout, then fence and transition in ~1 s.'),
    dict(q='Why did the frozen-then-woken nn1 shut down?', options=['Out of memory', 'The JournalNodes rejected its writes: its epoch 7 was below the promised epoch 8', 'ZooKeeper deleted its files', 'An admin killed it'], answer=1,
         why='Epochs make split-brain impossible on the shared log.'),
    dict(q='Which component is NOT used in a QJM HA cluster?', options=['ZKFC', 'JournalNode', 'Secondary NameNode', 'ZooKeeper'], answer=2,
         why='The standby does checkpointing; the Secondary NameNode is not used.'),
    dict(q='Clients should address HDFS as…', options=['hdfs://nn1:8020', 'hdfs://<nameservice>, e.g. hdfs://canteen', 'The ZooKeeper address', 'A DataNode address'], answer=1,
         why='The failover proxy provider tries the configured NameNodes behind the nameservice.'),
    dict(q='Which command switches the active role gracefully to nn1?', options=['hdfs dfsadmin -failover', 'hdfs haadmin -failover nn2 nn1', 'hdfs namenode -switch', 'zkfc -restart'], answer=1,
         why='Real: “Failover to NameNode at nn1 … successful” in 2.2 s.'),
])

REVISION = [
    'HA = one <b>active</b> + standby NameNode(s) per <b>nameservice</b>; no Secondary NameNode.',
    '<b>QJM</b>: edits to 3 or 5 <b>JournalNodes</b>; a majority must accept. Lose the majority → NameNodes stop (lab: “Timed out waiting 20000ms for a quorum”).',
    '<b>ZKFC</b> + <b>ZooKeeper</b>: ephemeral lock znode; session timeout 10 s → automatic failover (lab: ~10 s).',
    'Failover steps: lock → fence old active → transition standby to active.',
    '<b>Epochs</b> stop a zombie: “IPC\'s epoch 7 is less than the last promised epoch 8” → old active exits.',
    'Clients use the nameservice and a failover proxy provider; a dead address can cost a 20 s connect timeout.',
    'Commands: <code>hdfs haadmin -getAllServiceState</code>, <code>-failover nn2 nn1</code>, <code>hdfs zkfc -formatZK</code>, <code>namenode -bootstrapStandby</code>.',
    'Lab: 12/12 writes survived a crash; graceful failover 2.2 s.',
]
FAQ = [
    ('How does NameNode high availability work in Hadoop?', 'Two or more NameNodes serve one namespace: one active, the rest standby. The active writes every edit to a quorum of JournalNodes; standbys read those edits and receive block reports from all DataNodes, so they hold an up-to-date namespace and block map. ZooKeeper and a ZKFailoverController next to each NameNode run an election; when the active fails, a standby is fenced in and promoted automatically.'),
    ('What is the role of ZooKeeper in HDFS HA?', 'It provides the lock used for leader election. The active NameNode\'s ZKFC holds an ephemeral znode while its session is alive. If the NameNode or ZKFC dies or is partitioned, the session expires, the znode disappears, and another ZKFC acquires it and triggers failover. ZooKeeper does not store HDFS metadata.'),
    ('What is fencing and why is it needed?', 'Fencing ensures that a previously active NameNode can no longer act as active, for example by killing it over SSH. With QJM, epochs already prevent the old active from writing edits, but fencing also prevents it from serving stale reads to clients that still contact it.'),
    ('What is the difference between the Secondary NameNode and the Standby NameNode?', 'The Secondary NameNode only merges the edit log into a new fsimage (checkpointing) and cannot replace the NameNode. The Standby NameNode keeps a live, up-to-date copy of the namespace, performs checkpointing, and can become active within seconds.'),
    ('Why use an odd number of JournalNodes?', 'Writes need a majority. With 3 JNs one may fail; with 4 still only one may fail (majority 3), so the fourth adds cost without tolerance. 5 JNs tolerate two failures.'),
    ('What happens to clients during a failover?', 'Clients using the nameservice retry on the other NameNode. In-flight calls may be delayed by timeouts (in our lab one write took 22 s), but they complete once the new active is up; applications normally see only a pause.'),
]

PRACTICE_INTRO = 'HA exercises using the real timestamps, epochs and logs from the lab.'
PROBLEMS = [
    dict(level='easy', title='Failure tolerance', stmt='For 3 and 5 JournalNodes, print how many may fail while edits can still be written.', inp='3, 5',
         code='''for n in [3, 5]:
    t = n - (n // 2 + 1)
    print(n, "JNs tolerate", t, "failure" if t == 1 else "failures")
''', explain='3 JNs tolerate 1 failure; 5 tolerate 2.'),
    dict(level='easy', title='Parse haadmin output', stmt='Find the active NameNode from <code>hdfs haadmin -getAllServiceState</code> output.', inp='two lines',
         code='''out = """nn1:8020                                           standby
nn2:8020                                           active"""
print([l.split()[0] for l in out.splitlines() if l.split()[1] == "active"])
''', explain='nn2:8020. Monitoring scripts parse exactly this.'),
    dict(level='easy', title='Epoch sequence', stmt='The lab showed epochs 2, 3, 4 and 7, 8 across failovers. How many active-role changes happened between epoch 2 and epoch 8?', inp='2 → 8',
         code='''print(8 - 2, "new active writers")
''', explain='6: every transition to active (automatic or manual) takes a new epoch.'),
    dict(level='medium', title='Slowest write', stmt='From the client log, find the slowest write and its duration.', inp='write lines',
         code='''log = ["15:44:19 write 1 ok  (took 2 s)", "15:44:24 write 3 ok  (took 3 s)", "15:44:46 write 4 ok  (took 22 s)", "15:44:48 write 5 ok  (took 2 s)"]
slow = max(log, key=lambda l: int(l.split("took ")[1].split()[0]))
print(slow)
''', explain='Write 4, 22 s: the client\'s 20 s connect timeout to the dead nn1 address plus the retry on nn2.'),
    dict(level='medium', title='Detect a failover in JMX samples', stmt='Given HAState samples every 5 s from nn2, print when it became active.', inp='timestamps and states',
         code='''samples = [("15:44:25", "standby"), ("15:44:30", "standby"), ("15:44:35", "standby"), ("15:44:40", "active")]
prev = None
for t, s in samples:
    if prev and s != prev:
        print("state change at", t, prev, "->", s)
    prev = s
''', explain='A simple change detector is how failover alerts are built from /jmx.'),
    dict(level='medium', title='Quorum check', stmt='Write a function that says whether the active can write, given which of 3 JNs are up.', inp='[True, False, True]',
         code='''def can_write(up):
    return sum(up) > len(up) // 2
print(can_write([True, False, True]), can_write([True, False, False]))
''', explain='True with 2 of 3, False with 1 of 3, matching the lab.'),
    dict(level='business', title='Patching without downtime', stmt='Monthly OS patching restarts the NameNode for 20 minutes. Without HA, 300 analysts wait (₹900/hour each). What does HA save per year on patching alone?', inp='12 × 20 min × 300 × ₹900/h',
         code='''print(f"Rs {12 * 20 / 60 * 300 * 900:,.0f} per year")
''', explain='₹10.8 lakh a year (illustrative) from rolling patches with haadmin -failover.'),
    dict(level='advanced', title='Majority from votes', stmt='Simulate the epoch protocol: JNs promise a new epoch only if it is higher than their current one. Run two competing candidates with epochs 5 and 5 and show only one can win.', inp='3 JNs at epoch 4',
         code='''jns = [4, 4, 4]
def propose(name, epoch):
    yes = 0
    for i, e in enumerate(jns):
        if epoch > e:
            jns[i] = epoch; yes += 1
    return f"{name}: {yes} promises -> {'ACTIVE' if yes >= 2 else 'refused'}"
print(propose("nn1", 5))
print(propose("nn2", 5))
''', explain='nn1 gets 3 promises; nn2 with the same epoch gets 0 and is refused. Real QJM uses the same rule: a strictly higher epoch from a majority.'),
]

SCN_INTRO = 'HA is a favourite topic for Hadoop administrator and senior data engineer interviews.'
SCENARIOS = '''    <article class="scn">
      <div class="scn__head"><span class="scn__tag">HDFS · architecture</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>“Is the NameNode a single point of failure?”</h4>
      <p class="scn__situation">The classic question.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> Hadoop 1 vs Hadoop 2+ HA.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>In Hadoop 1, yes. Since Hadoop 2, HA runs an active and standby NameNode sharing edits through JournalNodes (QJM).</li>
          <li>ZooKeeper + ZKFC fail over automatically in seconds; epochs and fencing prevent split-brain.</li>
          <li>The Secondary NameNode was never a backup; it only checkpoints.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Operations · incident</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>Failovers happen every few days at peak hours</h4>
      <p class="scn__situation">No hardware is failing, but the active NameNode keeps losing its role around 2 pm.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> GC pauses vs ZooKeeper timeouts.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Check NameNode GC logs: a pause longer than the ZooKeeper session timeout (10 s default) makes ZKFC lose the lock, and the woken NameNode exits.</li>
          <li>Fix the cause: heap sizing, GC tuning, fewer objects (small files), RPC load from a misbehaving job.</li>
          <li>Only then consider a slightly longer session timeout; it also slows real failovers.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Design · placement</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>Where do you put JournalNodes and ZooKeeper?</h4>
      <p class="scn__situation">Designing a new 60-node cluster with 2 racks of masters.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> failure domains.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>3 JNs and 3 ZooKeeper servers on separate machines across racks, so one rack failure leaves a majority (ideally 3 racks for masters).</li>
          <li>The two NameNodes on different racks and power feeds; JN disks dedicated and fast (edits are synchronous).</li>
          <li>Use real fencing (sshfence or a power fencer) and monitor HAState.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Concepts · split-brain</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>“What if fencing fails? Can two NameNodes both be active?”</h4>
      <p class="scn__situation">A follow-up to test depth.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> QJM epochs.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>With QJM, a new active gets a higher epoch from a majority of JournalNodes; they reject writes from older epochs, so the old active cannot change the namespace and exits on its first write.</li>
          <li>It could briefly serve stale reads, which is why fencing is still configured.</li>
          <li>Real lab log: “IPC's epoch 7 is less than the last promised epoch 8”, then “Shutting down NameNode”.</li>
        </ul>
      </div></details>
    </article>
'''
