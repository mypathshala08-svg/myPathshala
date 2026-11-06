import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
BODY = body(HERE)

META = dict(
    module='01-introduction', lesson='01-prerequisites-sql-hdfs-and-yarn-refresher', n='1.1',
    module_label='Module 1 · Start here: why Hive?',
    title='Prerequisites: SQL, HDFS and YARN in one lesson',
    desc='What to know before learning Apache Hive: SQL (SELECT, GROUP BY, JOIN), HDFS (blocks, replication, NameNode, DataNode) and YARN with MapReduce (containers, map, shuffle, reduce). A story-based refresher with animations, runnable Python and a readiness checklist.',
    og_desc='Hive is SQL + HDFS + YARN in one coat. Refresh all three in 25 minutes with animations and runnable code.',
    minutes=28, level='Beginner',
    lead='Every confusing sentence in a Hive tutorial is a mix of three older ideas: SQL, HDFS and YARN. This lesson refreshes all three through one small question, <i>total sales per city</i>, followed from a SQL prompt all the way down to blocks, containers and the shuffle, so that the rest of the course feels natural.',
    chips=['Readiness checklist', '4 animations', 'Runs in your browser (Python)'],
)

SETUP = '''import sqlite3
db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE orders (id INT, city TEXT, amount INT)")
rows = [(1, "Pune", 220), (2, "Thane", 150), (3, "Pune", 180), (4, "Mumbai", 310),
        (5, "Thane", 90), (6, "Pune", 60), (7, "Mumbai", 140), (8, "Pune", 100)]
db.executemany("INSERT INTO orders VALUES (?, ?, ?)", rows)
'''
MAIN = SETUP + '''
for city, total in db.execute("SELECT city, SUM(amount) FROM orders GROUP BY city ORDER BY SUM(amount) DESC"):
    print(f"{city:8}{total:5}")
'''
RUN = dict(
    heading='SQL you already know: the question we will send to a cluster',
    intro='<p>SQLite is a tiny database that ships with Python. Here it answers “total sales per city” for 8 orders. In Hive the <i>query</i> will look almost the same; only the scale and the machinery underneath change. Try the challenges: a filter, a join, a <code>HAVING</code> and a deliberate mistake.</p>',
    code=MAIN,
    anno=[
        ('db.execute("CREATE TABLE orders (id INT, city TEXT, amount INT)")', 'A table is a grid with named, typed columns. In Hive the table definition is stored separately (the metastore) and the rows live in files.'),
        ('SELECT city, SUM(amount) … GROUP BY city', 'Group the rows by city and add up the amounts in each group. This is the “aggregate” pattern behind most reports.'),
        ('ORDER BY SUM(amount) DESC', 'Sort the groups by their totals, biggest first.'),
    ],
    tasks=[
        dict(label='1 · Total per city', hint='Press <b>Run</b>. Then change <code>SUM</code> to <code>COUNT(*)</code> and then to <code>AVG(amount)</code>.', code=None),
        dict(label='2 · Filter first', hint='<b>Predict first:</b> how many rows survive <code>WHERE amount >= 150</code>, and what is the total per city for them? Then run it.',
             code=SETUP + '''
q = "SELECT city, COUNT(*), SUM(amount) FROM orders WHERE amount >= 150 GROUP BY city ORDER BY city"
for r in db.execute(q):
    print(r)
'''),
        dict(label='3 · A JOIN', hint='Each order has a city; this table adds the state. Predict the number of rows the join returns, then run. Add a city with no orders and see what an inner join does with it.',
             code=SETUP + '''
db.execute("CREATE TABLE cities (city TEXT, state TEXT)")
db.executemany("INSERT INTO cities VALUES (?, ?)", [("Pune", "MH"), ("Thane", "MH"), ("Mumbai", "MH")])
q = "SELECT o.id, o.city, c.state, o.amount FROM orders o JOIN cities c ON o.city = c.city WHERE o.id <= 3"
for r in db.execute(q):
    print(r)
'''),
        dict(label='4 · HAVING', hint='<code>WHERE</code> filters rows <i>before</i> grouping; <code>HAVING</code> filters groups <i>after</i>. Which cities have a total above 300?',
             code=SETUP + '''
q = "SELECT city, SUM(amount) FROM orders GROUP BY city HAVING SUM(amount) > 300 ORDER BY city"
print(db.execute(q).fetchall())
'''),
        dict(label='5 · Spot the error', hint='This query crashes. Read the last line of the error, find the typo and fix it.', expect='error',
             code=SETUP + '''
print(db.execute("SELECT city, SUM(amout) FROM orders GROUP BY city").fetchall())
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: is your Hadoop ready?',
    intro='<p>If you built the Hadoop lab from the Hadoop course, run these three commands on the master node. They check the three prerequisites in the real world: HDFS is up, YARN is up, and Java processes are running. <b>The outputs below are typical examples written for this lesson, not a recording from a particular machine</b>: your host names, IDs and sizes will differ.</p>',
    items=[
        dict(title='1 · Which Hadoop daemons are running?', cmd='jps', file='Terminal (master)',
             output='4821 NameNode\n5210 ResourceManager\n5533 SecondaryNameNode\n6012 Jps',
             note='NameNode (HDFS master) and ResourceManager (YARN master) must both be present. On worker nodes you would see DataNode and NodeManager instead.'),
        dict(title='2 · Is HDFS answering?', cmd='hdfs dfs -ls /\nhdfs dfsadmin -report | head -n 8', file='Terminal (master)',
             output='Found 2 items\ndrwxr-xr-x   - hadoop supergroup          0 2026-10-20 09:12 /data\ndrwxrwx---   - hadoop supergroup          0 2026-10-20 09:10 /tmp\nConfigured Capacity: 1610612736000 (1.46 TB)\nDFS Used: 3221225472 (3 GB)\nLive datanodes (3):',
             note='“Live datanodes (3)” means three workers are reporting blocks. If you see 0, HDFS is up but has nowhere to store data.'),
        dict(title='3 · Is YARN answering?', cmd='yarn node -list', file='Terminal (master)',
             output='Total Nodes:3\n         Node-Id\t     Node-State\tNode-Http-Address\tNumber-of-Running-Containers\n worker1:41233\t        RUNNING\t     worker1:8042\t                           0\n worker2:39871\t        RUNNING\t     worker2:8042\t                           0\n worker3:44012\t        RUNNING\t     worker3:8042\t                           0',
             note='Each RUNNING NodeManager offers memory and cores for containers. If a worker is missing here, jobs will never run on it.'),
    ],
)

TRACE = dict(
    heading='Map, shuffle and reduce for GROUP BY, one line at a time',
    intro='<p>This tiny program does by hand what a cluster does for a <code>GROUP BY</code>: each block is summed on its own, then the partial sums are combined by city. Watch the dictionaries fill up.</p>',
    code='''blocks = [[("Pune", 220), ("Thane", 150)],
          [("Pune", 180), ("Mumbai", 310)]]
partials = []
for b in blocks:
    d = {}
    for city, amt in b:
        d[city] = d.get(city, 0) + amt
    partials.append(d)
final = {}
for d in partials:
    for city, amt in d.items():
        final[city] = final.get(city, 0) + amt
print(final)
''',
    notes={4: 'Map :: Each block is handled on its own, as a separate map task would be.', 10: 'Reduce :: Now combine the partial sums by city, as the reducers do after the shuffle.'},
)

WORKED_INTRO = 'Three tasks a data engineer does in the first week with Hive: size a table in blocks, rebuild a GROUP BY by hand, and check whether a query will have to wait for YARN. Each one runs live and is traced in memory.'
EXAMPLES = [
    dict(level='b', tag='HDFS · storage planning', title='How many blocks and how much disk does a file need?',
         problem='<p>TiffinGo stores daily order logs of <b>250 MB</b>, <b>1,000 MB</b> and <b>5 MB</b>. With a block size of <b>128 MB</b> and replication <b>3</b>, print the number of blocks and the raw disk used for each file.</p>',
         inp='sizes (MB): 250, 1000, 5 · block 128 MB · replication 3',
         approach=['Blocks = file size ÷ block size, rounded up.', 'Raw disk = file size × replication (the last block is only as big as its data).', 'Print one line per file.'],
         code='''import math
block, repl = 128, 3
for size in [250, 1000, 5]:
    blocks = math.ceil(size / block)
    print(f"{size:5} MB -> {blocks} block(s), {size * repl} MB raw disk")
''', notes={4: 'Blocks :: Round up: a partial block still counts as a block, but it only uses the space of its data.'},
         tryit='Change the block size to 256 MB. How many blocks does the 1,000 MB file need now? Fewer blocks means fewer map tasks, but less parallelism.'),
    dict(level='i', tag='MapReduce · by hand', title='Rebuild GROUP BY from map and reduce',
         problem='<p>Three blocks hold these order rows. Compute the <b>total amount per city</b> the cluster way: a map step that makes partial sums per block, then a reduce step that combines them. Finally check that no money was lost on the way.</p>',
         inp='block 1: Pune 220, Thane 150 · block 2: Mumbai 310, Pune 60 · block 3: Mumbai 140, Pune 100',
         approach=['Map: for each block build a dictionary city → partial sum.', 'Reduce: add the partial sums for the same city.', 'Check that the grand total equals the sum of all rows.'],
         code='''blocks = [[("Pune", 220), ("Thane", 150)],
          [("Mumbai", 310), ("Pune", 60)],
          [("Mumbai", 140), ("Pune", 100)]]
partials = []
for b in blocks:
    d = {}
    for city, amt in b:
        d[city] = d.get(city, 0) + amt
    partials.append(d)
final = {}
for d in partials:
    for city, amt in d.items():
        final[city] = final.get(city, 0) + amt
print(sorted(final.items()))
print("nothing lost:", sum(final.values()) == sum(a for b in blocks for _, a in b))
''', notes={5: 'Map :: Partial sums for one block.', 11: 'Reduce :: Combine partial sums across blocks.'},
         tryit='Add a fourth block with one Pune row. Only the partial sums are sent over the network, not the rows: that is why a map-side sum (a combiner) saves bandwidth.'),
    dict(level='a', tag='YARN · capacity', title='Will my query run now, or wait?',
         problem='<p>A queue owns <b>40%</b> of a cluster with <b>20 nodes × 64 GB</b> offered to YARN. Each Hive query needs <b>1 ApplicationMaster container of 2 GB</b> plus <b>30 task containers of 4 GB</b>. Three analysts run 1 query each. Print how much memory the queue has, how much one query needs, and how many queries can run at once.</p>',
         inp='20 nodes × 64 GB · queue 40% · query: 2 GB + 30 × 4 GB',
         approach=['Queue memory = nodes × memory × share.', 'One query needs 2 + 30 × 4 GB.', 'Concurrent queries = queue memory ÷ query memory, rounded down.'],
         code='''nodes, node_gb, share = 20, 64, 0.40
queue_gb = nodes * node_gb * share
query_gb = 2 + 30 * 4
running = int(queue_gb // query_gb)
print(f"queue memory: {queue_gb:.0f} GB")
print(f"one query needs: {query_gb} GB")
print(f"queries that fit at once: {running}")
print("3 analysts submit ->", running, "run,", max(0, 3 - running), "wait")
''', notes={2: 'Capacity :: 20 × 64 × 0.40 = 512 GB for this queue.'},
         tryit='If analysts set their tasks to 8 GB containers, how many queries fit? Bigger containers do not always make a query faster, but they make fewer fit.'),
]

QUIZ = mix([
    dict(q='What does GROUP BY city with SUM(amount) return?', options=['Every row sorted by city', 'One row per city with the total amount of its rows', 'Only the city with the largest amount', 'The number of columns in the table'], answer=1,
         why='<code>GROUP BY</code> puts rows with the same city in one group and the aggregate (<code>SUM</code>) turns each group into a single row.'),
    dict(q='A 400 MB file is stored in HDFS with 128 MB blocks. How many blocks does it have?', options=['3', '4', '5', '1'], answer=1,
         why='128 + 128 + 128 = 384, and 16 MB remain, so there are <b>4</b> blocks. The last block is only 16 MB.'),
    dict(q='Which HDFS daemon knows which DataNodes hold each block?', options=['DataNode', 'NodeManager', 'NameNode', 'ResourceManager'], answer=2,
         why='The <b>NameNode</b> keeps the file and block metadata. DataNodes store the bytes.'),
    dict(q='Why is every HDFS block stored on three machines by default?', options=['To make files load three times faster only', 'To survive machine failures and give more places to run a task', 'Because blocks are 3 MB', 'Because YARN needs three copies'], answer=1,
         why='Replication gives fault tolerance and flexibility for scheduling tasks near their data. The cost is three times the raw storage.'),
    dict(q='What is a YARN container?', options=['A Docker image of the database', 'A reserved bundle of memory and CPU on one machine in which a task runs', 'A folder in HDFS', 'A type of SQL table'], answer=1,
         why='A container is a slice of a NodeManager’s memory and cores granted by the ResourceManager. (YARN containers are not Docker containers, although YARN can run Docker.)'),
    dict(q='In MapReduce, what does the shuffle do?', options=['Sorts the final answer for display', 'Moves partial results across the network so that all values for one key meet at one reducer', 'Copies blocks to three DataNodes', 'Compiles the SQL'], answer=1,
         why='The shuffle groups map outputs by key and sends each key to its reducer. It is usually the most expensive step.'),
    dict(q='A Hive query stays in state ACCEPTED for ten minutes. What is the most likely reason?', options=['The SQL has a syntax error', 'YARN has no free containers for it yet', 'HDFS has lost the table', 'The metastore is deleted'], answer=1,
         why='ACCEPTED means YARN has received the application but has not yet started it, usually because the queue has no free capacity.'),
])

REVISION = [
    '<b>SQL</b>: <code>SELECT … FROM … WHERE … GROUP BY … HAVING … ORDER BY</code>; <code>JOIN</code> matches rows on a key.',
    '<b>HDFS</b>: big files are cut into <b>blocks</b> (128 MB), each copied <b>3 times</b> on different DataNodes.',
    '<b>NameNode</b> = metadata master (RAM). <b>DataNode</b> = stores blocks. Clients read bytes directly from DataNodes.',
    '<b>YARN</b>: ResourceManager (cluster brain) + NodeManagers (per machine). Work runs in <b>containers</b> (memory + vcores).',
    '<b>MapReduce</b>: map (per block, parallel) → shuffle (group by key over the network) → reduce (combine per key).',
    'One map task per block: 1 GB ≈ 8 blocks ≈ 8 map tasks. Many tiny files = many tiny tasks.',
    'Joins and group-bys need a shuffle; the shuffle is the expensive step.',
    'Hive does not replace Hadoop. It writes the distributed program for you from SQL.',
]
FAQ = [
    ('Do I need to know Java to learn Hive?', 'No. You write HiveQL, which is SQL-like. Java only matters when you write custom functions (UDFs) in a later module, and even then Python and other options exist.'),
    ('How much SQL do I really need before Hive?', 'Comfortable use of SELECT, WHERE, GROUP BY, ORDER BY and INNER/LEFT JOIN is enough to start. Window functions and subqueries come up later and are taught when needed.'),
    ('Do I need to install Hadoop before starting?', 'No. All concepts in this course can be followed from the lessons and the in-browser Python examples. The “Run on your PC” panels are optional; they show real commands for learners who have built the Hadoop lab.'),
    ('What is the difference between a YARN container and a Docker container?', 'A YARN container is a reservation of memory and CPU on one node, granted by the ResourceManager, in which a task process runs. A Docker container is a packaged, isolated runtime environment. YARN can optionally launch tasks inside Docker containers, but the two ideas are different.'),
    ('Why does HDFS use such large blocks (128 MB) compared with a normal file system (4 KB)?', 'Large blocks keep the number of blocks, and therefore the NameNode’s metadata and the disk seek overhead, small, and they make streaming reads of large files efficient. It suits big sequential scans, which is what analytics does.'),
]

PRACTICE_INTRO = 'Short programs that refresh the three prerequisites: SQL aggregation, HDFS arithmetic and the map/reduce idea. Predict the output before you open the solution.'
PROBLEMS = [
    dict(level='easy', title='Total per city', stmt='Using SQL, print the number of orders and the total amount per city, sorted by city.', inp='orders: Pune 220, Thane 150, Pune 180, Mumbai 310',
         code='''import sqlite3
db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE orders (city TEXT, amount INT)")
db.executemany("INSERT INTO orders VALUES (?, ?)", [("Pune", 220), ("Thane", 150), ("Pune", 180), ("Mumbai", 310)])
for r in db.execute("SELECT city, COUNT(*), SUM(amount) FROM orders GROUP BY city ORDER BY city"):
    print(r)
''', explain='<code>COUNT(*)</code> counts rows in each group, <code>SUM</code> adds the amounts. This single pattern is behind most dashboards.'),
    dict(level='easy', title='Blocks of a file', stmt='A file is 1,000 MB and the block size is 128 MB. How many blocks, and how big is the last one?', inp='1000 MB, 128 MB',
         code='''import math
size, block = 1000, 128
n = math.ceil(size / block)
print(n, "blocks; last block", size - (n - 1) * block, "MB")
''', explain='7 full blocks (896 MB) plus a last block of 104 MB. The last block only uses the space it needs.'),
    dict(level='easy', title='Raw disk with replication', stmt='A 2 TB table is stored with replication 3. How much raw disk does it use?', inp='2 TB × 3',
         code='print(2 * 3, "TB of raw disk")\n', explain='6 TB. This is why capacity planning for HDFS always multiplies by the replication factor.'),
    dict(level='medium', title='HAVING vs WHERE', stmt='List cities whose total is more than 300, but count only orders of at least 100.', inp='orders: Pune 220, Thane 90, Pune 60, Mumbai 310, Thane 150, Pune 100',
         code='''import sqlite3
db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE orders (city TEXT, amount INT)")
db.executemany("INSERT INTO orders VALUES (?, ?)", [("Pune", 220), ("Thane", 90), ("Pune", 60), ("Mumbai", 310), ("Thane", 150), ("Pune", 100)])
q = "SELECT city, SUM(amount) FROM orders WHERE amount >= 100 GROUP BY city HAVING SUM(amount) > 300 ORDER BY city"
print(db.execute(q).fetchall())
''', explain='<code>WHERE</code> removes small orders before grouping (Pune keeps 220 + 100 = 320, Thane keeps 150, Mumbai 310). <code>HAVING</code> then keeps groups above 300: Mumbai and Pune.'),
    dict(level='medium', title='Left join to find cities with no orders', stmt='Find the cities in the cities table that have no orders at all.', inp='cities: Pune, Thane, Nashik · orders: Pune, Pune, Thane',
         code='''import sqlite3
db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE cities (city TEXT)")
db.execute("CREATE TABLE orders (city TEXT)")
db.executemany("INSERT INTO cities VALUES (?)", [("Pune",), ("Thane",), ("Nashik",)])
db.executemany("INSERT INTO orders VALUES (?)", [("Pune",), ("Pune",), ("Thane",)])
q = "SELECT c.city FROM cities c LEFT JOIN orders o ON c.city = o.city WHERE o.city IS NULL"
print(db.execute(q).fetchall())
''', explain='A <code>LEFT JOIN</code> keeps every row from the left table; where no order matches, the right side is <code>NULL</code>. Filtering on <code>IS NULL</code> finds the unmatched cities. This anti-join pattern is common in Hive too.'),
    dict(level='medium', title='Which DataNode holds what?', stmt='With 4 DataNodes and blocks B1..B4, place 3 replicas of each block on consecutive DataNodes (round robin). Then simulate DN2 failing and list blocks that still have at least one copy.', inp='nodes DN1..DN4, 4 blocks, replication 3',
         code='''nodes = ["DN1", "DN2", "DN3", "DN4"]
place = {f"B{b}": [nodes[(b - 1 + k) % 4] for k in range(3)] for b in range(1, 5)}
down = "DN2"
for blk, where in place.items():
    alive = [n for n in where if n != down]
    print(blk, where, "-> alive:", alive)
''', explain='Every block lost at most one copy, so all four blocks are still readable. The NameNode would now re-replicate the under-replicated ones.'),
    dict(level='business', title='How many map tasks?', stmt='A table is 50 GB (51,200 MB) stored as one large file with 128 MB blocks. How many map tasks will a full scan start? What if the same data were stored as 40,000 files of about 1.3 MB each?', inp='51,200 MB; 128 MB blocks; or 40,000 small files',
         code='''import math
total_mb, block = 51200, 128
print("one big file :", math.ceil(total_mb / block), "map tasks")
print("40,000 files :", 40000, "map tasks (at least one per file)")
''', explain='400 tasks versus 40,000. Each task has start-up overhead, so the small-files layout is far slower even though the data is identical. Modules 2 and 3 show how Hive avoids this.'),
    dict(level='business', title='Queue planning for month-end', stmt='Month-end reports need 12 queries at the same time. Each needs 90 GB of containers. How much memory must the queue own? How many queries can run if it owns only 400 GB?', inp='12 queries × 90 GB; queue of 400 GB',
         code='''need = 12 * 90
print("memory needed:", need, "GB")
fit = 400 // 90
print("queries running in 400 GB:", fit, "| waiting:", 12 - fit)
''', explain='1,080 GB are needed to run all together. With 400 GB only 4 run and 8 wait; they are not failing, they are queued. Admins use this calculation to size queues and to decide whether to stagger the reports.'),
]

SCN_INTRO = 'Interviewers for Hive roles usually begin with the prerequisites. These situations test whether you can connect SQL, HDFS and YARN.'
SCENARIOS = (
    scn('Any company · concepts', 'Fresher', '“What happens to my GROUP BY on a cluster?”',
        'The interviewer says: “You wrote SELECT city, SUM(amount) … GROUP BY city on a 2 TB table. Walk me through what happens underneath, without naming any tool.”',
        'do you understand parallel partial work, the shuffle and the reduce, rather than just SQL syntax?',
        '''<ol>
          <li>The table is stored as blocks on many machines. A task is started for each block, close to where the block is stored.</li>
          <li>Each task adds up the amounts per city for its own block (map).</li>
          <li>The partial sums are sent over the network so that all values for one city arrive at the same reducer (shuffle).</li>
          <li>Each reducer adds the partial sums for its cities and writes the final rows (reduce).</li>
        </ol>''', 'saying “the database loads the whole table and loops over it”.') +
    scn('Operations · troubleshooting', 'Fresher', 'The query is not running',
        'An analyst says: “My report has been stuck at ACCEPTED for 15 minutes. Is Hive broken?”',
        'can you tell waiting for capacity from failure?',
        '''<ul>
          <li>ACCEPTED means YARN has the application but has not yet given it its first container; the queue is probably full of other jobs.</li>
          <li>Check the ResourceManager UI (port 8088): which queue, how much is used, who is using it.</li>
          <li>Options: wait, ask for a larger queue share, reduce the query’s container size or parallelism, or reschedule heavy reports.</li>
        </ul>''', 'killing and resubmitting the job repeatedly; that sends it to the back of the queue again.') +
    scn('Data platform · design', 'Mid-level', 'Millions of tiny files',
        'A team lands 40,000 small files a day (about 1 MB each) into HDFS and complains that every query is slow and the NameNode is using lots of memory.',
        'do you connect block size, tasks and NameNode memory?',
        '''<ol>
          <li>Each file is at least one block object and one task: 40,000 files means 40,000 tiny tasks with start-up overhead each.</li>
          <li>The NameNode keeps every file and block as an object in RAM, so millions of small files can exhaust its heap.</li>
          <li>Fix: compact files into larger ones (for example hourly or daily), store in a columnar format, and design the writers to produce fewer, larger files.</li>
        </ol>''', 'adding more worker nodes; the bottleneck is the number of files, not the number of workers.') +
    scn('Any company · concepts', 'Fresher', '“Is Hive a database?”',
        'The interviewer asks: “Hive has tables and SQL. So is it a database like MySQL?”',
        'do you know that Hive provides SQL on top of Hadoop rather than its own storage and engine?',
        '''<ul>
          <li>Not quite. Hive stores table <b>definitions</b> in a metastore, while the <b>data</b> stays as files in HDFS (or cloud storage).</li>
          <li>Queries are turned into distributed jobs on YARN, so they are built for large scans and take seconds or minutes, not milliseconds.</li>
          <li>It is great for analytics on big data, and not designed for thousands of tiny transactions per second like MySQL. (We study this in detail in Lesson 1.2.)</li>
        </ul>''', 'a flat “yes” or “no”; explain what is the same (SQL) and what is different (storage and engine).')
)
