import os
HERE = os.path.dirname(os.path.abspath(__file__))
BODY = body(HERE)
rd = lambda f: open(os.path.join(HERE, f)).read()

META = dict(
    module='07-hdfs-advanced', lesson='04-snapshots-quotas-and-trash', n='7.4',
    module_label='Module 7 · HDFS advanced',
    title='Snapshots, quotas and trash',
    desc='Protect HDFS data from people and programs, with real Hadoop 3.5.0 outputs: a snapshot in 1.7 s, a file deleted with -skipTrash and restored from .snapshot, snapshotDiff, snapshots that refuse deletion, a name quota of 3 that fits only 2 files, a 10 MB space quota that rejects a 2-byte file (“diskspace consumed = 402653184 B = 384 MB”), and trash moves, restores and expunge checkpoints. Python simulations, quiz and interview scenarios.',
    og_desc='A 2-byte file rejected by a 10 MB quota, and a -skipTrash delete undone in seconds. Snapshots, quotas and trash on a real cluster.',
    minutes=26, level='Intermediate',
    lead='Replication protects data from broken disks, not from a wrong command or a runaway script. HDFS has three tools for that: snapshots (point-in-time views you can restore from), quotas (limits per folder) and trash (a recycle bin). This lesson uses all three on a real cluster, including two surprises that catch even experienced admins.',
    chips=['Real restore after -skipTrash', 'The 384 MB quota surprise', 'Runs in your browser (Python)'],
)

