import os
HERE = os.path.dirname(os.path.abspath(__file__))
BODY = body(HERE)
rd = lambda f: open(os.path.join(HERE, f)).read()

META = dict(
    module='07-hdfs-advanced', lesson='03-erasure-coding', n='7.3',
    module_label='Module 7 · HDFS advanced',
    title='Erasure coding',
    desc='HDFS erasure coding on a real Hadoop 3.5.0 cluster: the same 140,760,270-byte file uses 422,280,810 bytes with 3× replication and 235,132,110 with RS-3-2 (1.67×); a block group with five internal blocks; the file still reads correctly (same MD5) after 2 DataNodes die and fails with “3 missing blocks” after the third; a 15-byte file costs 45 bytes either way. Policies, striping, cells, verifyClusterSetup, when to use EC. Real XOR parity in Python, quiz and interview scenarios.',
    og_desc='Same safety as three copies at 1.67× the space, until you ask it to do the wrong job. Erasure coding on a real cluster.',
    minutes=28, level='Advanced',
    lead='Three replicas are simple and fast, but they triple the disk bill. Hadoop 3 added erasure coding: split data into pieces, compute parity, and survive the same failures with far less space. This lesson stores one file both ways on a real cluster, kills DataNodes until the data is lost, and explains which data should and should not be erasure-coded.',
    chips=['Real EC vs replication on one cluster', 'Parity you can compute in the browser', 'Runs in your browser (Python)'],
)

