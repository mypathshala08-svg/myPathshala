import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
BODY = body(HERE)

META = dict(
    module='03-querying', lesson='04-order-sort-distribute-cluster-by', n='3.4',
    module_label='Module 3 · Querying with HiveQL',
    title='ORDER BY, SORT BY, DISTRIBUTE BY and CLUSTER BY',
    desc='The four ordering clauses of HiveQL, shown with the real files written by three reducers in Hive 4.2.1: ORDER BY (total order, one reducer), SORT BY (sorted per reducer), DISTRIBUTE BY (same key to the same reducer), CLUSTER BY (distribute + sort), DISTRIBUTE BY + SORT BY, strict mode for ORDER BY without LIMIT, NULLS FIRST/LAST, ORDER BY positions and top-N.',
    og_desc='Same 12 orders, three reducers, four clauses: open the real output files and see exactly what ORDER BY, SORT BY, DISTRIBUTE BY and CLUSTER BY do.',
    minutes=28, level='Beginner → Advanced',
    lead='Hive has four ways to order data, and interviewers love asking about them. Instead of describing them, this lesson runs all four on the same twelve TiffinGo orders with three reducers and opens the files each reducer wrote. You will see why SORT BY gave three overlapping sorted files, why ORDER BY wrote one, and how DISTRIBUTE BY with SORT BY gives you per-city order. <b>All outputs are real</b>, from Hive 4.2.1.',
    chips=['Real reducer output files', 'Strict mode and NULL order', 'Interview favourite', 'Runs in your browser (Python)'],
)

