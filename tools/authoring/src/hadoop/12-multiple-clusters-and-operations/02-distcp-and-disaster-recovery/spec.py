import os
HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.dirname(HERE)
BODY = body(HERE)
rd = lambda f: open(os.path.join(UP, f)).read()

META = dict(
    module='12-multiple-clusters-and-operations', lesson='02-distcp-and-disaster-recovery', n='12.2',
    module_label='Module 12 · Multiple clusters and operations',
    title='DistCp and disaster recovery',
    desc='DistCp and Hadoop disaster recovery on two real Hadoop 3.5.0 clusters: a full copy (170 MB, 5 maps, 25.5 s), the silent skip of a changed file with plain DistCp, -update (size + checksum), -delete, snapshot-diff sync (-diff s1 s2: 1 file, rename replayed), -bandwidth, and a failover drill that shows the RPO. RPO and RTO, active-passive vs active-active, -p preserve flags, checksums, cloud targets, architecture diagram, animations, Python simulation, quiz and interview scenarios.',
    og_desc='Plain DistCp said "success" and skipped a changed file. Sync two real clusters properly, use snapshot diffs, and run a DR drill.',
    minutes=32, level='Advanced',
    lead='A second cluster only protects you if it holds the right data. This lesson copies a production folder to a real DR cluster with DistCp, catches the classic silent skip, keeps the copy in sync with -update, -delete and snapshot diffs, and runs a failover drill that shows exactly what a disaster would cost.',
    chips=['Two real clusters', 'Architecture diagram + 2 animations', 'Runs in your browser (Python)'],
)

