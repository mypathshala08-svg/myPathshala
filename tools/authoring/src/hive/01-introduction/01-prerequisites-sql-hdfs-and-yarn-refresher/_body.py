import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import *

# ---------------------------------------------------------------- story
sc = (label_box(20, 24, 140, 74, ['SQL', 'the language you speak'], 'blue', 11) +
      label_box(180, 24, 140, 74, ['HDFS', 'the cupboard that holds data'], 'green', 11) +
      label_box(340, 24, 140, 74, ['YARN', 'the manager who lends workers'], 'acc', 11) +
      t(166, 66, '+', 18, 'ink3', bold=True) + t(326, 66, '+', 18, 'ink3', bold=True) +
      arrow(486, 61, 512, 61, 'ink3', 2.2) +
      box(518, 24, 104, 74, 'violet') + t(570, 56, 'Hive', 14, 'violet', bold=True) + t(570, 74, 'SQL on Hadoop', 8.6, 'ink2'))
scene_svg = scene('Three building blocks, SQL, HDFS and YARN, combine into Apache Hive.', sc,
                  'Hive is not magic. It is <tspan font-weight="700" class="s-acc">three old friends in one coat</tspan>.')

story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“I’ll start the Hive course tonight!”</h2>
  <div class="story">
    <p class="narration">It is a Monday evening at the TiffinGo office in Kharghar. Kabir, the data intern, has just been told that next month his team will move its order analytics to <b>Apache Hive</b>. He is excited, so he opens the first page of a Hive tutorial and reads: “Hive translates HiveQL into jobs that run on YARN and read blocks from HDFS.” He reads it three times. Then he walks to Arjun Sir’s desk.</p>

{scene_svg}

K> Sir, I understood only “Hive”. What are YARN and blocks and HDFS? Am I too late to start?
A> Not at all, Kabir. Hive is built from three older ideas, and every confusing sentence in a Hive tutorial is a mix of them: <b>SQL</b> is the language you ask questions in, <b>HDFS</b> is where the data physically lives, and <b>YARN</b> is the manager that lends out computers to do the work. If one of the three is a stranger, Hive feels like magic. And magic is very hard to debug at 2 a.m.
R> So what do we do first?
A> A small doorway test with three questions. One: what does <code>GROUP BY</code> do? Two: what is a block? Three: what is a container?
K> One is easy, it adds up per city. Two… a piece of a file? Three… a Docker thing?
A> Good, one out of three, and half of another. That is exactly why this lesson exists. In about 25 minutes you will be able to answer all three, and every later Hive lesson will make sense. Riya, you join too: a refresher never hurts.
  </div>
</section>
'''

# ---------------------------------------------------------------- definition
lv = '''
LEVELS> The three prerequisites at three levels
L1> A school
      <ul>
        <li><b>SQL</b> is the way you ask the school office a question: “How many students are in each class?” You say <i>what</i> you want, not <i>how</i> to count.</li>
        <li><b>HDFS</b> is the school’s huge archive. Files are too big for one cupboard, so they are cut into pieces and kept in many cupboards (DataNodes). One register (the NameNode) knows which piece is where. Every piece has two spare copies.</li>
        <li><b>YARN</b> is the principal’s office: it decides which classroom (computer) and how many helpers a task may use. A <b>container</b> is one booked classroom with a fixed amount of memory and CPU.</li>
        <li><b>MapReduce</b> is the way the work is done: many helpers each count their own pile (<i>map</i>), then the partial counts are sent to one person per topic (<i>shuffle</i>) who adds them up (<i>reduce</i>).</li>
      </ul>
L2> How the three work together
      <ul>
        <li>A SQL query names a <b>table</b> and says what to compute. SQL does not say where the data lives or how many machines to use.</li>
        <li>On a cluster the table is a set of <b>files in HDFS</b>. Each file is cut into blocks (128 MB by default), and each block lives on 3 DataNodes.</li>
        <li>To compute, something must read those blocks. YARN gives containers on the machines <b>near the blocks</b> (data locality), so the code travels to the data and not the other way around.</li>
        <li>Each container reads its block (map), sends partial results to the right reducer (shuffle by key), and the reducers produce the final answer (reduce), which is written back to HDFS or returned to you.</li>
        <li>Hive’s whole job is to write that Java / Tez program <i>for you</i> from your SQL. You will see exactly how in Lesson 1.4.</li>
      </ul>