MAIN = '''# Simulate 3 reducers: DISTRIBUTE BY city, then SORT BY within each reducer
rows = [("Mumbai", 530), ("Mumbai", 500), ("Pune", 410), ("Thane", 300), ("Mumbai", 180),
        ("Pune", 40), ("Mumbai", 590), ("Delhi", 310), ("Pune", 460), ("Thane", 250)]
R = 3

reducers = [[] for _ in range(R)]
for city, amount in rows:
    r = sum(city.encode()) % R            # a simple hash of the key
    reducers[r].append((city, amount))

for i, part in enumerate(reducers):
    part.sort(key=lambda x: (x[0], -x[1]))      # SORT BY city, amount DESC
    print(f"reducer {i}:", part)
'''
RUN = dict(
    heading='Run the code: reducers by hand',
    intro='<p>These programs imitate the shuffle: a hash of the distribute key picks a reducer, each reducer sorts its own rows, and ORDER BY merges everything into one list. Press <b>Run</b>, then try the challenges. (Python’s simple hash differs from Hive’s, so cities may land on other reducers than in the lab.)</p>',
    code=MAIN,
    anno=[
        ('r = sum(city.encode()) % R            # a simple hash of the key', 'DISTRIBUTE BY: hash(key) mod number-of-reducers. Equal keys always land on the same reducer.'),
        ('part.sort(key=lambda x: (x[0], -x[1]))      # SORT BY city, amount DESC', 'SORT BY works inside one reducer only.'),
    ],
    tasks=[
        dict(label='1 · DISTRIBUTE + SORT', hint='Press <b>Run</b>. Check that each city appears in only one reducer. Change R to 2.', code=None),
        dict(label='2 · SORT BY without a key', hint='<b>Predict first:</b> rows are dealt to reducers round-robin and sorted per reducer. Is the combined list in order?',
             code='''amounts = [530, 500, 410, 300, 180, 40, 590, 480, 460, 360, 310, 250]
R = 3
parts = [sorted(amounts[i::R], reverse=True) for i in range(R)]   # SORT BY amount DESC
for i, p in enumerate(parts):
    print("reducer", i, p)
combined = sum(parts, [])
print("globally sorted?", combined == sorted(amounts, reverse=True))
'''),
        dict(label='3 · ORDER BY = one reducer', hint='Merge the sorted parts into one total order, like the single ORDER BY reducer. heapq.merge does a k-way merge.',
             code='''import heapq
parts = [[530, 300, 40], [500, 180, 480], [590, 410, 250]]
parts = [sorted(p, reverse=True) for p in parts]
print(list(heapq.merge(*parts, reverse=True)))
'''),
        dict(label='4 · Top-N cheaply', hint='Each map task keeps only its top 2; the final step sorts just 6 numbers instead of 12. Is the answer the same?',
             code='''tasks = [[530, 500, 410, 300], [180, 40, 590, 480], [460, 360, 310, 250]]
local_top = [sorted(t, reverse=True)[:2] for t in tasks]
final = sorted(sum(local_top, []), reverse=True)[:2]
print("local tops:", local_top, "-> top 2:", final)
print("same as full sort:", final == sorted(sum(tasks, []), reverse=True)[:2])
'''),
        dict(label='5 · Spot the error', hint='The script assumes SORT BY gives a global order and checks the first row is the maximum. It fails. Use a single sorted list (ORDER BY) instead.', expect='error',
             code='''reducer_files = [[590, 480, 460], [500, 410, 300], [530]]     # SORT BY output, 3 files
combined = sum(reducer_files, [])
assert combined == sorted(combined, reverse=True), "SORT BY output is only sorted per file"
print("ok")
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: reproduce the files',
    intro='<p>Run each statement and list the output folder in a terminal (<code>docker exec hiveserver2 ls /data/exports/…</code>). <b>Outputs are real</b>, from Hive 4.2.1.</p>',
    items=[
        dict(title='1 · Which settings are active?', cmd='SET hive.strict.checks.orderby.no.limit;\nSET hive.orderby.position.alias;\nSET hive.default.nulls.last;', file='Beeline',
             output='| hive.strict.checks.orderby.no.limit=false  |\n| hive.orderby.position.alias=true  |\n| hive.default.nulls.last=true  |\n(table borders removed)',
             note='These three settings explain the behaviour in Step 6. Companies often switch the strict check on for shared clusters.'),
        dict(title='2 · Count the output files', cmd="SET mapred.reduce.tasks=3;\n-- run Steps 1–5, then:\n$ for d in sortby orderby distby clusterby distsort; do echo $d: $(ls /data/exports/$d | grep -v crc); done", file='Beeline + Terminal',
             output='sortby: 000000_0 000001_0 000002_0\norderby: 000000_0\ndistby: 000000_0 000001_0 000002_0\nclusterby: 000000_0 000001_0 000002_0\ndistsort: 000000_0 000001_0 000002_0',
             note='One file per reducer. ORDER BY used one reducer for the final sort even though three were requested.'),
        dict(title='3 · NULLS FIRST in ascending order', cmd='SELECT payment, orders FROM payment_mix ORDER BY orders NULLS FIRST LIMIT 3;', file='Beeline',
             output='+------------+---------+\n|  payment   | orders  |\n+------------+---------+\n| Crypto     | NULL    |\n| BNPL       | 0       |\n| Gift card  | 0       |\n+------------+---------+',
             note='With the default (nulls last for ASC) Crypto would come last; NULLS FIRST moves it to the top.'),
    ],
)

TRACE = dict(
    heading='Routing rows to reducers, one row at a time',
    intro='<p>Watch each row’s key decide its reducer, then each reducer’s list being sorted on its own.</p>',
    code='''rows = [("Pune", 410), ("Delhi", 310), ("Pune", 40), ("Mumbai", 590)]
reducers = {0: [], 1: []}
for city, amount in rows:
    r = len(city) % 2
    reducers[r].append(amount)
for r in reducers:
    reducers[r].sort(reverse=True)
print(reducers)
''',
    notes={4: 'Route :: A hash of the key picks the reducer; both Pune rows go to the same place.', 7: 'Sort :: Each reducer sorts only its own list.'},
)

WORKED_INTRO = 'Three ordering tasks: a cheap top-N, a per-city ranking file, and checking whether an export really needs a global sort.'
EXAMPLES = [
    dict(level='b', tag='Reporting · top-N', title='Top 3 cities by revenue',
         problem='<p>From the real revenue per city, print the top 3, as <code>ORDER BY revenue DESC LIMIT 3</code>.</p>',
         inp='8 cities with revenue from the lab',
         approach=['Sort the cities by revenue, descending.', 'Take the first three.', 'Print them.'],
         code='''rev = {"Mumbai": 2941120, "Bengaluru": 2724070, "Pune": 2344660, "Hyderabad": 1763190,
       "Delhi": 1614230, "Thane": 1408910, "Navi Mumbai": 1172750, "Chennai": 752250}
top3 = sorted(rev.items(), key=lambda kv: -kv[1])[:3]
for city, r in top3:
    print(f"{city:10} {r:,}")
''', notes={3: 'Top-N :: Sort, then cut at 3.'},
         tryit='Matches the real Hive result in Step 6 (Mumbai, Bengaluru, Pune).'),
    dict(level='i', tag='Per-key output', title='Each city’s orders from highest to lowest',
         problem='<p>Group the 12 sample orders by city and order each group by amount descending, like <code>DISTRIBUTE BY city SORT BY city, amount DESC</code>.</p>',
         inp='12 real sample orders (city, amount)',
         approach=['Group amounts by city.', 'Sort cities by name and amounts high → low.', 'Print one line per city.'],
         code='''rows = [("Mumbai", 530), ("Mumbai", 500), ("Pune", 410), ("Thane", 300), ("Mumbai", 180), ("Pune", 40),
        ("Mumbai", 590), ("Mumbai", 480), ("Pune", 460), ("Hyderabad", 360), ("Delhi", 310), ("Thane", 250)]
groups = {}
for city, amount in rows:
    groups.setdefault(city, []).append(amount)
for city in sorted(groups):
    print(city, sorted(groups[city], reverse=True))
''', notes={5: 'Group :: Like DISTRIBUTE BY: all rows of a city together.'},
         tryit='Compare with the real distsort files in Step 5: Mumbai 590, 530, 500, 480, 180 and Pune 460, 410, 40, the same per-city order.'),
    dict(level='a', tag='Performance · decision', title='Does this export need ORDER BY?',
         problem='<p>For each export request decide the cheapest correct clause: a top-N for people, a per-key stream for a program, or no ordering at all.</p>',
         inp='requests: top 20 customers for CEO · events per customer for a sessionising script · full order dump for a data lake',
         approach=['Top-N for people → ORDER BY … LIMIT.', 'Per-key processing → DISTRIBUTE BY key SORT BY key, time.', 'Bulk dump → no ordering.'],
         code='''requests = [("top 20 customers for CEO", "top"), ("events per customer for a script", "per_key"),
            ("full order dump for the data lake", "bulk")]
choice = {"top": "ORDER BY spend DESC LIMIT 20",
          "per_key": "DISTRIBUTE BY customer_id SORT BY customer_id, event_ts",
          "bulk": "no ORDER BY (keep parallel writes)"}
for name, kind in requests:
    print(f"{name:35} -> {choice[kind]}")
''', notes={5: 'Decide :: Match the clause to who consumes the data.'},
         tryit='Add “a sorted file for a legacy system that requires total order” and note that it really needs ORDER BY; plan time for the single reducer.'),
]

QUIZ = mix([
    dict(q='Beginner: Which clause guarantees a total order of the whole result?', options=['SORT BY', 'ORDER BY', 'DISTRIBUTE BY', 'CLUSTER BY'], answer=1,
         why='ORDER BY wrote one fully sorted file even with 3 reducers requested.'),
    dict(q='Beginner: With 3 reducers, what does SORT BY amount DESC produce?', options=['One sorted file', 'Three files, each sorted, but not ordered across files', 'Unsorted files', 'An error'], answer=1,
         why='The 530 order ended up alone in the third file, after 40 in the second.'),
    dict(q='Beginner: What does DISTRIBUTE BY city guarantee?', options=['Rows sorted by city', 'All rows of a city go to the same reducer', 'One file per city', 'A total order'], answer=1,
         why='Mumbai and Pune were each in one file, but shared it: no one-file-per-city promise and no sorting.'),
    dict(q='Intermediate: CLUSTER BY city is equivalent to…', options=['ORDER BY city', 'DISTRIBUTE BY city SORT BY city', 'SORT BY city', 'GROUP BY city'], answer=1,
         why='And it sorts ascending only; use DISTRIBUTE BY + SORT BY … DESC for other orders.'),
    dict(q='Intermediate: Why can ORDER BY on billions of rows be slow?', options=['It uses no reducers', 'The final total sort runs in a single reducer', 'It disables vectorisation', 'It writes ORC'], answer=1,
         why='Use LIMIT, per-key sorting or no sort when a global order is not needed.'),
    dict(q='Intermediate: What does hive.strict.checks.orderby.no.limit=true do?', options=['Adds LIMIT 100 automatically', 'Rejects ORDER BY without LIMIT', 'Makes ORDER BY use 3 reducers', 'Sorts NULLs first'], answer=1,
         why='Real message: “Order by-s without limit are disabled for safety reasons”.'),
    dict(q='Advanced: With hive.default.nulls.last=true, where do NULLs go in ORDER BY x DESC?', options=['Last', 'First', 'Removed', 'Random'], answer=1,
         why='Nulls last applies to ascending order; descending reverses it, so Crypto (NULL) came first until NULLS LAST was added.'),
    dict(q='Advanced: Why is ORDER BY … LIMIT 10 cheap even on a huge table?', options=['It reads only 10 rows from disk', 'Each task keeps its own top 10, so the final reducer merges only a few rows', 'It skips the shuffle completely', 'It uses the metastore'], answer=1,
         why='All rows are still read, but very few are shuffled and sorted at the end.'),
])

REVISION = [
    '<b>ORDER BY</b>: total order, final sort in <b>one reducer</b>; use with LIMIT on big data.',
    '<b>SORT BY</b>: sorted <b>within each reducer</b>; files overlap; no global order.',
    '<b>DISTRIBUTE BY k</b>: same k → same reducer (hash), unsorted; several keys can share a reducer.',
    '<b>CLUSTER BY k</b> = DISTRIBUTE BY k SORT BY k, ascending only. Not the same as bucketing (CLUSTERED BY … INTO n BUCKETS).',
    '<code>DISTRIBUTE BY k SORT BY k, x DESC</code>: per-key groups in any order.',
    'Reducers for SORT/DISTRIBUTE/CLUSTER: estimated or <code>mapred.reduce.tasks</code>; ORDER BY ignores it for the final sort.',
    '<code>hive.strict.checks.orderby.no.limit</code> (default false), <code>hive.default.nulls.last</code> (true: NULLs last ASC, first DESC), <code>NULLS FIRST|LAST</code>, <code>ORDER BY 2</code> allowed.',
    'Top-N (<code>ORDER BY … LIMIT n</code>) is cheap: local top-n per task, small final merge.',
]
FAQ = [
    ('Is SORT BY faster than ORDER BY?', 'For large data, yes, because many reducers sort in parallel, but it answers a different question: you get several individually sorted outputs, not one ordered result. If you need the overall top rows, use ORDER BY with LIMIT; if you need per-key order for a later step, use DISTRIBUTE BY with SORT BY.'),
    ('What is the difference between CLUSTER BY and CLUSTERED BY?', 'CLUSTER BY is a query clause that distributes and sorts rows for that query only. CLUSTERED BY (col) INTO n BUCKETS is part of CREATE TABLE and fixes how a table’s data is split into bucket files permanently (Module 5). The names are similar; the purposes are not.'),
    ('Does the order of rows survive into the next query?', 'No. Tables have no guaranteed row order. Even if you write sorted files, a later SELECT without ORDER BY may read them in parallel and return rows in any order. Sorting files is still useful for compression and data skipping, not for result order.'),
    ('How many reducers will Hive use?', 'By default Hive estimates from the input size (bytes per reducer) up to a maximum, and Tez can adjust it at run time. You can fix it with mapred.reduce.tasks (we used 3 to make the effect visible). ORDER BY still uses one reducer for its final total sort.'),
    ('Can I sort by a column that is not selected?', 'Usually yes for ORDER BY on simple queries, but with SELECT DISTINCT or GROUP BY the sort columns must be among the selected or grouped expressions. For SORT BY and DISTRIBUTE BY, the columns must be available in the rows reaching the reducer. When in doubt, select the column too.'),
]

PRACTICE_INTRO = 'Programs that model reducers, hashing and sorting, with the matching HiveQL in each explanation.'
PROBLEMS = [
    dict(level='easy', title='Global vs per-file order', stmt='Are the files [590, 480], [500, 300], [530] globally sorted when concatenated?', inp='three files',
         code='''files = [[590, 480], [500, 300], [530]]
c = sum(files, [])
print(c, c == sorted(c, reverse=True))
''', explain='False. Each file is sorted (SORT BY), the whole is not.'),
    dict(level='easy', title='Reducer for a key', stmt='With 4 reducers and hash = sum of character codes, which reducer gets Pune, Thane and Delhi?', inp='Pune, Thane, Delhi',
         code='''for c in ["Pune", "Thane", "Delhi"]:
    print(c, sum(c.encode()) % 4)
''', explain='The same city always maps to the same reducer. Hive uses its own hash function, so real assignments differ.'),
    dict(level='easy', title='Top 2', stmt='Top 2 amounts from [40, 590, 300, 530, 180].', inp='[40, 590, 300, 530, 180]',
         code='''print(sorted([40, 590, 300, 530, 180], reverse=True)[:2])
''', explain='[590, 530]. Hive: ORDER BY amount DESC LIMIT 2.'),
    dict(level='medium', title='Collisions', stmt='8 cities, 8 reducers, simple hash. How many reducers are empty and how many hold more than one city?', inp='8 TiffinGo cities',
         code='''cities = ["Mumbai", "Pune", "Thane", "Navi Mumbai", "Bengaluru", "Hyderabad", "Delhi", "Chennai"]
load = [0] * 8
for c in cities:
    load[sum(c.encode()) % 8] += 1
print(load, "| empty:", load.count(0), "| shared:", sum(1 for n in load if n > 1))
''', explain='Hashing rarely gives a perfect one-key-per-reducer spread. Use partitions when you need one folder per key.'),
    dict(level='medium', title='NULL placement', stmt='Sort [5005, None, 0, 30011] descending with NULLs first (Hive default for DESC) and with NULLs last.', inp='[5005, None, 0, 30011]',
         code='''vals = [5005, None, 0, 30011]
nn = sorted([v for v in vals if v is not None], reverse=True)
print("NULLS FIRST:", [None] * vals.count(None) + nn)
print("NULLS LAST :", nn + [None] * vals.count(None))
''', explain='Matches the payment_mix results: Crypto (NULL) first by default in DESC, last with NULLS LAST.'),
    dict(level='medium', title='Merge sorted files', stmt='Merge the three sorted reducer files into one descending list.', inp='[590,480,460] [500,410,300] [530]',
         code='''import heapq
print(list(heapq.merge([590, 480, 460], [500, 410, 300], [530], reverse=True)))
''', explain='[590, 530, 500, 480, 460, 410, 300]. A merge of sorted runs is how a final sort combines partial results.'),
    dict(level='business', title='Hours lost to a global sort', stmt='A single reducer sorts 120 GB at 40 MB/s. 300 parallel reducers would each sort 0.4 GB at the same speed. Compare times.', inp='120 GB, 40 MB/s, 300 reducers',
         code='''gb, mbps, r = 120, 40, 300
single = gb * 1024 / mbps / 3600
parallel = gb / r * 1024 / mbps / 60
print(f"one reducer: {single:.1f} h | 300 reducers: {parallel:.1f} min each")
''', explain='About 0.9 hours on one reducer versus about 10 seconds each in parallel. Only pay for a total order when someone needs it. (Speeds illustrative.)'),
    dict(level='business', title='Strict mode savings', stmt='A shared cluster saw 12 accidental unlimited ORDER BY queries a month, each holding a reducer for 3 hours at Rs 60 per hour. What does strict mode save per year?', inp='12/month × 3 h × Rs 60',
         code='''print("Rs", 12 * 3 * 60 * 12, "per year")
''', explain='Rs 25,920 a year in reducer time, plus fewer blocked jobs for other teams.'),
]

SCN_INTRO = 'The four ordering clauses are a classic Hive interview topic. Good answers use evidence like reducer output files.'
SCENARIOS = (
    scn('Any company · concepts', 'Fresher', '“ORDER BY vs SORT BY?”',
        'The interviewer asks for the difference and when you would use each.',
        'do you know the reducer-level behaviour?',
        '''<ul>
          <li>ORDER BY gives a total order using a single final reducer; fine with LIMIT or small results.</li>
          <li>SORT BY sorts within each reducer; with several reducers the overall output is only partially ordered.</li>
          <li>Use SORT BY with DISTRIBUTE BY when downstream processing works per key.</li>
        </ul>''', '“SORT BY is just a faster ORDER BY”.') +
    scn('Operations · performance', 'Mid-level', 'A job stuck at 99%',
        'An export with ORDER BY event_time over 2 billion rows stays at 99% for hours.',
        'can you diagnose a single-reducer bottleneck?',
        '''<ol>
          <li>ORDER BY funnels everything to one reducer for the final sort.</li>
          <li>Ask whether a total order is needed; usually LIMIT, per-key sorting or none is enough.</li>
          <li>Enable <code>hive.strict.checks.orderby.no.limit</code> on shared clusters.</li>
        </ol>''', 'adding more reducers: ORDER BY still uses one for the final sort.') +
    scn('Data engineering · design', 'Mid-level', 'Per-customer processing',
        'A Python TRANSFORM script must see each customer’s events together and in time order.',
        'do you know DISTRIBUTE BY + SORT BY?',
        '''<pre>SELECT TRANSFORM (customer_id, event_ts, event)
USING 'python3 sessions.py' AS (customer_id, session_id, events)
FROM (SELECT customer_id, event_ts, event FROM events
      DISTRIBUTE BY customer_id
      SORT BY customer_id, event_ts) t;</pre>''', 'CLUSTER BY customer_id alone: events would not be in time order.') +
    scn('Data platform · terms', 'Fresher', 'CLUSTER BY vs CLUSTERED BY',
        'A candidate mixes up CLUSTER BY in a query and CLUSTERED BY in CREATE TABLE.',
        'do you separate query-time and storage-time concepts?',
        '''<ul>
          <li>CLUSTER BY: query clause = DISTRIBUTE BY + SORT BY, for that query only.</li>
          <li>CLUSTERED BY … INTO n BUCKETS: table property; data stored in n bucket files by hash of the column (Module 5).</li>
        </ul>''', 'treating them as the same feature.')
)