RUN = dict(
    heading='Decide like DistCp',
    intro='<p>This model reproduces our second run. Each file has a size and a checksum. Plain DistCp only checks whether the name exists at the target; <code>-update</code> also compares size and checksum; <code>-delete</code> removes target files the source no longer has.</p>',
    code='''prod = {"canteen_orders.csv": (4692009, "c1"), "menu.csv": (143, "m2"),
        "orders_day31.csv": (70147, "d1"), "orders_x30.csv": (140759640, "x1"),
        "student_orders.csv": (19418699, "s1")}
dr = {"canteen_orders.csv": (4692009, "c1"), "menu.csv": (143, "m1"),
      "feedback.txt": (5093962, "f1"), "orders_x30.csv": (140759640, "x1"),
      "student_orders.csv": (19418699, "s1")}

def plan(src, dst, update=False, delete=False):
    copy, skip = [], []
    for name, (size, crc) in src.items():
        if name not in dst:
            copy.append(name)
        elif update and dst[name] != (size, crc):   # size OR checksum differs
            copy.append(name)
        else:
            skip.append(name)
    gone = [n for n in dst if n not in src] if delete else []
    return copy, skip, gone

for opts in [{}, {"update": True}, {"update": True, "delete": True}]:
    c, s, g = plan(prod, dr, **opts)
    print(opts or "no options", "-> copy", c, "| skipped", len(s), "| delete", g)
''',
    anno=[
        ('        elif update and dst[name] != (size, crc):   # size OR checksum differs', 'Our menu.csv: same 143 bytes, different checksum. Only -update notices.'),
        ('    gone = [n for n in dst if n not in src] if delete else []', '-delete is what removed feedback.txt from the DR copy.'),
    ],
    tasks=[
        dict(label='1 · Three ways to sync', hint='Press <b>Run</b>. Which run leaves DR with the old chai price?', code=None),
        dict(label='2 · Snapshot diff to plan', hint='Turn a snapshotDiff report into actions: + copy, - delete, R rename, M ignore (a modified folder).',
             code='''diff = ["M\\t.", "+\\t./orders_2026-11-01.csv", "R\\t./orders_day31.csv -> ./orders_2026-10-31.csv"]
for line in diff:
    kind, path = line.split("\\t")
    if kind == "+":
        print("copy  ", path)
    elif kind == "-":
        print("delete", path)
    elif kind == "R":
        old, new = path.split(" -> ")
        print("rename", old, "to", new, "(no bytes copied)")
'''),
        dict(label='3 · RPO from a schedule', hint='<b>Predict first:</b> syncs at 01:00 and 13:00; the disaster strikes at 12:40. How many hours of data are lost? What about hourly syncs?',
             code='''def lost_hours(sync_hours, disaster):
    last = max(h for h in sync_hours if h <= disaster)
    return disaster - last
print("twice a day:", round(lost_hours([1, 13], 12 + 40 / 60), 2), "h")
print("hourly     :", round(lost_hours(list(range(24)), 12 + 40 / 60), 2), "h")
'''),
        dict(label='4 · Will the sync fit?', hint='2 TB changes per day; the link between sites gives 400 MB/s, but DistCp may use only half during the night window of 6 h. Does it fit?',
             code='''changed_mb = 2 * 1024 * 1024
rate = 400 / 2
hours = changed_mb / rate / 3600
print(f"{hours:.1f} h needed, window 6 h ->", "fits" if hours <= 6 else "does NOT fit")
'''),
        dict(label='5 · Spot the error', hint='This plan should copy changed files, but it crashes on a file that exists only at the target. Fix the lookup.',
             code='''src = {"a.csv": (10, "x")}
dst = {"a.csv": (10, "y"), "old.csv": (5, "z")}
for name in dst:
    if src[name] != dst[name]:
        print("copy", name)
''', expect='error'),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run it on your PC: two clusters, one sync, one drill',
    intro='<p>You need the Module 8 lab (prod) and the Lesson 7.2 federation lab (DR) running together; stop the Module 5 lab to save memory. <code>join_clusters.sh</code> connects only prod\'s three workers to the DR network: both clusters use names like <code>namenode</code>, and when we joined every container to both networks, a client resolved <code>resourcemanager</code> to the wrong network and got "Connection refused". Then run <code>distcp_lab.sh</code> inside <code>lab8-worker1-1</code>. It takes about 4 minutes.</p>',
    items=[
        dict(title='Connect the clusters, then sync and drill', file='distcp_lab.sh',
             cmd='# ---- join_clusters.sh (run on your PC) ----\n' + rd('lab/join_clusters.sh') + '\n# ---- distcp_lab.sh ----\n' + rd('lab/distcp_lab.sh') + '\n# Run:  docker cp distcp_lab.sh lab8-worker1-1:/tmp/ && docker exec lab8-worker1-1 bash /tmp/distcp_lab.sh',
             output=rd('tx122.txt').strip(),
             note='Real output. Timings vary. Notice step 2: plain DistCp reports success with "Files Skipped=4" while the DR menu still has the old price.'),
    ],
)

TRACE = dict(
    heading='Applying a snapshot diff',
    intro='<p>Follow a DR folder as the diff is applied: a rename moves a name without copying bytes, and only the new file is copied.</p>',
    code='''dr = {"orders_day31.csv": 70147, "menu.csv": 143}
diff = [("R", "orders_day31.csv", "orders_2026-10-31.csv"), ("+", "orders_2026-11-01.csv", 28086)]
copied = 0
for op in diff:
    if op[0] == "R":
        dr[op[2]] = dr.pop(op[1])
    elif op[0] == "+":
        dr[op[1]] = op[2]
        copied += op[2]
print(sorted(dr), copied)
''',
    notes={6: 'Rename :: The DR NameNode just renames the file; no data crosses the network.',
           9: 'Copy :: Only new or modified files are copied: 28,086 bytes in our lab.'},
)

WORKED_INTRO = 'Four DR calculations from different industries: RPO and RTO, the sync window, snapshot savings and cost.'
EXAMPLES = [
    dict(level='b', tag='Banking · RPO/RTO', title='Does the nightly sync meet the regulator?',
         problem='<p>A bank\'s policy says RPO ≤ 4 hours and RTO ≤ 2 hours. Today it syncs once a night at 02:00 and failover takes 90 minutes. What is the worst-case RPO, and does it comply?</p>',
         inp='sync every 24 h · failover 90 min · limits 4 h / 2 h',
         approach=['Worst case: disaster just before the next sync.',
                   'RPO = sync interval; RTO = failover time.',
                   'Compare with the limits.'],
         code='''interval_h, failover_min = 24, 90
rpo, rto = interval_h, failover_min / 60
print(f"RPO {rpo} h (limit 4) -> {'OK' if rpo <= 4 else 'FAIL'}; RTO {rto} h (limit 2) -> {'OK' if rto <= 2 else 'FAIL'}")
print("syncs needed per day for RPO 4 h:", 24 // 4)
''', notes={2: 'Worst case :: Data written just after a sync waits a full interval.'},
         tryit='RTO passes, RPO fails. Six snapshot-diff syncs a day (every 4 hours) fix it.'),
    dict(level='i', tag='Telecom · bandwidth', title='How long does the first copy take?',
         problem='<p>A telecom starts DR for 1.2 PB of call records. The inter-site link is 10 Gbit/s; DistCp may use 60% of it. How many days does the first full copy take?</p>',
         inp='1.2 PB · 10 Gbit/s · 60% usable',
         approach=['Convert the link to bytes per second.',
                   'Divide data by usable rate.',
                   'Convert to days.'],
         code='''data_bytes = 1.2 * 1024**5
rate = 10e9 / 8 * 0.60
days = data_bytes / rate / 86400
print(f"{days:.1f} days")
''', notes={2: 'Bits vs bytes :: 10 Gbit/s is 1.25 GB/s before overheads.'},
         tryit='About 21 days. That is why big first copies are often seeded by shipping disks or done in stages, with -update runs afterwards.'),
    dict(level='i', tag='E-commerce · snapshots', title='How much listing does a snapshot diff save?',
         problem='<p>A folder holds 50 million files; 20,000 change per day. A plain -update run must compare every file (say 2 ms of NameNode work per file on each side); a -diff run asks only for the changes. Compare the comparison time.</p>',
         inp='50,000,000 files · 20,000 changes · 2 ms per file',
         approach=['-update: every file is listed and compared on both clusters.',
                   '-diff: the NameNode returns only the changes.',
                   'Compare.'],
         code='''files, changed, ms = 50_000_000, 20_000, 2
update_h = files * ms * 2 / 1000 / 3600
diff_min = changed * ms * 2 / 1000 / 60
print(f"-update compare: {update_h:.0f} h   -diff: {diff_min:.1f} min")
''', notes={3: 'Both sides :: Source and target listings are both needed for -update.'},
         tryit='The numbers are a simple model, but the gap is real: in our lab -diff ran 1 map for 1 file. Big clusters schedule hourly diffs that a full comparison could never finish.'),
    dict(level='a', tag='Insurance · cost', title='Backup, active–passive or active–active?',
         problem='<p>An insurer loses about ₹5 lakh of business per hour of downtime and ₹2 lakh per hour of lost data. Option A, cloud backup: ₹40 lakh/yr, RTO 48 h, RPO 24 h. Option B, active–passive DR: ₹1.6 crore/yr, RTO 2 h, RPO 1 h. Option C, active–active: ₹4 crore/yr, RTO 0.1 h, RPO 0.1 h. Expect one disaster every 5 years. Which is cheapest in total?</p>',
         inp='3 options · 0.2 disasters per year',
         approach=['Expected yearly loss = 0.2 × (RTO × downtime cost + RPO × data cost).',
                   'Total = running cost + expected loss.',
                   'Compare.'],
         code='''opts = {"A backup": (40, 48, 24), "B active-passive": (160, 2, 1), "C active-active": (400, 0.1, 0.1)}
for name, (cost_lakh, rto, rpo) in opts.items():
    loss = 0.2 * (rto * 5 + rpo * 2)
    print(f"{name:18} run {cost_lakh:4} lakh + expected loss {loss:5.1f} lakh = {cost_lakh + loss:6.1f} lakh/yr")
''', notes={3: 'Expected loss :: Probability times impact; regulators may also set hard limits.'},
         tryit='Numbers are illustrative. Here backup is cheapest on paper, but if a regulator demands RPO ≤ 4 h, only B or C are allowed, and B wins.'),
]

QUIZ = mix([
    dict(q='How does DistCp copy files?', options=['With one big client process', 'As a map-only MapReduce job: map tasks copy files in parallel', 'Through the NameNode', 'With rsync over SSH'], answer=1,
         why='Our first copy launched 5 map tasks for 5 files.'),
    dict(q='In our lab, plain DistCp (no options) ran after menu.csv changed but kept its size. What happened?', options=['It copied menu.csv', 'It skipped menu.csv because the name already existed', 'It failed with a checksum error', 'It deleted menu.csv on DR'], answer=1,
         why='Files Copied=1 (the new file), Files Skipped=4, and the job still succeeded.'),
    dict(q='What does -update compare?', options=['Only names', 'Size and checksum', 'Modification time only', 'Owner and group'], answer=1,
         why='Equal size (143 bytes) but different checksum, so menu.csv was copied.'),
    dict(q='What does -delete do?', options=['Deletes the source after copying', 'Removes target files that no longer exist at the source', 'Deletes failed files', 'Deletes snapshots'], answer=1,
         why='feedback.txt, deleted on prod, was removed from DR.'),
    dict(q='What does -diff s1 s2 need?', options=['Nothing special', 'Snapshot s1 on both sides (the target unchanged since then) and s2 on the source', 'The same Hadoop version on both clusters', 'Kerberos'], answer=1,
         why='Then DistCp applies only the changes reported by the NameNode.'),
    dict(q='What is the RPO?', options=['How long recovery takes', 'How much recent data you can afford to lose, measured in time', 'The number of replicas', 'The DR cluster size'], answer=1,
         why='In our drill, the file written after the last sync was the loss.'),
    dict(q='Two clusters use different block sizes. A copy fails with a checksum mismatch. What is the right first fix?', options=['Always use -skipcrccheck', 'Preserve block size with -pb (or use COMPOSITE_CRC checksums)', 'Lower replication', 'Use -m 1'], answer=1,
         why='HDFS file checksums depend on block size; skipping checks hides real corruption.'),
    dict(q='Which DR design usually gives the lowest RPO and RTO?', options=['Weekly backup', 'Active–passive with nightly sync', 'Active–active', 'No DR'], answer=2,
         why='Both sites serve and receive data; it is also the most expensive.'),
])

REVISION = [
    '<b>DistCp</b> = map-only MapReduce copy; maps copy files and verify checksums.',
    'No option: existing names are <b>skipped</b> (our changed menu.csv). <code>-update</code>: size + checksum. <code>-overwrite</code>: always. <code>-delete</code>: mirror deletions.',
    '<code>-update -diff s1 s2</code>: apply a snapshot diff (1 file, 1 map, rename replayed in our lab).',
    '<code>-p</code> preserves metadata; <code>-pb</code> keeps block size so checksums match; <code>-bandwidth</code> throttles; <code>-m</code> sets maps.',
    '<b>RPO</b> = data you can lose (time since last sync); <b>RTO</b> = time to recover.',
    'Designs: backup, active–passive, active–active, cloud as DR. Replicate metadata (Hive metastore) too.',
    'Test with drills: our report ran on DR with identical results; the unsynced file was missing.',
]
FAQ = [
    ('What is DistCp in Hadoop?', 'DistCp (distributed copy) copies large amounts of data within or between clusters. It runs as a map-only MapReduce job: the client lists the source files, and map tasks copy them in parallel from source DataNodes to destination DataNodes, verifying checksums. It supports incremental copies (-update, -delete), snapshot-based syncs (-diff), preserving metadata (-p) and throttling (-bandwidth).'),
    ('What is the difference between -update and -overwrite in DistCp?', 'With -update, a file is copied only if it is missing at the target or its size or checksum differs. With -overwrite, every file is copied again even if it is identical. Without either, files whose names already exist at the target are skipped, even if their content changed.'),
    ('What are RPO and RTO?', 'The recovery point objective (RPO) is the maximum acceptable amount of data loss, measured as the time since the last good copy. The recovery time objective (RTO) is the maximum acceptable time to restore service after a disaster. Sync frequency drives RPO; automation and drills drive RTO.'),
    ('How do you do disaster recovery for HDFS?', 'Keep a second cluster (or cloud storage) at another site, sync data with scheduled DistCp runs (ideally snapshot-based with -diff), replicate metadata such as the Hive metastore, document a failover runbook (DNS, job configs, access) and test it with regular drills. Commercial tools (for example Cloudera Replication Manager) automate the same steps.'),
    ('Why does DistCp fail with a checksum mismatch between clusters?', 'HDFS file checksums are computed from block-level checksums, so they depend on block size and checksum type. If source and target use different settings, the checksums differ even for identical data. Preserve block size and checksum type (-pbc) or use the COMPOSITE_CRC combine mode; use -skipcrccheck only when you verify the data another way.'),
]

PRACTICE_INTRO = 'DR exercises with the real numbers from our two clusters.'
PROBLEMS = [
    dict(level='easy', title='Copy speed', stmt='The first copy moved 169,964,453 bytes in 25,540 ms. What was the effective rate in MB/s?', inp='bytes · ms',
         code='''print(round(169964453 / 2**20 / 25.540, 1), "MB/s")
''', explain='About 6.3 MB/s, including job start-up; the copy itself was faster.'),
    dict(level='easy', title='What was skipped?', stmt='Run 2 copied 70,147 bytes and skipped 164,870,491. How many bytes were really changed on prod, and how many of the skipped bytes were stale?', inp='Bytes Copied / Bytes Skipped',
         code='''print("copied", 70147, "| stale but skipped: menu.csv", 143, "bytes")
''', explain='Only 143 bytes were stale, but they held the new price. A tiny skip can be a business error.'),
    dict(level='easy', title='Throttle check', stmt='At -bandwidth 1 (MB/s), what is the minimum time to copy 19,418,699 bytes? The run took 34.2 s. Where did the rest go?', inp='19.4 MB · 1 MB/s',
         code='''print(round(19418699 / 2**20, 1), "s minimum")
''', explain='About 18.5 s of copying; the rest was job submission, container start-up and checksum verification.'),
    dict(level='medium', title='RPO for a schedule', stmt='Syncs run at 00:00, 06:00, 12:00 and 18:00. A disaster happens at 17:30. How much data is lost, and what is the worst case?', inp='4 syncs a day',
         code='''syncs = [0, 6, 12, 18]
d = 17.5
print("lost:", d - max(s for s in syncs if s <= d), "h | worst case: 6 h")
''', explain='5.5 hours this time; the worst case is a full interval of 6 hours.'),
    dict(level='medium', title='Mirror check', stmt='Write a function that lists files to copy, files to delete and files that are stale-but-skipped for a plain run.', inp='two dicts name → checksum',
         code='''src = {"a": "1", "b": "2", "c": "3"}
dst = {"a": "1", "b": "9", "d": "4"}
print("copy:", [n for n in src if n not in dst])
print("stale but skipped:", [n for n in src if n in dst and src[n] != dst[n]])
print("left behind:", [n for n in dst if n not in src])
''', explain='c is copied, b is stale but skipped, d stays behind: the three problems -update and -delete solve.'),
    dict(level='medium', title='Maps for a big copy', stmt='DistCp splits 120,000 files totalling 30 TB over -m 200 maps. Roughly how much does each map copy, and how long at 80 MB/s per map?', inp='30 TB · 200 maps · 80 MB/s',
         code='''per_map_gb = 30 * 1024 / 200
print(f"{per_map_gb:.0f} GB per map, about {per_map_gb * 1024 / 80 / 3600:.1f} h")
''', explain='About 154 GB per map and 0.5 hours, if the network and both clusters can sustain 16 GB/s in total, which they often can\'t: throttle and schedule.'),
    dict(level='business', title='Is a drill worth it?', stmt='A failover drill costs one Saturday for 6 engineers (₹15,000 each). Without drills, the team estimates RTO doubles from 2 h to 4 h in a real disaster, at ₹5 lakh per hour. With one disaster every 5 years, is a drill every quarter worth it?', inp='4 drills/yr · ₹15,000 × 6 · 0.2 disasters/yr',
         code='''drills = 4 * 6 * 15000
saved = 0.2 * (4 - 2) * 500000
print(f"drills Rs {drills:,} vs expected saving Rs {saved:,.0f} per year")
''', explain='₹3.6 lakh vs ₹2 lakh on these illustrative numbers. Teams usually still drill, because a failed real failover can be far worse than the average, and regulators often require it.'),
    dict(level='advanced', title='Build a copy plan from a snapshot diff', stmt='Given a snapshotDiff report with +, -, M and R lines, produce the list of DR actions and the bytes to copy.', inp='diff lines + sizes',
         code='''diff = ["M\\t.", "+\\t./a.csv", "-\\t./old.csv", "R\\t./x.csv -> ./y.csv", "M\\t./menu.csv"]
size = {"./a.csv": 28086, "./menu.csv": 143}
plan, nbytes = [], 0
for line in diff:
    kind, path = line.split("\\t")
    if path == ".":
        continue
    if kind in "+M":
        plan.append(("copy", path)); nbytes += size[path]
    elif kind == "-":
        plan.append(("delete", path))
    elif kind == "R":
        plan.append(("rename",) + tuple(path.split(" -> ")))
print(plan, nbytes, "bytes")
''', explain='Copy a.csv and menu.csv (28,229 bytes), delete old.csv, rename x.csv to y.csv: everything else is untouched.'),
]

SCN_INTRO = 'DistCp and DR questions come up in data platform and Hadoop admin interviews.'
SCENARIOS = '''    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Tools · basics</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>"How do you copy data between two Hadoop clusters?"</h4>
      <p class="scn__situation">A standard question for any Hadoop role.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> DistCp and its key options.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Use DistCp: a map-only MapReduce job that copies files in parallel and verifies checksums.</li>
          <li>For repeated syncs use -update (size + checksum) and -delete; for big folders use snapshots with -diff.</li>
          <li>Throttle with -bandwidth, preserve metadata with -p, use webhdfs:// across Hadoop versions.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Incident · data</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>The DR copy has old data, but every nightly job "succeeded"</h4>
      <p class="scn__situation">An auditor finds that a reference table on DR is three months out of date.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> DistCp default semantics and verification.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Plain DistCp skips files whose names already exist; a file rewritten with the same name was never copied again.</li>
          <li>Fix the job: -update (and -delete if DR must mirror deletions), or snapshot-based -diff syncs.</li>
          <li>Add verification: compare file counts and checksums (hdfs dfs -checksum) for key folders, and alert on differences.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Design · DR</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>Design DR for a 2 PB cluster with RPO 1 hour</h4>
      <p class="scn__situation">A payments company asks for a plan and its cost drivers.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> RPO/RTO thinking and incremental replication.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Seed DR once (staged DistCp or shipped disks), then hourly snapshots with distcp -update -diff on the changed folders.</li>
          <li>Replicate the Hive metastore and configs; keep a runbook for DNS, job schedulers and access; run quarterly drills.</li>
          <li>Size the link for the hourly change rate with headroom; monitor sync lag as a first-class alert.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Concepts · RPO/RTO</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>"What is the difference between backup and disaster recovery?"</h4>
      <p class="scn__situation">Often asked together with RPO and RTO.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> data protection vs service continuity.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Backup keeps copies of data so it can be restored; restoring and rebuilding compute may take days (long RTO).</li>
          <li>DR keeps a ready site that can take over the service within the RTO, with data no older than the RPO.</li>
          <li>Many teams need both: DR for outages, backups or snapshots for mistakes (a bad -delete is replicated to DR too).</li>
        </ul>
      </div></details>
    </article>
'''
