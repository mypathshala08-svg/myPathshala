import os
HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.dirname(HERE)
BODY = body(HERE)
rd = lambda f: open(os.path.join(UP, f)).read()


def section(name):
    """One '########## name' block of tx113.txt, without the header line."""
    out, on = [], False
    for line in rd('tx113.txt').splitlines():
        if line.startswith('##########'):
            on = line.split()[1] == name
            continue
        if on:
            out.append(line)
    return '\n'.join(out).strip()


ENV_FILES = ''.join(f'\n# ---- {f} ----\n' + '\n'.join('# ' + l for l in rd('lab/' + f).strip().split('\n'))
                    for f in ['sched-fifo.env', 'sched-capacity.env', 'sched-capacity-ulf.env',
                              'sched-capacity-preempt.env', 'sched-fair.env', 'fair-scheduler.xml'])

META = dict(
    module='11-yarn', lesson='03-schedulers-fifo-capacity-and-fair', n='11.3',
    module_label='Module 11 · YARN',
    title='Schedulers: FIFO, Capacity and Fair',
    desc='YARN schedulers compared on a real Hadoop 3.5.0 cluster: the same big job (30 × 40 s) and small job (2 × 5 s) under FIFO, the Capacity Scheduler with prod 70 / dev 30 queues, user-limit-factor 1 vs 4, preemption, and the Fair Scheduler. Small job 159.6 s under FIFO vs 24.2 s with queues; the big job 430 s because user-limit-factor 1 held it to 2,560 of 6,144 MB; preemption cut the wait from 51 s to 21 s; Fair rounded 384 MB maps up to 1 GB. Queue hierarchy, elasticity, ACLs, placement rules, refreshQueues, Python simulator, quiz and interview scenarios.',
    og_desc='A 10-second job waited 2 minutes behind a big one. Then we changed the scheduler five times and measured who won and who paid.',
    minutes=30, level='Intermediate',
    lead='When many teams share one cluster, the YARN scheduler decides whose task gets the next free container. This lesson runs the same pair of jobs under FIFO, three Capacity Scheduler set-ups and the Fair Scheduler on a real cluster, and turns the measured waits into rules for designing queues.',
    chips=['6 real scheduler runs', 'Queue architecture diagram', 'Runs in your browser (Python)'],
)