RUN = dict(
    heading='Parity you can compute: XOR erasure coding',
    intro='<p>HDFS\'s simplest policy, XOR-2-1, computes one parity cell as the XOR of two data cells. Lose any one of the three and XOR the other two to get it back. Reed-Solomon does the same idea with more parity. Run it, then lose a different cell.</p>',
    code='''d1 = b"order_id,item,amount\\n1,chai,20\\n"
d2 = b"2,poha,30\\n3,dosa,40\\n4,idli,30\\n"
size = max(len(d1), len(d2))
d1, d2 = d1.ljust(size, b"\\0"), d2.ljust(size, b"\\0")     # cells are padded to equal size

parity = bytes(a ^ b for a, b in zip(d1, d2))            # XOR-2-1: one parity cell
print("stored cells:", len(d1), "+", len(d2), "+", len(parity), "bytes")

lost = "d2"                                               # a DataNode dies
rebuilt = bytes(a ^ p for a, p in zip(d1, parity))        # d1 XOR parity = d2
print("rebuilt", lost, "correct:", rebuilt == d2)
print(rebuilt.rstrip(b"\\0").decode())
print(f"overhead: {(len(d1) + len(d2) + len(parity)) / (2 * size):.2f}x")
''',
    anno=[
        ('parity = bytes(a ^ b for a, b in zip(d1, d2))            # XOR-2-1: one parity cell', 'XOR has a handy property: if p = a ⊕ b, then a = p ⊕ b and b = p ⊕ a. One parity cell protects against one loss.'),
        ('rebuilt = bytes(a ^ p for a, p in zip(d1, parity))        # d1 XOR parity = d2', 'Reconstruction is computation, not copying: the reader needs the surviving cells and CPU time.'),
        ('print(f"overhead: {(len(d1) + len(d2) + len(parity)) / (2 * size):.2f}x")', '3 cells stored for 2 cells of data: 1.5×, versus 3× with replication. RS-6-3 also reaches 1.5× but survives 3 losses.'),
    ],
    tasks=[
        dict(label='1 · Rebuild a lost cell', hint='Press <b>Run</b>. Then lose <code>d1</code> instead and rebuild it from <code>d2</code> and <code>parity</code>.', code=None),
        dict(label='2 · Overhead of policies', hint='<b>Predict first:</b> which policy is cheapest? Compute raw space and failures tolerated for each.',
             code='''policies = {"replication 3": (1, 2), "XOR-2-1": (2, 1), "RS-3-2": (3, 2), "RS-6-3": (6, 3), "RS-10-4": (10, 4)}
for name, (k, m) in policies.items():
    overhead = 3.0 if name.startswith("replication") else (k + m) / k
    tolerated = 2 if name.startswith("replication") else m
    print(f"{name:14} {overhead:.2f}x raw   survives {tolerated} failure(s)")
'''),
        dict(label='3 · Our lab numbers', hint='Check the real <code>-du</code> output: data 140,760,270 bytes; raw 422,280,810 (replicated) and 235,132,110 (RS-3-2).',
             code='''data, rep, ec = 140_760_270, 422_280_810, 235_132_110
print(f"replication: {rep / data:.2f}x   EC: {ec / data:.2f}x   saving: {1 - ec / rep:.0%}")
'''),
        dict(label='4 · Small files', hint='A file smaller than one cell still needs full-size parity cells. Compute raw bytes under RS-3-2 for 15 bytes, 1 MB and 10 MB (cell 1 MB).',
             code='''import math
cell, k, m = 1024 * 1024, 3, 2
for size in [15, 1024 * 1024, 10 * 1024 * 1024]:
    stripes = math.ceil(size / (k * cell))
    parity = m * (min(size, cell) if stripes == 1 else cell) * stripes   # parity cells are as big as the largest data cell
    raw = size + parity
    print(f"{size:>10} bytes -> raw {raw:>10}  ({raw / size:.2f}x)")
'''),
        dict(label='5 · Spot the error', hint='This check thinks a stripe with 3 lost units is still readable under RS-3-2. Fix the rule (need at least k survivors).',
             code='''k, m = 3, 2
lost = 3
readable = lost <= k
print("readable:", readable)
assert not readable, "RS-3-2 survives at most m = 2 losses"
''', expect='error'),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run it on your PC: replication vs RS-3-2 on five DataNodes',
    intro='<p>Use the 5-DataNode cluster from Module 5 (lab5). The script enables RS-3-2, checks the cluster, copies the same file into a replicated folder and an erasure-coded folder, compares disk usage, then stops DataNodes one by one and reads the files. It restarts the DataNodes at the end. Save as <code>ec_lab.sh</code> in the lab folder and run <code>bash ec_lab.sh</code>.</p>',
    items=[
        dict(title='Erasure coding lab', file='ec_lab.sh',
             cmd=rd('ec_lab.sh') + '\n# Run:  bash ec_lab.sh',
             output=rd('tx_ec.txt').strip(),
             note='Real output. The read with 2 DataNodes down took 63 s here because the NameNode still listed them as live and the client waited for a connect timeout; a repeat run took 2 s. Block IDs and IPs will differ on your run.'),
    ],
)

TRACE = dict(
    heading='Striping cells round-robin',
    intro='<p>Follow how a writer spreads 1 MB cells over three data internal blocks, stripe by stripe, and adds two parity cells per stripe.</p>',
    code='''k, m = 3, 2
cells = ["c1", "c2", "c3", "c4", "c5", "c6", "c7"]
blocks = {i: [] for i in range(k + m)}
for n, cell in enumerate(cells):
    blocks[n % k].append(cell)
stripes = (len(cells) + k - 1) // k
for s in range(stripes):
    blocks[3].append(f"P{s + 1}")
    blocks[4].append(f"Q{s + 1}")
print(blocks)
''',
    notes={5: 'Round-robin :: Cell n goes to data block n mod 3.',
           8: 'Parity :: Every stripe (up to 3 cells) gets its own 2 parity cells.'},
)

WORKED_INTRO = 'Three erasure-coding decisions with numbers: storage saved, how many DataNodes a policy needs, and whether a folder should be erasure-coded at all.'
EXAMPLES = [
    dict(level='b', tag='Cost · storage', title='How much disk does EC save on the archive?',
         problem='<p>The university\'s archive holds 400 TB of data, all with replication 3. If it moves to RS-6-3, how much raw disk is freed?</p>',
         inp='400 TB · 3× vs 1.5×',
         approach=['Raw with replication = 400 × 3.',
                   'Raw with RS-6-3 = 400 × 9/6.',
                   'Difference.'],
         code='''data = 400
rep, ec = data * 3, data * 9 / 6
print(f"replication {rep} TB, RS-6-3 {ec:.0f} TB, freed {rep - ec:.0f} TB")
''', notes={2: 'Overhead :: (k + m) / k = 9 / 6 = 1.5.'},
         tryit='600 TB freed: half the raw space, with 3 tolerated failures instead of 2.'),
    dict(level='i', tag='Cluster · requirements', title='Can our cluster use the policy?',
         problem='<p>The cluster has 8 DataNodes in 3 racks. Which of RS-3-2, RS-6-3 and RS-10-4 can it run, using the rule “at least k + m DataNodes”?</p>',
         inp='8 DataNodes',
         approach=['Units per group = k + m.',
                   'Compare with the DataNode count.',
                   'Report usable policies.'],
         code='''nodes = 8
for name, k, m in [("RS-3-2", 3, 2), ("RS-6-3", 6, 3), ("RS-10-4", 10, 4)]:
    print(f"{name:8} needs {k + m:2} DataNodes ->", "OK" if nodes >= k + m else "not enough")
''', notes={3: 'Units :: Each internal block must be on a different DataNode.'},
         tryit='Rack tolerance needs more: hdfs ec -verifyClusterSetup also checks racks, as our 2-rack lab showed for RS-3-2.'),
    dict(level='a', tag='Decision · fit', title='Should this folder be erasure-coded?',
         problem='<p>Three folders: /logs/2021 (400 TB, average file 900 MB, read once a year), /tmp (2 TB, average file 40 KB, read constantly) and /warehouse/today (50 TB, 256 MB files, read by every morning job). Score each for EC.</p>',
         inp='3 folders',
         approach=['EC needs files much larger than one stripe (k × 1 MB).',
                   'EC suits cold data.',
                   'Recommend.'],
         code='''folders = [("/logs/2021", 900, "cold"), ("/tmp", 0.04, "hot"), ("/warehouse/today", 256, "hot")]
for path, avg_mb, temp in folders:
    big = avg_mb >= 6 * 10        # well beyond one RS-6-3 stripe of 6 MB
    print(f"{path:18} {'EC' if big and temp == 'cold' else 'keep replication'}")
''', notes={3: 'Rule :: Big and cold → EC; small or hot → replication.'},
         tryit='/warehouse/today could move to EC once it becomes cold (e.g. after 90 days).'),
]

QUIZ = mix([
    dict(q='With RS-6-3, how many DataNode failures can a block group survive?', options=['1', '2', '3', '6'], answer=2,
         why='m = 3 parity units: any 3 of the 9 can be lost.'),
    dict(q='What is the raw storage overhead of RS-6-3?', options=['3.0×', '2.0×', '1.5×', '1.0×'], answer=2,
         why='(6 + 3) / 6 = 1.5×.'),
    dict(q='In our lab, how much disk did the 140,760,270-byte file use under RS-3-2?', options=['140,760,270', '235,132,110', '422,280,810', '281,520,540'], answer=1,
         why='1.67×; with replication it was 422,280,810 (3×).'),
    dict(q='Why did the 15-byte file cost 45 bytes under EC?', options=['A bug', 'One small data cell still needs two parity cells of the same size', 'EC adds headers', 'It was replicated'], answer=1,
         why='EC saves space only for files spanning several cells.'),
    dict(q='What happened after a third DataNode was stopped?', options=['The EC file still read', 'The EC file could not be read: 3 missing blocks in the stripe', 'The NameNode crashed', 'The file was auto-replicated'], answer=1,
         why='Only 2 of 5 units left; 3 are needed.'),
    dict(q='Which command applies EC to new files in a folder?', options=['hdfs dfs -setrep -ec', 'hdfs ec -setPolicy -path /dir -policy RS-6-3-1024k', 'hdfs dfsadmin -ec', 'hadoop ec -convert'], answer=1,
         why='Existing files keep their layout until rewritten.'),
    dict(q='Which data is the best fit for erasure coding?', options=['Many small hot files', 'Large, rarely read archival files', 'Files being appended all day', 'Temporary job output'], answer=1,
         why='Cold, large files: big savings, rare reconstruction cost.'),
    dict(q='Why did verifyClusterSetup warn about RS-3-2 on our cluster?', options=['Too few DataNodes', '3 racks are required, but there were only 2', 'Java version', 'Disk full'], answer=1,
         why='Without enough racks, one rack failure could take too many units.'),
])

REVISION = [
    'EC: <b>k data + m parity</b> units; survive any <b>m</b> losses; overhead <b>(k+m)/k</b>.',
    'Policies: RS-6-3 (enabled by default, 9 DNs, 1.5×), RS-3-2 (5 DNs, 1.67×), RS-10-4, XOR-2-1.',
    'Striped layout: 1 MB <b>cells</b> round-robin; a <b>block group</b> of k+m <b>internal blocks</b> on different DataNodes.',
    'Lab: 422,280,810 B (rep 3) vs 235,132,110 B (RS-3-2) for the same file; same MD5 after 2 DNs died; “3 missing blocks” after the third.',
    'Small files: no saving (15 B → 45 B). Hot data: loses locality, costs decode CPU.',
    'Commands: <code>hdfs ec -listPolicies / -enablePolicy / -verifyClusterSetup / -setPolicy / -getPolicy</code>.',
    'Policy affects only new files; move existing data with a copy.',
]
FAQ = [
    ('What is erasure coding in Hadoop?', 'A storage method introduced in Hadoop 3 in which file data is split into data units and parity units are computed with an algorithm such as Reed-Solomon. The units are stored on different DataNodes, and the original data can be reconstructed from any k of the k + m units. It gives similar or better fault tolerance than 3× replication at around 1.4–1.67× storage.'),
    ('What are the disadvantages of erasure coding?', 'Reconstruction needs network reads from several nodes and CPU for decoding; reads lose data locality because data is striped across nodes; small files gain no space; it needs at least k + m DataNodes and enough racks; and some write features behave differently from replicated files. It is best for large, cold data.'),
    ('How do you enable erasure coding on a directory?', 'Enable the policy if needed (hdfs ec -enablePolicy -policy RS-6-3-1024k), check the cluster with hdfs ec -verifyClusterSetup, then run hdfs ec -setPolicy -path /dir -policy RS-6-3-1024k. Files created afterwards in that directory are erasure-coded; existing files must be copied to be converted.'),
    ('What is a block group?', 'In striped erasure coding, the set of k data and m parity internal blocks that together store a range of a file. Each internal block is stored on a different DataNode and has an ID derived from the group ID.'),
    ('Replication or erasure coding: how do you choose?', 'Use replication for hot data, small files and data read with locality by many jobs. Use erasure coding for large files that are rarely read, such as archives, old partitions and backups, where storage savings matter more than read performance.'),
]

PRACTICE_INTRO = 'Erasure-coding exercises using the real sizes, IDs and messages from the lab.'
PROBLEMS = [
    dict(level='easy', title='Overhead formula', stmt='Print the overhead (k+m)/k for RS-3-2, RS-6-3 and RS-10-4.', inp='3 policies',
         code='''for k, m in [(3, 2), (6, 3), (10, 4)]:
    print(f"RS-{k}-{m}: {(k + m) / k:.2f}x")
''', explain='1.67×, 1.50×, 1.40×.'),
    dict(level='easy', title='Saving in the lab', stmt='How many bytes did RS-3-2 save compared with replication for the lab file?', inp='422,280,810 vs 235,132,110',
         code='''print(f"{422_280_810 - 235_132_110:,} bytes saved")
''', explain='187,148,700 bytes, about 44% less raw space.'),
    dict(level='easy', title='Internal block indexes', stmt='Internal block IDs are the group ID plus the index. Given the five IDs from fsck, print each index and whether it holds data or parity (k = 3).', inp='-9223372036854775728 … -9223372036854775724',
         code='''ids = [-9223372036854775728 + i for i in range(5)]
group = ids[0]
for b in ids:
    i = b - group
    print(b, "index", i, "data" if i < 3 else "parity")
''', explain='Indexes 0–2 are data, 3–4 parity: consecutive IDs in one block group.'),
    dict(level='medium', title='XOR recovery', stmt='Data cells a = b"HDFS", b = b"EC!!"; parity p = a XOR b. Rebuild a from b and p.', inp='two 4-byte cells',
         code='''a, b = b"HDFS", b"EC!!"
p = bytes(x ^ y for x, y in zip(a, b))
print(bytes(x ^ y for x, y in zip(b, p)))
''', explain='b"HDFS": XOR parity is the simplest erasure code.'),
    dict(level='medium', title='Readable or not?', stmt='For RS-6-3, given the number of lost units in a block group, print whether it can be read.', inp='0 to 4 lost',
         code='''k, m = 6, 3
for lost in range(5):
    print(lost, "lost ->", "readable" if lost <= m else "LOST")
''', explain='Up to 3 losses are fine; the fourth makes the group unreadable.'),
    dict(level='medium', title='Stripes in a file', stmt='How many full stripes does a 140,760,270-byte file have under RS-3-2 with 1 MB cells?', inp='140,760,270 bytes',
         code='''cell, k = 1024 * 1024, 3
print(140_760_270 // (k * cell), "full stripes")
''', explain='44 full stripes of 3 MB, plus a partial one; each stripe has its own 2 parity cells.'),
    dict(level='business', title='Archive disk budget', stmt='Disk costs ₹4,000 per TB (with servers and power, illustrative). An archive of 300 TB moves from replication 3 to RS-6-3. What is the saving?', inp='300 TB',
         code='''freed = 300 * 3 - 300 * 1.5
print(f"{freed:.0f} TB freed -> Rs {freed * 4000:,.0f}")
''', explain='450 TB freed, about ₹18 lakh of disk (illustrative), or room for years of new data.'),
    dict(level='advanced', title='Placement check', stmt='Given rack assignments of the 5 internal blocks, check whether losing any single rack loses more than m = 2 units.', inp='5 units over 2 racks',
         code='''from collections import Counter
racks = ["r1", "r1", "r2", "r2", "r2"]           # rack of each internal block
worst = max(Counter(racks).values())
print("worst rack holds", worst, "units ->", "safe" if worst <= 2 else "a rack failure loses data")
''', explain='With 2 racks, one holds 3 units: exactly why verifyClusterSetup asked for 3 racks for RS-3-2.'),
]

SCN_INTRO = 'Erasure coding questions are common in Hadoop 3 interviews, especially for platform and administrator roles.'
SCENARIOS = '''    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Hadoop 3 · features</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>“What's new in Hadoop 3 for storage?”</h4>
      <p class="scn__situation">A common Hadoop 2 vs 3 question.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> erasure coding and its trade-offs.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Erasure coding: e.g. RS-6-3 stores 1.5× instead of 3× and tolerates 3 failures.</li>
          <li>Also: more than two NameNodes for HA, intra-DataNode disk balancer, and other improvements.</li>
          <li>Mention when not to use EC: small files, hot data needing locality.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Capacity · decision</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>Storage is 85% full; buying disks takes 4 months</h4>
      <p class="scn__situation">A 2 PB cluster, mostly replicated. 60% of data is older than a year and rarely read.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> practical EC adoption.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Identify cold, large-file folders; check <code>verifyClusterSetup</code> for RS-6-3 (nodes and racks).</li>
          <li>Create EC folders, copy cold partitions with distcp, verify checksums/row counts, repoint tables, delete originals.</li>
          <li>Moving 1.2 PB of data from 3× to 1.5× frees roughly 1.8 PB of raw space; do it in batches off-peak.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Performance · troubleshooting</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>Jobs on EC data are slower and network traffic jumped</h4>
      <p class="scn__situation">After converting a frequently queried table to EC, morning jobs take 40% longer.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> locality and decode costs.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Striped files have no node-local splits: every read pulls cells from several DataNodes over the network.</li>
          <li>Any failed node forces decoding, which costs CPU (check that native ISA-L acceleration is enabled).</li>
          <li>Keep hot tables replicated; apply EC only after data cools down.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Concepts · reliability</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>“Is EC as safe as replication?”</h4>
      <p class="scn__situation">A manager's question before approving EC.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> fault tolerance with conditions.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>RS-6-3 tolerates 3 simultaneous losses per block group vs 2 for replication 3, at half the space.</li>
          <li>Conditions: enough DataNodes and racks so units are spread out, and capacity for reconstruction traffic.</li>
          <li>Real demo: data survived 2 lost DataNodes with an identical checksum under RS-3-2, and failed only at the third.</li>
        </ul>
      </div></details>
    </article>
'''