L3> Details that matter in production
      <ul>
        <li><b>Block size and parallelism:</b> a 1 GB file is 8 blocks of 128 MB, so up to 8 map tasks can run at once. Millions of tiny files mean millions of tiny tasks, the classic <i>small files problem</i>.</li>
        <li><b>Replication</b> (default 3) gives fault tolerance <i>and</i> more places to run a task near its data. It also triples raw storage.</li>
        <li><b>The NameNode keeps all metadata in RAM.</b> Every file, directory and block is an object. This is why Hive layouts that create very many small files hurt the whole cluster, not only your query.</li>
        <li><b>A container</b> is a bundle of memory and vcores on one NodeManager. A query that asks for more than the queue allows waits in the <b>ACCEPTED</b> state; it is not “slow”, it is queued.</li>
        <li><b>Shuffle is the expensive step:</b> data moves over the network and is sorted by key. Joins and group-bys are shuffle-heavy; Modules 5 and 8 of this course are mostly about avoiding unnecessary shuffles.</li>
        <li><b>SQL semantics carry over, but not transactions’ speed:</b> a Hive query takes seconds to minutes even on small data, because starting distributed work has fixed costs.</li>
      </ul>
/LEVELS
'''

definition = f'''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>What exactly should I know before Hive?</h2>
''' + def_block(
    'The <b>prerequisites of Apache Hive</b> are three bodies of knowledge. First, <b>relational querying with SQL</b>: tables, rows and columns, <code>SELECT</code>, <code>WHERE</code>, aggregation with <code>GROUP BY</code>, and <code>JOIN</code>s. Second, the <b>Hadoop Distributed File System (HDFS)</b>: files split into replicated blocks, with a NameNode that holds the metadata and DataNodes that hold the blocks. Third, <b>YARN and the MapReduce model</b>: a ResourceManager that grants <b>containers</b> on NodeManagers, and a processing pattern of <b>map</b>, <b>shuffle</b> and <b>reduce</b> that works in parallel on blocks. A basic familiarity with the <b>Linux command line</b> is useful for the hands-on panels.',
    'Know how to <b>ask questions of a table with SQL</b>. Know that big files are <b>cut into blocks and stored on many computers</b> (HDFS). Know that a <b>manager (YARN) lends out workers</b> and that the workers <b>count their own piles first and then combine the counts</b> (MapReduce). That is all. You do <i>not</i> need to write Java.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Table, row, column', 'A table is a grid. A row is one record (one order). A column is one field (city, amount).'),
    ('Aggregate', 'A function that turns many rows into one value: <code>SUM</code>, <code>COUNT</code>, <code>AVG</code>, <code>MAX</code>.'),
    ('JOIN', 'Combining rows of two tables where a key matches, e.g. orders with customers on <code>cust_id</code>.'),
    ('Block', 'A fixed-size piece of a file in HDFS (128 MB by default). The unit of storage and of parallel work.'),
    ('Replication', 'Keeping several copies of each block on different machines (default 3).'),
    ('NameNode / DataNode', 'The HDFS master that knows where every block is / the workers that store the blocks.'),
    ('Container', 'A reserved bundle of memory and CPU cores on one machine, granted by YARN, in which a task runs.'),
    ('Map, shuffle, reduce', 'Process each block in parallel (map), group the partial results by key across the network (shuffle), combine them per key (reduce).'),
]) + '''

  <h3>Readiness checklist: tick what you can already do</h3>
''' + table(['I can…', 'Skill', 'If not, start here'], [
    ['Write <code>SELECT … WHERE … GROUP BY … ORDER BY</code> on one table', 'SQL', 'This lesson, part 7, then the <a href="../../../sql/">SQL course</a>'],
    ['Explain what <code>JOIN</code> does with two small tables', 'SQL', 'This lesson, task 3 in part 7'],
    ['Say why a big file is split into blocks and why each block is copied', 'HDFS', 'This lesson, animation 1, then Hadoop <a href="../../../hadoop/">Module 5</a>'],
    ['Say who knows where a block is (NameNode) and who stores it (DataNode)', 'HDFS', 'Same as above'],
    ['Explain what a container is and who gives it out', 'YARN', 'This lesson, animation 2, then Hadoop <a href="../../../hadoop/">Module 11</a>'],
    ['Describe map, shuffle and reduce for “total per city”', 'MapReduce', 'This lesson, parts 4 to 5'],
    ['Open a terminal and use <code>cd</code>, <code>ls</code>, <code>cat</code>', 'Linux (optional)', '<a href="../../../linux/">Linux course</a>'],
], minw=620) + lv + '''
EXAM> Q: “What are the prerequisites for learning Hive?” A: SQL (because HiveQL is SQL-like), HDFS (because table data is stored as files in HDFS), YARN and MapReduce (because queries run as distributed jobs on YARN), and basic Linux. Then add one sentence: “Hive does not replace Hadoop, it sits on top of it.”
</section>
'''

# ---------------------------------------------------------------- types
types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Four skills, and what each one unlocks in Hive</h2>
''' + cards([
    ('SQL', 'Tables, <code>SELECT</code>, <code>WHERE</code>, <code>GROUP BY</code>, <code>JOIN</code>. HiveQL is 90% the SQL you already know, so this is the most important skill.', 'Needed from Module 2'),
    ('HDFS', 'Blocks, replication, NameNode, DataNodes. Explains where a Hive table’s data actually lives and why file layout matters.', 'Needed from Lesson 1.3'),
    ('YARN + MapReduce', 'Containers, map, shuffle, reduce. Explains what happens after you press Enter on a query and why joins are expensive.', 'Needed from Lesson 1.4'),
    ('Linux basics', '<code>cd</code>, <code>ls</code>, <code>cat</code>, <code>nano</code>, running a command and reading its output. Only for the “Run on your PC” panels.', 'Optional'),
]) + '''

  <h3>Which prerequisite matters in which Hive lesson?</h3>
''' + table(['Hive topic', 'SQL', 'HDFS', 'YARN / MapReduce'], [
    ['1.2 What is Hive', '●●', '●', '●'],
    ['1.3 Architecture and metastore', '●', '●●', '●●'],
    ['1.4 How a query becomes a job', '●●', '●●', '●●●'],
    ['2.x Tables, types, loading', '●●●', '●●', '●'],
    ['2.5 Queries and joins', '●●●', '●', '●●'],
    ['3.x Partitioning, bucketing, formats, optimisation', '●●', '●●●', '●●●'],
], minw=520) + '''
TIP> More dots mean the topic leans harder on that skill. If you only have time for one refresher before starting Module 2, make it <b>SQL</b>: <code>GROUP BY</code> and <code>JOIN</code> appear in almost every Hive example.
</section>
'''