RUN = dict(
    heading='Simulate the four schedulers',
    intro='<p>A small model of our lab: 12 container slots, the big job (30 tasks × 40 s) at time 0 and the small job (2 tasks × 5 s) at 15 s. Each ApplicationMaster takes a slot and needs about 5 s before it asks for task containers. It is a model, so the seconds differ from the lab, but the pattern is the same: FIFO hurts the small job, capacity with user-limit-factor 1 hurts the big job, preemption gets the small job going fastest without holding the big job back for long.</p>',
    code='''import math

def simulate(policy, slots=12):
    jobs = {"big":   dict(arrive=0,  left=30, secs=40, run=[], am=None, end=None, queue="dev"),
            "small": dict(arrive=15, left=2,  secs=5,  run=[], am=None, end=None, queue="prod")}
    if policy == "fair":
        slots //= 2                 # Fair rounds 384 MB maps up to 1 GB: half as many containers
    preempted = 0
    for t in range(1000):
        for j in jobs.values():     # tasks that finished free their slot
            j["run"] = [e for e in j["run"] if e > t]
            if j["am"] is not None and j["left"] == 0 and not j["run"] and j["end"] is None:
                j["end"] = t
        active = [n for n, j in jobs.items() if j["arrive"] <= t and j["end"] is None]
        used = lambda n: len(jobs[n]["run"]) + (jobs[n]["am"] is not None)
        free = slots - sum(used(n) for n in jobs)
        def limit(n):
            if policy == "capacity-ulf1" and jobs[n]["queue"] == "dev":
                return math.ceil(0.3 * slots) + 1       # one user <= 1 x 30% of the cluster
            if policy == "fair" and len(active) == 2:
                return slots // 2
            return slots
        def wants(n):
            j = jobs[n]
            return j["am"] is None or (j["left"] > 0 and t >= j["am"] + 5)
        if policy == "preempt" and t >= 30 and wants("small") and free == 0 and jobs["big"]["run"]:
            jobs["big"]["run"].pop(); jobs["big"]["left"] += 1; preempted += 1; free += 1
        order = active                                  # FIFO: order of arrival
        if policy in ("capacity-ulf4", "preempt"):
            order = sorted(active, key=lambda n: jobs[n]["queue"] != "prod")   # prod is under its guarantee
        if policy == "fair":
            order = sorted(active, key=lambda n: used(n))                       # furthest below fair share first
        for n in order:
            while free > 0 and wants(n) and used(n) < limit(n):
                if jobs[n]["am"] is None:
                    jobs[n]["am"] = t
                else:
                    jobs[n]["run"].append(t + jobs[n]["secs"]); jobs[n]["left"] -= 1
                free -= 1
            if policy == "fifo" and wants(n):
                break                                   # nobody passes the head of the line
        if all(j["end"] is not None for j in jobs.values()):
            break
    s = jobs["small"]
    return jobs["big"]["end"], s["am"] - s["arrive"], s["end"] - s["arrive"], preempted

for p in ["fifo", "capacity-ulf1", "capacity-ulf4", "preempt", "fair"]:
    big, wait, small, pre = simulate(p)
    print(f"{p:14} big {big:4d} s | small: AM waited {wait:3d} s, took {small:3d} s | preempted {pre}")
''',
    anno=[
        ('                return math.ceil(0.3 * slots) + 1       # one user <= 1 x 30% of the cluster', 'user-limit-factor 1: our big job alone held 2,560 of 6,144 MB (5 containers) in the lab.'),
        ('        if policy == "preempt" and t >= 30 and wants("small") and free == 0 and jobs["big"]["run"]:', 'Preemption: after a wait, take a container back from the over-using queue. In the lab 2 were preempted.'),
        ('                break                                   # nobody passes the head of the line', 'FIFO in one line: if the first app still wants containers, nobody behind it gets any.'),
    ],
    tasks=[
        dict(label='1 · Four schedulers', hint='Press <b>Run</b>. Compare with the lab: FIFO small 159.6 s · Capacity small 24.2 s, big 430.0 s · ULF 4 small 121.5 s · preemption small 77.9 s.', code=None),
        dict(label='2 · Queue sizes', hint='<b>Predict first:</b> a cluster of 40 nodes × 64 GB. Queues prod 60, etl 25, adhoc 15. How much memory is each queue guaranteed, and how much can adhoc reach with maximum-capacity 40?',
             code='''cluster_gb = 40 * 64
for q, cap in {"prod": 60, "etl": 25, "adhoc": 15}.items():
    print(f"{q:6} guaranteed {cluster_gb * cap / 100:7.0f} GB")
print(f"adhoc can grow to {cluster_gb * 40 / 100:.0f} GB when others are idle")
'''),
        dict(label='3 · User limit', hint='A queue has 30% of a 6,144 MB cluster. How much can ONE user hold with user-limit-factor 1, 2 and 4 (the queue max is 100%)? This is the formula; in our lab the real job held 2,560 MB (5 containers, AM included) at factor 1, because the scheduler allows the container that crosses the limit and rounds to whole containers.',
             code='''cluster, cap, maxcap = 6144, 0.30, 1.00
for ulf in [1, 2, 4]:
    limit = min(cluster * cap * ulf, cluster * maxcap)
    print(f"user-limit-factor {ulf}: one user up to about {limit:5.0f} MB (formula)")
'''),
        dict(label='4 · Fair shares', hint='Three queues with weights 2, 1, 1 on 120 containers. What is each fair share? What if only two are active?',
             code='''weights = {"prod": 2, "etl": 1, "adhoc": 1}
for active in [["prod", "etl", "adhoc"], ["prod", "adhoc"]]:
    total = sum(weights[q] for q in active)
    print({q: round(120 * weights[q] / total) for q in active})
'''),
        dict(label='5 · Spot the error', hint='This check of a capacity-scheduler config should reject child queues that do not add up to 100%. It crashes on a typo in the queue list. Fix the key.',
             code='''conf = {"root.queues": "prod,dev", "root.prod.capacity": 70, "root.dev.capacity": 30}
total = sum(conf[f"root.{q}.capacity"] for q in conf["root.queue"].split(","))
print("OK" if total == 100 else f"children add up to {total}%")
''', expect='error'),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run it on your PC: switch schedulers and race two jobs',
    intro='<p>Use the Module 8 lab cluster. Put <code>rm.sh</code>, the <code>sched-*.env</code> files and <code>fair-scheduler.xml</code> in the <code>mr-lab</code> folder next to <code>docker-compose.yaml</code>. <code>rm.sh</code> recreates <b>only</b> the ResourceManager with another scheduler; HDFS and the NodeManagers keep running and re-register within a few seconds. Then copy <code>sched_lab.sh</code> into the namenode container and race the jobs. Each run takes 3–8 minutes.</p>',
    items=[
        dict(title='Switch the scheduler', file='rm.sh',
             cmd=rd('lab/rm.sh') + '\n# The files rm.sh combines with ./config:' + ENV_FILES + '\n\n# Run, in the mr-lab folder:\n#   bash rm.sh capacity',
             output=section('capacity').split('\nbig')[0],
             note='Real output. If you set capacity keys yourself, always keep root.queues and every capacity: a capacity-scheduler.xml with only some keys stops the ResourceManager with “Queue configuration missing child queue names for root” (we hit this in Lesson 11.4).'),
        dict(title='Race a big and a small job, under every scheduler', file='sched_lab.sh',
             cmd=rd('lab/sched_lab.sh') + '\n# In the mr-lab folder:\n#   docker cp sched_lab.sh lab8-namenode-1:/tmp/mr/\n#   bash rm.sh fifo     && docker exec lab8-namenode-1 bash /tmp/mr/sched_lab.sh default default\n#   bash rm.sh capacity && docker exec lab8-namenode-1 bash /tmp/mr/sched_lab.sh dev prod\n#   … capacity-preempt, fair, capacity-ulf, capacity-ulf-preempt the same way\n# The "probe" lines: start only the big job in dev and read\n#   curl -s http://resourcemanager:8088/ws/v1/cluster/metrics   every 15 s',
             output=rd('tx113.txt').strip(),
             note='Real output of all six runs plus the probe. Times will differ on your machine; the pattern (who waits, who is capped) will not. “capacity-preempt” with user-limit-factor 1 preempted nothing: dev never borrowed beyond its share, so there was nothing to take back.'),
    ],
)

TRACE = dict(
    heading='How the Capacity Scheduler limits one user',
    intro='<p>The limit our big job hit, computed step by step: a queue\'s guaranteed share, its maximum, and the user limit that applies when one user is alone in the queue.</p>',
    code='''cluster_mb = 3 * 2048
capacity, max_capacity, ulf = 0.30, 1.00, 1
guaranteed = cluster_mb * capacity
queue_max = cluster_mb * max_capacity
user_limit = min(guaranteed * ulf, queue_max)
containers = int(user_limit // 512) + 1
print(guaranteed, queue_max, user_limit, containers)
''',
    notes={3: 'Guarantee :: 30% of 6,144 MB = 1,843 MB.',
           5: 'User limit :: 1 × the guarantee, however big maximum-capacity is.',
           6: 'Rounding :: The scheduler lets a user go one container over; the lab showed 5 containers = 2,560 MB.'},
)

WORKED_INTRO = 'Four scheduler design problems from different industries: sizing queues, guarantee vs elasticity, the user limit, and the cost of preemption.'
EXAMPLES = [
    dict(level='b', tag='Telecom · queue sizing', title='Size the queues for a telecom cluster',
         problem='<p>A telecom company has 60 nodes with 96 GB for YARN each. Billing must be guaranteed 50%, fraud detection 20%, analytics 30%. How much memory does each queue get, and how many 4 GB containers is that?</p>',
         inp='60 × 96 GB · 50 / 20 / 30 · 4 GB containers',
         approach=['Cluster memory = nodes × memory per node.',
                   'Guarantee = cluster × capacity %.',
                   'Containers = guarantee ÷ container size.'],
         code='''cluster = 60 * 96
for q, cap in {"billing": 50, "fraud": 20, "analytics": 30}.items():
    gb = cluster * cap / 100
    print(f"{q:9} {gb:6.0f} GB -> {int(gb // 4)} containers of 4 GB")
''', notes={3: 'Guarantee :: Capacities at one level must add up to 100%.'},
         tryit='Add a 10% “ds” queue for data science. Which queue would you shrink, and why?'),
    dict(level='i', tag='E-commerce · elasticity', title='Guarantee or elasticity?',
         problem='<p>An online retailer\'s dashboard queue is guaranteed 40% of 1,000 containers but is busy only 4 hours a day. The data-science queue (30%) has maximum-capacity 30%. How many container-hours does data science lose per day by not being elastic up to 70% during the 20 idle hours?</p>',
         inp='1,000 containers · idle 40% for 20 h',
         approach=['Idle capacity = 40% × 1,000 for 20 hours.',
                   'Data science could use it only if maximum-capacity allows.',
                   'Loss = idle containers × hours.'],
         code='''idle_containers = 1000 * 0.40
hours = 20
print(f"{idle_containers * hours:,.0f} container-hours a day left idle")
''', notes={1: 'Idle :: Unused guarantee is wasted unless another queue may borrow it.'},
         tryit='Raise data science\'s maximum-capacity to 70% and turn on preemption: dashboards still get their 40% back within seconds.'),
    dict(level='i', tag='University · user limit', title='One PhD student, one department queue',
         problem='<p>The CSE department queue is guaranteed 25% of a 400-container cluster with maximum 60%. With user-limit-factor 1, 2 and 3, how many containers can one student take when the queue is otherwise empty?</p>',
         inp='400 containers · capacity 25% · max 60%',
         approach=['Guarantee = 100 containers.',
                   'User limit = factor × guarantee.',
                   'Never more than maximum-capacity (240).'],
         code='''guarantee, qmax = 400 * 0.25, 400 * 0.60
for ulf in [1, 2, 3]:
    print(f"user-limit-factor {ulf}: up to {min(guarantee * ulf, qmax):.0f} containers")
''', notes={3: 'Cap :: The queue maximum wins over a large factor.'},
         tryit='Our lab had the opposite surprise: ULF 1 held a lone job to 30% and made it 2× slower than under FIFO.'),
    dict(level='a', tag='Banking · preemption cost', title='What does preemption cost?',
         problem='<p>A bank\'s risk queue preempts 50 containers from the adhoc queue each morning. On average a preempted task had run 6 minutes of a 10-minute task, and its work is lost. How many container-minutes are redone per day, and per year (250 working days)? Compare with our lab: 2 containers preempted made the big job 7.8 s slower (207.6 → 215.4 s).</p>',
         inp='50 containers × 6 min lost · 250 days',
         approach=['Lost work per container = time already run.',
                   'Per day = containers × lost minutes.',
                   'Per year = per day × working days.'],
         code='''per_day = 50 * 6
print(f"{per_day} container-minutes a day, {per_day * 250 / 60:,.0f} container-hours a year")
print(f"lab: big job {215.4 - 207.6:.1f} s slower, small job {121.5 - 77.9:.1f} s faster")
''', notes={1: 'Waste :: Preempted work is redone, so preemption is a price paid for meeting guarantees.'},
         tryit='Short tasks make preemption cheap: what if tasks were 1 minute instead of 10?'),
]

QUIZ = mix([
    dict(q='What does the YARN scheduler decide?', options=['Which DataNode stores a block', 'Which application gets each free container', 'How many reducers a job has', 'When a NodeManager is declared dead'], answer=1,
         why='It is the pluggable part of the ResourceManager that allocates containers.'),
    dict(q='Under FIFO in our lab, how long did the small job wait for its ApplicationMaster?', options=['0.1 s', '120.4 s', '20.7 s', '51.0 s'], answer=1,
         why='Every free container went to the big job while it still had tasks waiting.'),
    dict(q='Which scheduler is the default in Apache Hadoop 3?', options=['FIFO', 'Capacity Scheduler', 'Fair Scheduler', 'DRF Scheduler'], answer=1,
         why='yarn.resourcemanager.scheduler.class defaults to the CapacityScheduler.'),
    dict(q='dev had capacity 30 and maximum-capacity 100, yet the big job held only 2,560 of 6,144 MB. Why?', options=['The NodeManagers were full', 'user-limit-factor 1 limits one user to 1 × the queue capacity', 'Preemption was off', 'The AM asked for too little'], answer=1,
         why='With user-limit-factor 4 the same job used the whole cluster and finished in 207.6 s instead of 430.0 s.'),
    dict(q='What does maximum-capacity control?', options=['The guaranteed share', 'How far a queue may grow by borrowing idle resources', 'The number of users', 'The container size'], answer=1,
         why='Capacity is the guarantee; maximum-capacity is the elastic ceiling.'),
    dict(q='What did preemption change in our lab?', options=['Nothing', 'The small job\'s wait fell from 51.0 s to 20.7 s; 2 dev containers were killed', 'The big job failed', 'Both jobs got faster'], answer=1,
         why='Preempted work is redone: the big job took 215.4 s instead of 207.6 s.'),
    dict(q='Why did the Fair Scheduler run only 6 containers for 384 MB maps?', options=['Fair limits apps to 6 containers', 'Fair rounds requests up to its 1,024 MB increment', 'The cluster lost nodes', 'DRF counted vcores'], answer=1,
         why='Our lab\'s small containers don\'t suit Fair\'s default increment-allocation of 1 GB.'),
    dict(q='How do you apply a changed capacity-scheduler.xml without restarting the RM?', options=['yarn node -refresh', 'yarn rmadmin -refreshQueues', 'hdfs dfsadmin -refreshNodes', 'mapred queue -reload'], answer=1,
         why='Queues can be added or resized live; removing a queue needs it stopped first.'),
])

REVISION = [
    'The <b>scheduler</b> in the ResourceManager decides who gets each free container: <b>FIFO</b>, <b>Capacity</b> (default in Hadoop 3) or <b>Fair</b>.',
    '<b>Capacity</b>: queue tree; <code>capacity</code> = guarantee, <code>maximum-capacity</code> = elastic ceiling, <code>user-limit-factor</code> = how many × capacity one user may hold (default 1).',
    'Lab: FIFO small job waited 120.4 s (159.6 s total); Capacity small 24.2 s but big 430.0 s (held to 2,560 MB by ULF 1); ULF 4: big 207.6 s, small 121.5 s; + preemption: small 77.9 s, 2 containers preempted.',
    'Without preemption, guarantees are honoured only as containers <b>finish</b>; preemption kills over-share containers and their work is redone.',
    '<b>Fair</b>: weighted fair share, min/max resources, DRF policy; it rounds to 1 GB by default (6 containers in our lab).',
    'Choose a queue: <code>-D mapreduce.job.queuename=prod</code>, placement rules, ACLs; apply changes with <code>yarn rmadmin -refreshQueues</code>.',
    'A partial <code>capacity-scheduler.xml</code> stops the RM: “Queue configuration missing child queue names for root”.',
]
FAQ = [
    ('What is the difference between the Capacity and Fair schedulers in YARN?', 'The Capacity Scheduler gives each queue a guaranteed percentage of the cluster, lets queues borrow idle resources up to a maximum, and limits how much a single user may take; it is the default in Hadoop 3 and the standard in Cloudera\'s platform. The Fair Scheduler shares resources so that all running applications or weighted queues get an equal share over time, with minimum and maximum shares. Both support hierarchical queues and preemption; they differ mainly in how they decide who is most entitled to the next container.'),
    ('What is user-limit-factor in the Capacity Scheduler?', 'It is the multiple of a queue\'s configured capacity that a single user may use. The default of 1 means one user can never use more than the queue\'s guarantee, even if maximum-capacity is higher and the cluster is idle. In our lab a lone job in a 30% queue held only 2,560 of 6,144 MB and took 430 s; with user-limit-factor 4 it used the whole cluster and took 207.6 s.'),
    ('What is preemption in YARN?', 'Preemption lets the ResourceManager take containers back from queues that use more than their guaranteed share when another queue is starved. The scheduling monitor (ProportionalCapacityPreemptionPolicy for the Capacity Scheduler) first asks the application to release containers and kills them after a timeout. The killed tasks are rerun, so preemption trades some wasted work for meeting guarantees.'),
    ('How do I submit a job to a specific YARN queue?', 'For MapReduce use -D mapreduce.job.queuename=prod (or set it in the job configuration), for Spark use --queue prod, and for Hive on Tez set tez.queue.name. Administrators can also map users and groups to queues with placement rules, and queue ACLs control who may submit.'),
    ('Why is my small job stuck in ACCEPTED?', 'ACCEPTED means the ResourceManager has the application but its ApplicationMaster has no container yet. Usually the queue is full (or at its maximum-am-resource-percent), the user has reached the user limit, or, under FIFO, an earlier application is still being served. Check the queue\'s use with mapred queue -list or the RM web UI\'s Scheduler page; in our lab a small job waited 120.4 s in ACCEPTED under FIFO.'),
]

PRACTICE_INTRO = 'Scheduler exercises built on the six real runs.'
PROBLEMS = [
    dict(level='easy', title='How much slower?', stmt='The small job needs about 10 s of work. How many times longer did it take under FIFO (159.6 s) and with Capacity queues (24.2 s)?', inp='159.6 s · 24.2 s · 10 s',
         code='''for name, t in [("FIFO", 159.6), ("Capacity", 24.2)]:
    print(f"{name}: {t / 10:.1f}x the work time")
''', explain='About 16× under FIFO and 2.4× with queues (the rest is AM start-up and container launches).'),
    dict(level='easy', title='Guaranteed share', stmt='Our cluster has 6,144 MB. What are prod\'s and dev\'s guaranteed shares in MB?', inp='70% · 30%',
         code='''print("prod", 6144 * 0.70, "MB, dev", 6144 * 0.30, "MB")
''', explain='4,300.8 and 1,843.2 MB. The lone big job held 2,560 MB: its user limit plus one container of rounding.'),
    dict(level='easy', title='Cost of the cap', stmt='How much longer did the big job take with user-limit-factor 1 (430.0 s) than with 4 (207.6 s)?', inp='430.0 · 207.6',
         code='''print(f"{430.0 - 207.6:.1f} s longer, {430.0 / 207.6:.2f}x")
''', explain='222.4 s longer: twice as slow, with most of the cluster idle.'),
    dict(level='medium', title='Preemption trade', stmt='Preemption saved the small job some seconds and cost the big job some. Compute both from the ULF 4 runs.', inp='small 121.5 → 77.9 · big 207.6 → 215.4',
         code='''print(f"small saved {121.5 - 77.9:.1f} s, big lost {215.4 - 207.6:.1f} s")
''', explain='43.6 s saved for 7.8 s lost: preemption pays off when the waiting job matters more.'),
    dict(level='medium', title='Containers per queue', stmt='A node manager offers 48 GB. With 20 nodes and 3 GB containers, how many containers does a 35% queue get?', inp='20 × 48 GB · 3 GB · 35%',
         code='''total = 20 * 48 // 3
print(int(total * 0.35), "of", total, "containers")
''', explain='112 of 320 containers guaranteed.'),
    dict(level='medium', title='Fair with weights', stmt='Queues prod (weight 3) and adhoc (weight 1) are both busy on 200 containers. What are their fair shares? What if adhoc is idle?', inp='weights 3 : 1 · 200',
         code='''for active in [{"prod": 3, "adhoc": 1}, {"prod": 3}]:
    t = sum(active.values())
    print({q: 200 * w // t for q, w in active.items()})
''', explain='150 and 50; alone, prod may use all 200.'),
    dict(level='business', title='Buy nodes or add preemption?', stmt='Reports miss their SLA 3 mornings a month because adhoc jobs hold the cluster. Option A: 10 more nodes at ₹6 lakh each. Option B: enable preemption, costing about 2% of adhoc compute (adhoc uses 40% of a 50-node cluster). Which is cheaper per year if a node-year costs ₹1.5 lakh to run?', inp='A: 10 × ₹6 L + 10 × ₹1.5 L/yr · B: 2% × 40% × 50 nodes',
         code='''a = 10 * 6 + 10 * 1.5
b = 0.02 * 0.40 * 50 * 1.5
print(f"A: Rs {a:.0f} lakh in year 1, B: Rs {b:.1f} lakh a year of redone work")
''', explain='About ₹75 lakh vs about ₹0.6 lakh (illustrative). Configure before you buy.'),
    dict(level='advanced', title='Design the queues', stmt='Write a capacity layout for root → prod (etl, reports), adhoc, ds, and check that each level adds up to 100%.', inp='a nested dict of capacities',
         code='''tree = {"prod": (60, {"etl": 70, "reports": 30}), "adhoc": (25, {}), "ds": (15, {})}
print("root level:", sum(c for c, _ in tree.values()))
for q, (c, kids) in tree.items():
    if kids:
        print(f"{q} children:", sum(kids.values()), {k: f"{c * v / 100:.0f}% of cluster" for k, v in kids.items()})
''', explain='Both levels add up to 100; etl gets 42% and reports 18% of the whole cluster. Child capacities are percentages of the parent.'),
]

SCN_INTRO = 'Scheduler questions come up for every Hadoop admin and data-engineering role, usually as “a job is stuck” or “design the queues”.'
SCENARIOS = '''    <article class="scn">
      <div class="scn__head"><span class="scn__tag">YARN · basics</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>“Explain FIFO, Capacity and Fair schedulers”</h4>
      <p class="scn__situation">A standard question in Hadoop interviews.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> one clear idea per scheduler and the default.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>FIFO serves apps in arrival order; a big job blocks small ones (our small job waited 120 s).</li>
          <li>Capacity (default in Hadoop 3): queues with guaranteed %, elastic up to maximum-capacity, user limits, preemption.</li>
          <li>Fair: everyone running converges to an equal or weighted share; also queues and preemption.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Operations · debugging</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>A job uses only a third of an idle cluster</h4>
      <p class="scn__situation">The queue's maximum-capacity is 100% and nothing else is running, yet the job won't grow.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> user limits.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Check user-limit-factor: at the default of 1, one user can't exceed the queue's capacity.</li>
          <li>Also check maximum-am-resource-percent and minimum-user-limit-percent.</li>
          <li>Raise the factor for that queue and run yarn rmadmin -refreshQueues; in our lab that cut the job from 430 s to 208 s.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Design · SLAs</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>Reports must finish by 7 AM, but analysts want the whole cluster</h4>
      <p class="scn__situation">You run a shared cluster for a bank.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> guarantees, elasticity and preemption together.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Reports queue with enough guaranteed capacity for the SLA (measured from past runs), analysts' queue elastic up to 100%.</li>
          <li>Enable preemption so borrowed capacity comes back in seconds; exempt the reports queue from being preempted.</li>
          <li>Limit AM share and user limits in the analysts' queue; monitor queue wait times and SLA misses.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Migration · schedulers</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>Moving from the Fair Scheduler to the Capacity Scheduler</h4>
      <p class="scn__situation">Your company is moving from an old CDH cluster to CDP.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> what changes in behaviour.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Translate weights and min/max shares into capacities and maximum-capacities (tools exist, e.g. fs2cs), then review user limits, which behave differently.</li>
          <li>Check container sizing: Fair's increment (1 GB by default) vs Capacity's minimum allocation changes how many containers fit.</li>
          <li>Replay a typical day's jobs on a test cluster and compare queue waits before switching.</li>
        </ul>
      </div></details>
    </article>
'''