RUN = dict(
    heading='A copy-on-write snapshot in Python',
    intro='<p>The live folder is a dictionary of file names to block IDs. A snapshot records nothing at first; when a file is deleted or replaced, the old entry is saved into the snapshot\'s difference list. Blocks are freed only when nothing refers to them.</p>',
    code='''live = {"sem1.csv": "blkA", "sem2.csv": "blkB"}
snapshots = {}

def create_snapshot(name):
    snapshots[name] = {}                          # empty: nothing copied

def delete(fname):
    for diff in snapshots.values():
        diff.setdefault(fname, live[fname])       # remember the old version
    del live[fname]

def view(name):
    return {**live, **snapshots[name]}            # live tree + saved differences

def referenced_blocks():
    return set(live.values()) | {b for d in snapshots.values() for b in d.values()}

create_snapshot("before_results")
delete("sem1.csv")
print("live            :", live)
print("snapshot view   :", view("before_results"))
print("blocks kept     :", sorted(referenced_blocks()))
''',
    anno=[
        ('    snapshots[name] = {}                          # empty: nothing copied', 'Creating a snapshot is instant because it copies nothing. Our real snapshot took 1.7 s, almost all Java start-up.'),
        ('        diff.setdefault(fname, live[fname])       # remember the old version', 'Copy-on-write: only when something changes is the old version recorded, and only once per snapshot.'),
        ('    return set(live.values()) | {b for d in snapshots.values() for b in d.values()}', 'blkA is still referenced by the snapshot, so it isn\'t deleted. That is why snapshots can hold disk space after files are deleted.'),
    ],
    tasks=[
        dict(label='1 · Delete and look back', hint='Press <b>Run</b>. Then restore: copy sem1.csv from the snapshot view into <code>live</code> under a new block ID.', code=None),
        dict(label='2 · Name quota counts the folder', hint='<b>Predict first:</b> with a name quota of 3 on an empty folder, how many files fit? (Real: “quota=3 file count=4”.)',
             code='''quota = 3
used = 1                         # the folder itself
files = 0
while used + 1 <= quota:
    used += 1; files += 1
print("files that fit:", files)
'''),
        dict(label='3 · The 384 MB reservation', hint='While a block is written, HDFS reserves block size × replication against the space quota. Which quotas can accept a 2-byte file?',
             code='''block, replication = 128 * 1024**2, 3
reserve = block * replication
for quota_mb in [10, 100, 384, 1024]:
    ok = quota_mb * 1024**2 >= reserve
    print(f"space quota {quota_mb:>5} MB -> {'ok' if ok else 'DSQuotaExceeded'} (needs {reserve // 1024**2} MB reserved)")
'''),
        dict(label='4 · Trash path', hint='Build the trash location for any deleted path, and the checkpoint name format yyMMddHHmmss for a given time.',
             code='''from datetime import datetime
user, path = "hadoop", "/user/hadoop/quota_lab/names/f1.txt"
print(f"/user/{user}/.Trash/Current{path}")
print("checkpoint:", datetime(2026, 10, 21, 16, 22, 55).strftime("%y%m%d%H%M%S"))
'''),
        dict(label='5 · Spot the error', hint='This code tries to edit a file inside a snapshot, like <code>rm .snapshot/…</code>. Snapshots are read-only: make the view a read-only mapping and catch the error.',
             code='''from types import MappingProxyType
snapshot = MappingProxyType({"sem1.csv": "blkA"})
del snapshot["sem1.csv"]          # Modification on a read-only snapshot is disallowed
''', expect='error'),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run it on your PC: snapshots, quotas and trash',
    intro='<p>Run this against the Module 5 lab cluster. Copy <code>canteen_orders.csv</code> into the namenode first (<code>docker cp canteen_orders.csv lab5-namenode-1:/tmp/</code>). The script cleans up its own folders from earlier runs, so you can run it again.</p>',
    items=[
        dict(title='The protection lab', file='protect_lab.sh',
             cmd=rd('protect_lab.sh') + '\n# Run:  bash protect_lab.sh',
             output=rd('tx_protect.txt').strip(),
             note='Real output. Note the quota lines: 2 files fit in a name quota of 3, and a 2-byte file breaks a 10 MB space quota because 384 MB are reserved for the new block.'),
    ],
)

TRACE = dict(
    heading='Checking a space quota while writing',
    intro='<p>Follow the NameNode\'s quota check as a client writes a small file into a folder with a 10 MB space quota.</p>',
    code='''quota = 10 * 1024 * 1024
used = 0
block_size, replication = 128 * 1024 * 1024, 3
needed = block_size * replication
if used + needed > quota:
    result = f"DSQuotaExceeded: quota = {quota} B but diskspace consumed = {used + needed} B"
else:
    result = "block allocated"
print(result)
''',
    notes={4: 'Reservation :: A new block is charged at full size × replication until it is finished.',
           5: 'Check :: 402,653,184 B > 10,485,760 B, so the write fails before any byte is sent.'},
)

WORKED_INTRO = 'Three protection calculations: the space snapshots really cost, a sensible quota, and a snapshot schedule.'
EXAMPLES = [
    dict(level='b', tag='Quota · sizing', title='What space quota does a team need?',
         problem='<p>A team expects 20 TB of data with replication 3 and wants 25% headroom. What space quota should be set?</p>',
         inp='20 TB · ×3 · +25%',
         approach=['Raw = data × replication.',
                   'Add 25% headroom.',
                   'Space quotas count raw bytes.'],
         code='''data_tb, rep, headroom = 20, 3, 0.25
print(f"setSpaceQuota {data_tb * rep * (1 + headroom):.0f}t")
''', notes={2: 'Raw :: Our 4.5 MB file used 13.4 MB of quota with 3 replicas.'},
         tryit='Setting 20t would fail at about 6.7 TB of real data. Teams often misread space quotas as data size.'),
    dict(level='i', tag='Snapshots · cost', title='How much disk do a week of snapshots hold?',
         problem='<p>A 50 TB folder changes 2% of its data per day (rewritten or deleted). Daily snapshots are kept for 7 days. Roughly how much extra raw space (replication 3) do the snapshots hold?</p>',
         inp='50 TB · 2%/day · 7 days · ×3',
         approach=['Each day 1 TB of old data is kept by snapshots.',
                   'For 7 days: 7 TB.',
                   'Times replication.'],
         code='''folder, change, days, rep = 50, 0.02, 7, 3
kept = folder * change * days
print(f"about {kept:.0f} TB of old data, {kept * rep:.0f} TB raw")
''', notes={2: 'Copy-on-write :: Only changed or deleted data costs extra.'},
         tryit='Compare with full copies: 7 × 50 TB × 3 = 1,050 TB raw. Snapshots are cheap only because most data doesn\'t change.'),
    dict(level='a', tag='Operations · schedule', title='Which snapshots to keep?',
         problem='<p>Policy: keep daily snapshots for 7 days and Sunday snapshots for 4 weeks. Given 30 days of snapshots named by day number (day 30 = today, day 30 is a Sunday), list which to keep.</p>',
         inp='days 1–30, Sundays every 7 days back from 30',
         approach=['Keep the last 7 days.',
                   'Keep Sundays within 28 days.',
                   'Delete the rest.'],
         code='''today = 30
keep = {d for d in range(today - 6, today + 1)} | {d for d in range(today, today - 28, -7)}
print("keep:", sorted(keep))
print("delete:", len(set(range(1, 31)) - keep), "snapshots")
''', notes={2: 'Retention :: Daily for a week, weekly for a month.'},
         tryit='A scheduled job runs -deleteSnapshot for the rest; without it, snapshots pile up and hold space forever.'),
]

QUIZ = mix([
    dict(q='How long does creating a snapshot of a huge folder take?', options=['Proportional to its size', 'About the same as a tiny folder: it is a metadata operation', 'Hours', 'It copies all blocks first'], answer=1,
         why='No blocks are copied; our 1.7 s was JVM start-up.'),
    dict(q='Which command must an admin run before snapshots can be taken in a folder?', options=['hdfs dfs -snapshot on', 'hdfs dfsadmin -allowSnapshot /dir', 'hdfs fsck -snapshot', 'None'], answer=1,
         why='Then users can run hdfs dfs -createSnapshot /dir name.'),
    dict(q='A file was deleted with -skipTrash. How was it recovered in the lab?', options=['From trash', 'Copied from /dir/.snapshot/before_results/…', 'From fsck', 'It could not be'], answer=1,
         why='The snapshot still referenced its blocks.'),
    dict(q='Name quota 3 on an empty folder: how many files fit?', options=['3', '2', '4', '1'], answer=1,
         why='The folder itself counts as one name: “quota=3 file count=4”.'),
    dict(q='Why did a 2-byte file exceed a 10 MB space quota?', options=['A bug', 'A new block reserves block size × replication (384 MB) while being written', 'Space quotas count files', 'The quota was in KB'], answer=1,
         why='“diskspace consumed = 402653184 B = 384 MB”.'),
    dict(q='What is the default value of fs.trash.interval?', options=['1440', '60', '0 (trash off)', '10080'], answer=2,
         why='hdfs getconf -confKey fs.trash.interval printed 0.'),
    dict(q='Which deletions does trash NOT catch?', options=['hdfs dfs -rm', 'hdfs dfs -rm -skipTrash and most API delete() calls', 'Deletes by admins', 'Deletes at night'], answer=1,
         why='Trash is a client-side shell feature; snapshots protect against all deletes.'),
    dict(q='Why can snapshots make a cluster run out of space?', options=['They copy everything', 'Blocks deleted from the live folder stay on disk while a snapshot refers to them', 'They disable replication', 'They store logs'], answer=1,
         why='Old snapshots must be deleted to free that space.'),
])

REVISION = [
    '<b>Snapshot</b>: read-only point-in-time view; <code>-allowSnapshot</code> then <code>-createSnapshot</code>; under <code>dir/.snapshot/name</code>; instant (copy-on-write).',
    'Restore = copy out of <code>.snapshot</code>; <code>snapshotDiff</code> shows + − M R; snapshots can\'t be edited; a folder with snapshots can\'t be deleted.',
    'Snapshots pin deleted blocks: delete old snapshots to free space. Not a backup: copy off-cluster (DistCp).',
    '<b>Name quota</b> counts files + folders including the folder itself (quota 3 → 2 files).',
    '<b>Space quota</b> counts raw bytes with replicas; a new block reserves 128 MB × 3 = 384 MB.',
    '<b>Trash</b>: <code>fs.trash.interval</code> (default 0 = off); <code>-rm</code> moves to <code>.Trash/Current</code>; <code>-expunge</code> checkpoints and purges; <code>-skipTrash</code> bypasses.',
    'Check usage: <code>hdfs dfs -count -q -h -v</code>.',
]
FAQ = [
    ('What are HDFS snapshots?', 'Read-only, point-in-time copies of a directory tree. An administrator enables them per directory with hdfs dfsadmin -allowSnapshot; users create them with hdfs dfs -createSnapshot. Creation copies no data; the NameNode records later changes so the old view remains available under the .snapshot path. They are used to recover from accidental deletes or overwrites and as a consistent source for backups.'),
    ('What is the difference between a name quota and a space quota?', 'A name quota limits the number of files and directories in a tree (including the directory itself). A space quota limits the raw bytes consumed, counting all replicas. They are set independently with hdfs dfsadmin -setQuota and -setSpaceQuota.'),
    ('Why does a small file fail a space quota that seems large enough?', 'Because when a block is allocated, HDFS charges a full block size times the replication factor against the quota until the block is completed. With 128 MB blocks and replication 3, a quota below 384 MB cannot accept any new file.'),
    ('How does the HDFS trash work?', 'If fs.trash.interval is greater than zero, deleting with the shell moves files to /user/&lt;name&gt;/.Trash/Current. Periodically (or on -expunge) Current is renamed to a timestamped checkpoint, and checkpoints older than the interval are deleted permanently. Files can be restored by moving them out of the trash. -skipTrash and most API deletes bypass it.'),
    ('Are snapshots a backup?', 'No. They live in the same cluster and depend on the same NameNode and DataNodes. They protect against logical mistakes, not against losing the cluster. For disaster recovery, copy data (or snapshot differences) to another cluster or to cloud storage with DistCp.'),
]

PRACTICE_INTRO = 'Protection exercises using the real messages and numbers from the lab.'
PROBLEMS = [
    dict(level='easy', title='Snapshot path', stmt='Build the path of sem1.csv inside the snapshot before_results of /user/hadoop/results.', inp='folder, snapshot, file',
         code='''d, s, f = "/user/hadoop/results", "before_results", "2026/sem1.csv"
print(f"{d}/.snapshot/{s}/{f}")
''', explain='/user/hadoop/results/.snapshot/before_results/2026/sem1.csv, as listed in the lab.'),
    dict(level='easy', title='Quota used', stmt='The space quota is 1 G and the remaining quota is 1010.6 M. How much is used, and how much data is that with replication 3?', inp='1024 M − 1010.6 M',
         code='''used = 1024 - 1010.6
print(f"used {used:.1f} M raw -> {used / 3:.1f} M of data")
''', explain='13.4 M raw = 4.5 M of data × 3: the canteen_orders.csv file.'),
    dict(level='easy', title='Reserved bytes', stmt='Compute the reservation that the 2-byte file triggered.', inp='128 MB × 3',
         code='''print(128 * 1024 * 1024 * 3, "bytes")
''', explain='402,653,184 bytes, exactly the number in the error message.'),
    dict(level='medium', title='Parse snapshotDiff', stmt='Count created, deleted and modified entries in the real snapshotDiff output.', inp='3 lines',
         code='''from collections import Counter
out = """M	./2026
+	./2026/sem1.csv
-	./2026/sem1.csv"""
print(Counter(line.split()[0] for line in out.splitlines()))
''', explain='One of each: the folder was modified, and the restored file appears as deleted (old inode) plus created (new inode).'),
    dict(level='medium', title='Which quota fails first?', stmt='A folder has name quota 1,000 and space quota 30 GB. A job writes 600 files of 20 MB each (replication 3). Which limit is hit?', inp='600 × 20 MB',
         code='''files, size_mb, rep = 600, 20, 3
names_needed = files + 1
raw_gb = files * size_mb * rep / 1024
print("names:", names_needed, "of 1000 | raw:", round(raw_gb, 1), "GB of 30 GB")
''', explain='Space: 35.2 GB > 30 GB, while names (601) are fine. Big files hit space quotas; tiny files hit name quotas.'),
    dict(level='medium', title='Trash age', stmt='A trash checkpoint is named 261021162255. With fs.trash.interval = 1440, when will it be deleted?', inp='yyMMddHHmmss + 1440 min',
         code='''from datetime import datetime, timedelta
t = datetime.strptime("261021162255", "%y%m%d%H%M%S")
print("created", t, "-> deleted after", t + timedelta(minutes=1440))
''', explain='One day later, at the next expunge run after that time.'),
    dict(level='business', title='Cost of a runaway job', stmt='Without quotas, a runaway job filled the cluster and 25 teams lost a 6-hour working day (₹1.2 lakh per team per day). With quotas only its own team would have been affected. What did the missing quota cost?', inp='24 other teams × ₹1.2 lakh × 6/8 day',
         code='''print(f"Rs {24 * 1.2 * 6 / 8:.1f} lakh")
''', explain='About ₹21.6 lakh in lost work (illustrative), for one missing admin command.'),
    dict(level='advanced', title='Blocks freed after deleting a snapshot', stmt='Live files refer to blocks {A, C}; snapshot s1 refers to {A, B}; snapshot s2 refers to {B, C, D}. Which blocks are freed if s1 is deleted? If s2 is also deleted?', inp='live {A,C}, s1 {A,B}, s2 {B,C,D}',
         code='''live, s1, s2 = {"A", "C"}, {"A", "B"}, {"B", "C", "D"}
before = live | s1 | s2
print("delete s1 frees:", sorted(before - (live | s2)))
print("then s2 frees  :", sorted((live | s2) - live))
''', explain='Deleting s1 frees nothing (A is live, B is in s2). Deleting s2 then frees B and D. Space returns only when no snapshot or live file refers to a block.'),
]

SCN_INTRO = 'Data protection questions come up in every Hadoop administration and data platform interview.'
SCENARIOS = '''    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Operations · recovery</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>“A user deleted a production folder. Can you get it back?”</h4>
      <p class="scn__situation">The classic incident question.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> trash, snapshots, backups, in order.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Check the user's <code>.Trash/Current</code> (and checkpoints); <code>-mv</code> it back.</li>
          <li>If trash was off or bypassed, copy it back from the latest snapshot under <code>.snapshot</code>.</li>
          <li>Otherwise restore from the DR cluster or reprocess from raw data. Then add snapshots and trash to prevent a repeat.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Quotas · troubleshooting</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>“DSQuotaExceeded, but the folder only has 2 GB of a 3 GB quota”</h4>
      <p class="scn__situation">A team's job fails while writing many files in parallel.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> block reservation and raw bytes.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Space quotas count raw bytes: 2 GB of data at replication 3 may already be 6 GB raw.</li>
          <li>Every block being written reserves block size × replication (384 MB with defaults); 20 parallel writers reserve 7.5 GB at once.</li>
          <li>Raise the quota to cover raw size plus in-flight blocks, or reduce parallel writers.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Capacity · snapshots</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>Deleting 100 TB didn't free any space</h4>
      <p class="scn__situation">An admin deleted old partitions, but the cluster's used space stayed the same.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> snapshots (and trash) holding blocks.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Check <code>hdfs lsSnapshottableDir</code> and snapshots on parent folders: they still reference the deleted blocks.</li>
          <li>Also check the trash: deleted data may sit in <code>.Trash</code> until the interval passes.</li>
          <li>Delete the obsolete snapshots / expunge trash; space is freed as DataNodes delete the blocks.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Design · policy</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>Design a data protection policy for a shared cluster</h4>
      <p class="scn__situation">40 teams, one production cluster, one DR cluster.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> layered protection.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Trash on (e.g. 3 days) cluster-wide; restrict <code>-skipTrash</code> to service accounts.</li>
          <li>Snapshots on critical folders: daily for 7 days, weekly for 4 weeks, with automatic cleanup.</li>
          <li>Name and space quotas on every team folder, with alerts at 80%.</li>
          <li>Nightly DistCp (snapshot diffs) to the DR cluster for critical data.</li>
        </ul>
      </div></details>
    </article>
'''