# ---------------------------------------------------------------- steps
SAMPLE = '''import sqlite3
db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE orders (id INT, city TEXT, amount INT)")
rows = [(1, "Pune", 220), (2, "Thane", 150), (3, "Pune", 180), (4, "Mumbai", 310),
        (5, "Thane", 90), (6, "Pune", 60), (7, "Mumbai", 140), (8, "Pune", 100)]
db.executemany("INSERT INTO orders VALUES (?, ?, ?)", rows)
'''
c1 = SAMPLE + '''for city, total in db.execute("SELECT city, SUM(amount) FROM orders GROUP BY city ORDER BY city"):
    print(city, total)'''
c2 = '''import math
size_mb, block_mb = 400, 128
blocks = math.ceil(size_mb / block_mb)
print("blocks:", blocks)
print("sizes :", [min(block_mb, size_mb - i * block_mb) for i in range(blocks)], "MB")'''
c3 = '''nodes = ["DN1", "DN2", "DN3", "DN4"]
for b in range(1, 5):
    copies = [nodes[(b - 1 + k) % 4] for k in range(3)]
    print(f"B{b} ->", copies)'''
c4 = '''node_gb, container_gb = 8, 2
print("containers per node:", node_gb // container_gb)
print("containers on 3 nodes:", 3 * (node_gb // container_gb))'''
c5 = '''blocks = [[("Pune", 220), ("Thane", 150), ("Pune", 180)],
          [("Mumbai", 310), ("Thane", 90), ("Pune", 60)],
          [("Mumbai", 140), ("Pune", 100)]]
partials = []
for b in blocks:                      # map: each block summed on its own
    d = {}
    for city, amt in b:
        d[city] = d.get(city, 0) + amt
    partials.append(d)
final = {}
for d in partials:                    # shuffle + reduce: combine by city
    for city, amt in d.items():
        final[city] = final.get(city, 0) + amt
print(partials)
print(final)'''
steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>One question, five moves: from SQL to an answer on a cluster</h2>
''' + stepper([
    ('SQL: you ask a question, not a method',
     code('python', 'sql_question.py', c1, run_code(c1)),
     'You wrote <i>what</i> you want (total per city). You did not say how to loop, where the rows are or how many computers to use. That freedom is why SQL became the language of data, and why Hive wants to speak it.'),
    ('HDFS: a big file is cut into blocks',
     code('python', 'blocks.py', c2, run_code(c2)),
     'A 400 MB file becomes four blocks: three full 128 MB blocks and one 16 MB block. The last block is only as big as its data; HDFS does not waste the space. Each block can be worked on by a different machine at the same time.'),
    ('HDFS: every block is copied to three machines',
     code('python', 'replicas.py', c3, run_code(c3)),
     'Real HDFS also considers racks, but the idea is the same: no two copies of a block on one machine. If DN2 dies, every block still has at least two living copies. The NameNode’s map of “block → machines” is what makes any of this findable.'),
    ('YARN: containers are the unit of work',
     code('python', 'containers.py', c4, run_code(c4)),
     'Each NodeManager offers its memory and cores. YARN carves them into containers (here 2 GB each). A query that needs 10 containers gets them if the cluster has them, and waits if not.'),
    ('MapReduce: count your own pile, then combine',
     code('python', 'map_reduce.py', c5, run_code(c5)),
     'Each block is summed locally (map). Then the partial sums for the same city are brought together and added (shuffle + reduce). Because each block is processed independently, 3 blocks can be 3 parallel tasks, and 3,000 blocks can be 3,000. This is the engine under every Hive query.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
def qbox(extra='', title='TiffinGo analytics'):
    return ('<rect x="30" y="14" width="300" height="190" rx="10" class="s-board"/><rect x="40" y="26" width="280" height="168" rx="4" class="s-card2"/>'
            + t(180, 42, title, 9.2, bold=True)
            + t(52, 62, 'SELECT city, SUM(amount)', 8.4, 'blue', anchor='start', mono=True)
            + t(52, 75, 'FROM orders', 8.4, 'blue', anchor='start', mono=True)
            + t(52, 88, 'GROUP BY city;', 8.4, 'blue', anchor='start', mono=True) + extra)
def pbar(p, col, label):
    return ('<rect x="52" y="108" width="256" height="14" rx="5" class="s-card2"/>' + (fill(52, 108, round(256 * p), 14, col, rx=5) if p else '') + t(180, 142, label, 8.8, 'ink2'))
def result(sub=''):
    r = t(60, 124, 'city', 8.4, 'ink3', anchor='start', mono=True) + t(180, 124, 'total', 8.4, 'ink3', anchor='start', mono=True)
    for k, (c, v) in enumerate([('Mumbai', 450), ('Pune', 560), ('Thane', 240)]):
        r += t(60, 140 + k * 14, c, 9, anchor='start', mono=True) + t(180, 140 + k * 14, str(v), 9, anchor='start', mono=True)
    return '<rect x="52" y="112" width="256" height="62" rx="4" class="s-card"/>' + r + (t(180, 188, sub, 8.6, 'green', bold=True) if sub else '')
see = [
    qbox(t(180, 140, 'You type a question and press Run.', 8.8, 'ink2')),
    qbox(pbar(.1, 'acc', 'Running… 10%')),
    qbox(pbar(.55, 'acc', 'Running… 55%')),
    qbox(pbar(1, 'green', 'Done in 22 seconds')),
    qbox(result()),
    qbox(result('Same answer as sqlite on your laptop, but now for 2 TB')),
]
BX = [(10, 'Block 1', ['1 Pune 220', '2 Thane 150', '3 Pune 180']), (130, 'Block 2', ['4 Mumbai 310', '5 Thane 90', '6 Pune 60']), (250, 'Block 3', ['7 Mumbai 140', '8 Pune 100'])]
static_b = ''.join(tall(x, 18, 100, 54, f'{n} · DN{i+1}', ls, 'green') for i, (x, n, ls) in enumerate(BX))
MAPX = [10, 130, 250]
def maps(txts=None):
    o = ''
    for i, x in enumerate(MAPX):
        o += box(x, 90, 100, 40, 'acc') + t(x + 50, 101, f'map task {i+1}', 8, bold=True)
        if txts:
            o += t(x + 50, 114, txts[i][0], 7.8, 'ink2', mono=True) + t(x + 50, 125, txts[i][1], 7.8, 'ink2', mono=True)
        else:
            o += t(x + 50, 118, 'in a container', 7.8, 'ink2')
    return o
partial = [('Pune 400', 'Thane 150'), ('Mumbai 310 Thane 90', 'Pune 60'), ('Mumbai 140', 'Pune 100')]
partial[1] = ('Mumbai 310', 'Thane 90 · Pune 60')
def reducers(vals=None):
    o = ''
    for i, (x, nm) in enumerate([(10, 'Pune'), (130, 'Thane'), (250, 'Mumbai')]):
        o += box(x, 168, 100, 36, 'blue') + t(x + 50, 179, f'reduce: {nm}', 8, bold=True)
        o += t(x + 50, 196, vals[i] if vals else 'waiting', 8, 'ink2', mono=True)
    return o
shuf = ''
for sx in (60, 180, 300):
    for rx in (60, 180, 300):
        shuf += f'<path d="M{sx} 130L{rx} 168" style="fill:none;stroke:#E05A8A;stroke-width:1.1;opacity:.7"/>'
behind = [
    static_b + t(180, 232, 'The file orders.csv is stored as 3 blocks on 3 DataNodes', 8.8, 'ink2'),
    static_b + maps() + t(180, 232, 'YARN grants a container next to each block', 8.8, 'acc', bold=True),
    static_b + maps(partial) + t(180, 232, 'Map: each task adds up only its own block', 8.8, 'acc', bold=True),
    static_b + maps(partial) + shuf + reducers() + t(180, 232, 'Shuffle: partial sums travel to one reducer per city', 8.8, 'red', bold=True),
    static_b + maps(partial) + reducers(['400+60+100=560', '150+90=240', '310+140=450']) + t(180, 232, 'Reduce: each reducer adds the partial sums', 8.8, 'blue', bold=True),
    static_b + reducers(['Pune 560', 'Thane 240', 'Mumbai 450']) + t(180, 232, 'Final rows are returned to the user', 8.8, 'green', bold=True),
]
see_caps = ['Kabir types the same question he ran on SQLite, now on the full 2 TB orders table.',
            'The query starts. The progress bar moves; he does not know about blocks or containers.',
            'Hive reports 55%. Tasks are running on many machines at once.',
            'Done in 22 seconds. (Time is illustrative.)',
            'Three rows appear: Mumbai 450, Pune 560, Thane 240. Exactly what the small SQL example gave.',
            'The difference is only scale: the same SQL now runs on a cluster.']
behind_caps = ['The orders file is already cut into blocks stored on different DataNodes. We show 3 blocks and 8 rows to keep it small.',
               'YARN grants one container per block, on the machine that holds the block (data locality). A map task starts in each.',
               'Each map task adds up the amounts per city for its own block only. These are partial sums.',
               'Partial sums are sent across the network so that all values for one city meet at one reducer. This is the shuffle.',
               'Each reducer adds the partial sums it received: Pune 400+60+100 = 560, Thane 150+90 = 240, Mumbai 310+140 = 450.',
               'The three result rows are written out and shown to the user. In Hive, writing this program is the system’s job, not yours.']
two = anim_two('GROUP BY on a cluster', 'One GROUP BY: what you see, and what the cluster does',
               'A SQL query and its result as the analyst sees them', 'Blocks, map tasks, shuffle and reducers computing the same GROUP BY',
               see, behind, see_caps, behind_caps)

# ---- scenario 1: HDFS blocks
DNX = [10, 100, 190, 280]
HOLD = {0: ['B1', 'B3', 'B4'], 1: ['B1', 'B2', 'B4'], 2: ['B1', 'B2', 'B3'], 3: ['B2', 'B3', 'B4']}
BCOL = {'B1': 'acc', 'B2': 'blue', 'B3': 'violet', 'B4': 'green'}
def dns(show_nodes=True, dead=None, label=True):
    o = ''
    for i, x in enumerate(DNX):
        tone = 'red' if dead == i else 'card'
        o += box(x, 74, 70, 74, tone) + t(x + 35, 86, f'DataNode {i+1}', 7.8, 'red' if dead == i else 'ink', bold=True)
        for k, b in enumerate(HOLD[i]):
            o += chip(x + 12, 92 + k * 18, b, 'grey' if dead == i else BCOL[b], w=46, h=14)
        if dead == i:
            o += t(x + 35, 142, '✗ down', 8, 'red', bold=True)
    return o
f1 = (box(10, 40, 100, 60, 'card') + t(60, 64, 'orders.csv', 9.4, bold=True, mono=True) + t(60, 80, '400 MB', 9, 'ink2') +
      t(250, 64, 'one file, too big', 9, 'ink2') + t(250, 78, 'for comfort on one disk', 9, 'ink2') + cap('A 400 MB file arrives in HDFS.', '', 'card', y=164, h=34))
f2 = (box(10, 40, 100, 60, 'card') + t(60, 64, 'orders.csv', 9.4, bold=True, mono=True) + arrow(114, 70, 144, 70) +
      ''.join(chip(150 + k * 50, 56 + 0, b, BCOL[b], w=44, h=28, size=8.6) for k, b in enumerate(['B1', 'B2', 'B3', 'B4'])) +
      t(250, 100, '128 MB · 128 MB · 128 MB · 16 MB', 8.2, 'ink2') + cap('Step 1: cut into blocks.', 'Block size 128 MB; the last block holds the remainder.', 'blue', y=158, h=46))
f3 = dns() + t(180, 62, 'Step 2: every block gets 3 copies on 3 different DataNodes', 8.6, 'acc', bold=True) + cap('12 block copies: 400 MB of data uses 1.2 GB of disk.', '', 'acc', y=164, h=34)
f4 = (box(100, 8, 160, 40, 'blue') + t(180, 24, 'NameNode', 9, bold=True) + t(180, 38, 'B1→DN1,2,3 · B2→DN2,3,4 …', 7.6, 'ink2', mono=True) +
      ''.join(f'<path d="M{x+35} 74L180 48" style="fill:none;stroke:#8A94A0;stroke-width:1;stroke-dasharray:3 3"/>' for x in DNX) + dns() +
      cap('The NameNode remembers where each block is.', 'It stores only this small map, never the data itself.', 'blue', y=158, h=46))
f5 = dns(dead=1) + t(180, 62, 'DataNode 2 stops responding', 9, 'red', bold=True) + cap('All four blocks are still readable from other copies.', 'B1 on DN1, DN3 · B2 on DN3, DN4 · B4 on DN1, DN4.', 'green', y=158, h=46)
s1 = anim_one('Real-time scenario 1', 'HDFS: one file, four blocks, twelve copies',
              'TiffinGo uploads a 400 MB order log. Follow it from one file to blocks on four machines, then see what happens when one machine dies.',
              'A file inside HDFS', 'A 400 MB file split into four blocks, copied three times over four DataNodes, then surviving a failed DataNode',
              [f1, f2, f3, f4, f5],
              ['A 400 MB file called orders.csv is copied into HDFS.',
               'HDFS cuts it into blocks of 128 MB. The fourth block is only 16 MB because that is all that is left.',
               'Each block is copied to three different DataNodes. Block B1 sits on DataNode 1, 2 and 3, and so on. (Illustrative placement; real HDFS also considers racks.)',
               'The NameNode keeps the map of which DataNodes hold each block. It never stores the data itself.',
               'DataNode 2 fails. The NameNode notices the missing heartbeat and every block still has at least two living copies. It will re-copy the lost ones in the background.'],
              hid='scenario-hdfs')

# ---- scenario 2: YARN containers
NX = [20, 130, 240]
def slots(assign):
    """assign: dict (node,slot) -> (label, color)"""
    o = ''
    for n, x in enumerate(NX):
        o += box(x, 52, 100, 92, 'card') + t(x + 50, 64, f'NodeManager {n+1} · 8 GB', 7.8, bold=True)
        for s in range(4):
            y = 70 + s * 17
            lab, col = assign.get((n, s), (None, None))
            if lab:
                o += fill(x + 8, y, 84, 14, col, rx=3) + t(x + 50, y + 10.5, lab, 7.6, bold=True, extra=' style="fill:#fff"')
            else:
                o += f'<rect x="{x+8}" y="{y}" width="84" height="14" rx="3" style="fill:none;stroke:var(--line);stroke-width:1.2;stroke-dasharray:3 2"/>' + t(x + 50, y + 10.5, 'free 2 GB', 7.2, 'ink3')
    return o
A = {(0, 0): 'A', (1, 0): 'A', (2, 0): 'A', (0, 1): 'A'}
B = {(1, 1): 'B', (2, 1): 'B', (0, 2): 'B', (1, 2): 'B', (2, 2): 'B', (0, 3): 'B'}
def mk(*pairs):
    d = {}
    for dct, col in pairs:
        for k, v in dct.items():
            d[k] = (f'job {v} · 2 GB', col)
    return d
Cg = {(1, 3): 'C', (2, 3): 'C'}
Cg2 = {(0, 0): 'C', (1, 0): 'C', (1, 3): 'C', (2, 3): 'C'}
rm = box(110, 4, 140, 40, 'acc') + t(180, 19, 'ResourceManager', 8.8, bold=True) + t(180, 33, 'owns the whole cluster’s capacity', 7.6, 'ink2')
y1 = rm + slots({}) + cap('Three NodeManagers, 4 free slots each: 12 containers.', '', 'card', y=164, h=34)
y2 = rm + slots(mk((A, 'acc'))) + cap('Job A (a Hive query) asks for 4 containers: granted.', 'Placed on several nodes, near its data.', 'acc', y=158, h=46)
y3 = rm + slots(mk((A, 'acc'), (B, 'blue'))) + cap('Job B asks for 6 containers: granted. 10 of 12 are in use.', '', 'blue', y=164, h=34)
y4 = rm + slots(mk((A, 'acc'), (B, 'blue'), (Cg, 'violet'))) + t(180, 156, 'job C: 2 containers waiting', 8.6, 'red', bold=True) + cap('Job C wants 4 but only 2 are free: it runs on 2 and waits.', '', 'violet', y=164, h=34)
y5 = rm + slots(mk((B, 'blue'), (Cg2, 'violet'))) + cap('Job A finishes: job C gets its 2 waiting slots.', 'The query did not get “slower”; it waited in line.', 'green', y=158, h=46)
s2 = anim_one('Real-time scenario 2', 'YARN: lending out containers, and why queries wait',
              'Three TiffinGo teams run Hive queries on a tiny three-node cluster. Each box is a 2 GB container slot. Watch the ResourceManager share them.',
              'Containers in action', 'Three jobs sharing twelve container slots on three NodeManagers, one job waiting for capacity', [y1, y2, y3, y4, y5],
              ['The cluster offers 12 container slots of 2 GB each (3 nodes × 8 GB ÷ 2 GB).',
               'Job A, a Hive query, asks for 4 containers and gets them straight away.',
               'Job B asks for 6 containers and gets them. Ten of the twelve slots are now busy.',
               'Job C asks for 4 containers, but only 2 are free. It starts with 2 and the rest wait in the queue.',
               'Job A finishes. Its containers are released and job C’s waiting containers start. In a real cluster this is why a Hive query can sit in the “ACCEPTED” state for a while.'],
              hid='scenario-yarn')

# ---- scenario 3: join needs shuffle
def tbl(x, y, title, head, rows, tone):
    o = box(x, y, 96, 16 + 12 * (len(rows) + 1) + 6, tone) + t(x + 48, y + 11, title, 8, bold=True)
    o += t(x + 8, y + 24, head, 7.4, 'ink3', anchor='start', mono=True)
    for k, r in enumerate(rows):
        o += t(x + 8, y + 36 + k * 12, r, 7.8, anchor='start', mono=True)
    return o
orders_t = tbl(12, 14, 'orders · node 1', 'order cust', ['o1    1', 'o2    2', 'o3    1'], 'acc')
cust_t = tbl(12, 90, 'customers · node 2', 'cust name', ['1     Asha', '2     Rohan'], 'blue')
g1 = orders_t + cust_t + t(190, 60, 'JOIN orders ON cust = id', 8.8, 'ink2', anchor='start', mono=True) + t(190, 76, 'Rows that match must meet', 8.8, 'ink2', anchor='start') + t(190, 90, 'on one machine. But the two', 8.8, 'ink2', anchor='start') + t(190, 104, 'tables sit on different nodes.', 8.8, 'ink2', anchor='start') + cap('On one laptop a join is a lookup. On a cluster the two', 'tables live on different machines, so rows must travel.', 'card', y=158, h=46)
tags = (t(150, 36, '(1, o1)', 8, 'acc', anchor='start', mono=True) + t(150, 48, '(2, o2)', 8, 'acc', anchor='start', mono=True) + t(150, 60, '(1, o3)', 8, 'acc', anchor='start', mono=True) +
        t(150, 106, '(1, Asha)', 8, 'blue', anchor='start', mono=True) + t(150, 118, '(2, Rohan)', 8, 'blue', anchor='start', mono=True))
g2 = orders_t + cust_t + arrow(112, 48, 146, 48, 'ink3') + arrow(112, 118, 146, 118, 'ink3') + tags + t(260, 80, 'Map step:', 8.4, 'ink2', bold=True, anchor='start') + t(260, 94, 'tag every row', 8.2, 'ink2', anchor='start') + t(260, 106, 'with its join key', 8.2, 'ink2', anchor='start') + cap('Map: every row is emitted as (key, row).', 'Rows of both tables; the key is the join column.', 'acc', y=158, h=46)
def red_boxes(c0, c1):
    return (box(220, 14, 130, 56, 'violet') + t(285, 26, 'Reducer 0 (key 2)', 8, bold=True) + c0 +
            box(220, 80, 130, 62, 'green') + t(285, 92, 'Reducer 1 (key 1)', 8, bold=True) + c1)
rr = ''.join(f'<path d="{d}" style="fill:none;stroke:#E05A8A;stroke-width:1.2"/>' for d in ['M156 34L218 108', 'M156 46L218 38', 'M156 58L218 110', 'M156 104L218 112', 'M156 116L218 42'])
g3 = (t(120, 36, '(1, o1)', 8, 'acc', mono=True) + t(120, 48, '(2, o2)', 8, 'acc', mono=True) + t(120, 60, '(1, o3)', 8, 'acc', mono=True) + t(120, 106, '(1, Asha)', 8, 'blue', mono=True) + t(120, 118, '(2, Rohan)', 8, 'blue', mono=True) + rr +
      red_boxes(t(285, 44, '2: o2, Rohan', 8, mono=True), t(285, 106, '1: o1, o3, Asha', 8, mono=True)) + cap('Shuffle: key mod 2 chooses the reducer.', 'All rows with the same key arrive at the same reducer.', 'red', y=158, h=46))
g4 = red_boxes(t(285, 44, 'o2 → Rohan', 8, 'green', bold=True, mono=True), t(285, 106, 'o1 → Asha', 8, 'green', bold=True, mono=True) + t(285, 120, 'o3 → Asha', 8, 'green', bold=True, mono=True)) + cap('Reduce: pair the order rows with the customer row.', 'Output: o1→Asha, o2→Rohan, o3→Asha.', 'green', y=158, h=46)
g5 = t(180, 40, 'Join cost = moving both tables across the network', 9.4, 'red', bold=True) + ''.join(t(40, 66 + k * 16, s, 8.8, 'ink', anchor='start') for k, s in enumerate(['• Small + big table: send the small one to every mapper.', '• Both tables bucketed the same way: no shuffle needed.', '• One key with a million rows: that reducer is overloaded.'])) + cap('Hive has a tool for each case (Modules 2 and 3).', '', 'blue', y=150, h=34)
s3 = anim_one('Real-time scenario 3 · advanced', 'Why a JOIN is harder than a GROUP BY',
              'A join must bring matching rows of two tables to the same place. On a cluster that means a shuffle of both tables. This is the single most important reason Hive performance work exists.',
              'A distributed join', 'Two tables on different nodes joined by tagging rows with a key, shuffling by key and pairing them in reducers', [g1, g2, g3, g4, g5],
              ['The orders table sits on node 1 and the customers table on node 2. SQL says JOIN, but the matching rows are on different machines.',
               'Map step: each mapper emits its rows as (join key, row). Order o1 becomes (1, o1); customer Asha becomes (1, Asha).',
               'Shuffle: the key decides the reducer (here key mod 2). Keys 1 and 2 go to different reducers, but every row for one key ends up in one place.',
               'Reduce step: each reducer pairs the order rows with the customer row for its key. The join result is complete.',
               'The price of this is moving both tables over the network. Later lessons show how to avoid it with map joins, bucketing and partitioning, and how skewed keys can overload one reducer.'],
              hid='scenario-join')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>The same GROUP BY: what you see, and what the cluster does</h2>
  <p>Left: the analyst’s screen. Right: the cluster. Use the same 8 sample orders you ran in step 1, now spread over three blocks.</p>
''' + two + '''
  <p>Three live scenarios follow: how HDFS keeps a file safe, how YARN shares containers (and why queries wait), and an advanced look at why joins are expensive.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

# ---------------------------------------------------------------- real-world
art = lambda inner: inner
uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Where these three skills show up in daily Hive work</h2>
''' + usecase(
    cyl(30, 18, 60, 36, 'MySQL', 'card') + '<path d="M60 58v8" class="s-line"/>' + box(14, 66, 92, 18, 'green') + t(60, 78, 'Hive on HDFS', 8, bold=True),
    '1. An analyst moves from MySQL to a data lake',
    'A bank’s analyst has used MySQL for years. On the new platform the same <code>SELECT … GROUP BY</code> works in Hive, but the data is files in HDFS. Knowing SQL makes the first week easy; knowing blocks explains why “only 3 files” can be slower than “300 files”.',
    ['SQL skill', '*Same query', 'Files in HDFS']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + ''.join(fill(22 + k * 20, 32, 16, 26, 'green') for k in range(4)),
    '2. “Why did my query start 400 tasks?”',
    'A data engineer sees 400 map tasks for a 50 GB table. Because 50 GB is only about 400 blocks of 128 MB, that is expected: one task per block. If the same data were 40,000 tiny files, there would be 40,000 tasks and the job would crawl.',
    ['Table size', '*Blocks', 'Map tasks']) + '\n' + usecase(
    '<rect x="16" y="20" width="88" height="50" rx="6" class="s-card2"/>' + t(60, 40, 'ACCEPTED', 9, 'acc', bold=True, mono=True) + t(60, 58, 'waiting…', 8.6, 'ink2'),
    '3. The query that “does nothing”',
    'At month end, many teams submit reports together. A Hive query shows state <b>ACCEPTED</b> for ten minutes: it is waiting for YARN containers, not stuck. Admins give each team a queue so that one team cannot take everything.',
    ['Many queries', '*YARN queue', 'Wait or run']) + '\n' + usecase(
    '<rect x="14" y="18" width="92" height="54" rx="6" class="s-card2"/>' + t(60, 38, 'GROUP BY', 9, bold=True, mono=True) + t(60, 54, 'JOIN', 9, 'red', bold=True, mono=True),
    '4. Interview screening',
    'Hive interviews usually start with SQL (rank, window functions, joins), then ask “what happens when I run this on 1 TB?”. Candidates who can explain map, shuffle and reduce in plain words stand out.',
    ['SQL round', '*Cluster round', 'Offer']) + '\n' + usecase(
    '<path d="M20 66h80" class="s-line"/><rect x="26" y="40" width="18" height="26" rx="3" class="s-green"/><rect x="51" y="26" width="18" height="40" rx="3" style="fill:var(--track)"/><rect x="76" y="46" width="18" height="20" rx="3" style="fill:#8B5CF6"/>',
    '5. Cloud bills and sizing',
    'On a cloud cluster the number of containers you keep alive is money. Understanding that a query needs “blocks ÷ containers” rounds of work helps teams decide how big a cluster to rent for the night batch.',
    ['Data size', '*Parallelism', 'Cluster size and cost']) + '''
  <p class="muted">Examples are simplified; names and numbers are illustrative.</p>
</section>
'''

body = story + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
