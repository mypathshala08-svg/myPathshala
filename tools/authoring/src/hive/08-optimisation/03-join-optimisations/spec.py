import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from hivekit import tables
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()
def plain(n):
    lines = [l for l in capf(n).split('\n') if l.startswith('| ')]
    return '\n'.join(re.sub(r'\s*\|$', '', l[2:]).rstrip() for l in lines)
BODY = body(HERE)

META = dict(
    module='08-optimisation', lesson='03-join-optimisations', n='8.3',
    module_label='Module 8 · Query optimisation',
    title='Join optimisations: map join, bucket map join, SMB and skew join',
    desc='Hive join algorithms with real Hive 4.2.1 plans and Tez counters: shuffle (merge) join vs map join (342,929 vs 31,867 shuffled bytes), the map-join size threshold, ignored MAPJOIN hints, why bucketed external tables never got a bucket join, a real bucket map join (CUSTOM_EDGE, BucketMapJoin:true) on managed tables, an SMB join with insert-only sorted tables, the ACID “cannot be sorted” error, and skewed keys: what skew-join settings did on Tez and the hot-key split that worked.',
    og_desc='Shuffle join moved 10.8× more data than a map join. Bucket map join and SMB join finally appeared once we used the right table type. Real Hive 4.2.1 plans.',
    minutes=45, level='Intermediate → Advanced',
    lead='Joins are where most Hive time goes. This lesson runs one join four ways (shuffle, map, bucket map and SMB) and measures what moves, then builds a skewed table with one customer holding 40% of the orders. Along the way it finds the conditions most tutorials leave out: table type, sorting and ACID. <b>All plans and counters are real</b>, from Hive 4.2.1.',
    chips=['Real plans and counters', 'Bucket map join and SMB that work', 'Skew: what worked on Tez', 'Runs in your browser (Python)'],
)

MAIN = '''# Shuffle join vs map join: which rows move? (sizes from the lab)
orders, customers = 50000, 2000
row_bytes = {"orders": 116, "customers": 95}      # width from EXPLAIN

shuffle_join = orders * row_bytes["orders"] + customers * row_bytes["customers"]
tasks = 1                                         # map tasks reading orders
map_join = customers * row_bytes["customers"] * tasks

print("shuffle join moves about", shuffle_join, "bytes (both tables)")
print("map join moves about    ", map_join, "bytes (small side, per task)")
print("real SHUFFLE_BYTES: 342,929 vs 31,867")
'''
RUN = dict(
    heading='Run the code: model the join methods',
    intro='<p>These programs model what each join moves and how buckets and skew behave, using the lab numbers. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('shuffle_join = orders * row_bytes["orders"] + customers * row_bytes["customers"]', 'Every row of both sides crosses the network (estimated widths; real bytes are compressed and serialized differently).'),
        ('map_join = customers * row_bytes["customers"] * tasks', 'The small side is copied once per task. With 500 tasks the copies add up: map joins are for genuinely small sides.'),
    ],
    tasks=[
        dict(label='1 · Bytes moved', hint='Press <b>Run</b>. The model counts raw row bytes; real shuffle data is serialized and compressed, so the counters are smaller and the ratio differs (10.8× in reality), but the direction is the same.', code=None),
        dict(label='2 · Predict first: many tasks', hint='<b>Predict first:</b> with 400 map tasks, does broadcasting 2,000 customers still beat shuffling 50,000 orders? Change <code>tasks</code>.',
             code='''orders_bytes = 50000 * 116
for tasks in [1, 10, 100, 400]:
    broadcast = 2000 * 95 * tasks
    print(tasks, "tasks: broadcast", broadcast, "vs shuffle", orders_bytes, "->", "map join" if broadcast < orders_bytes else "shuffle")
'''),
        dict(label='3 · Which bucket?', hint='Rows go to bucket hash(key) mod 8. A bucket map join only pairs bucket i with bucket i. (Python’s hash of small ints is the int itself; Hive uses its own hash.)',
             code='''buckets = 8
for cid in [7, 15, 1044, 1492]:
    print("customer", cid, "-> bucket", cid % buckets)
'''),
        dict(label='4 · Skewed reducers', hint='Hash-partition the real skewed counts over 4 reducers and see the imbalance.',
             code='''rows = {7: 20016}
rows.update({cid: 15 for cid in range(1, 2001) if cid != 7})   # ~30,000 other rows spread evenly
reducers = [0] * 4
for cid, n in rows.items():
    reducers[cid % 4] += n
print(reducers)
'''),
        dict(label='5 · Spot the error', hint='This query plan check says “bucket map join” for any bucketed table. Fix it with what the lab showed.', expect='error',
             code='''table = {"bucketed": True, "external": True}
bucket_join_possible = table["bucketed"]          # bug
assert not (bucket_join_possible and table["external"]), "external bucketed tables got no bucket join in Hive 4.2.1"
print("ok")
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: the hot-key split, the default plan and skew metadata',
    intro='<p>The skew fixes from Step 8. <b>Outputs are real</b>, from Hive 4.2.1.</p>',
    items=[
        dict(title='1 · Split the hot key into its own join', cmd="SET hive.auto.convert.join=false;\nSELECT city, SUM(n) AS n, SUM(rev) AS rev FROM (\n  SELECT c.city, COUNT(*) AS n, SUM(o.amount) AS rev FROM orders_skew o JOIN customers c\n    ON o.customer_id = c.customer_id WHERE o.customer_id <> 7 GROUP BY c.city\n  UNION ALL\n  SELECT c.city, COUNT(*) AS n, SUM(o.amount) AS rev FROM orders_skew o JOIN customers c\n    ON o.customer_id = c.customer_id WHERE o.customer_id = 7 AND c.customer_id = 7 GROUP BY c.city\n) u GROUP BY city ORDER BY city;", file='Beeline',
             output=capf('l83_skew_split.txt'),
             note='Identical to the plain join, row for row (we compared both outputs). Customer 7 lives in Mumbai: 25,990 orders. The second branch joins 20,016 orders with one customer row, which is trivially a map join; the first branch has no hot key left.'),
        dict(title='2 · The default plan already avoids skew here', cmd='EXPLAIN SELECT c.city, COUNT(*), SUM(o.amount)\nFROM orders_skew o JOIN customers c ON o.customer_id = c.customer_id GROUP BY c.city;', file='Beeline',
             output='\n'.join(l for l in plain('l83_skew_mj.txt').split('\n') if '<-' in l),
             note='Customers is small, so Hive broadcasts it: rows are never shuffled by customer_id, so the hot key does not land on one reducer. Skew hurts shuffle joins between two large tables.'),
        dict(title='3 · Declaring skew in the table metadata', cmd='ALTER TABLE orders_skew SKEWED BY (customer_id) ON (7);\nDESCRIBE FORMATTED orders_skew;   -- skew lines', file='Beeline',
             output='\n'.join(l for l in capf('l83_skewdesc.txt').split('\n') if 'Skewed' in l),
             note='The metadata is stored, but with <code>hive.optimize.skewjoin.compiletime=true</code> (CBO on or off) the Tez plan did not change in our lab. Treat these settings as version-dependent and always check EXPLAIN.'),
    ],
)

TRACE = dict(
    heading='A sort-merge join of two sorted buckets',
    intro='<p>SMB merges bucket i of orders with bucket i of customers, both sorted by customer_id: two pointers, no hash table.</p>',
    code='''orders = [(3, 120), (3, 80), (11, 300), (19, 50)]      # (customer_id, amount), sorted
cust = [(3, "Pune"), (11, "Thane"), (19, "Delhi")]      # sorted
i = j = 0
out = []
while i < len(orders) and j < len(cust):
    if orders[i][0] == cust[j][0]:
        out.append((cust[j][1], orders[i][1])); i += 1
    elif orders[i][0] < cust[j][0]:
        i += 1
    else:
        j += 1
print(out)
''',
    notes={1: 'Bucket 3 :: customer_ids 3, 11, 19 are all 3 mod 8, so they share bucket 3.', 6: 'Match :: Equal keys: emit and move the order pointer.', 11: 'Result :: Only one row of each side is needed at a time: nothing must fit in memory.'},
)

WORKED_INTRO = 'Three join decisions from real platforms.'
EXAMPLES = [
    dict(level='b', tag='Analytics · reading plans', title='Name the join from the plan',
         problem='<p>Classify four plan fragments by join method.</p>',
         inp='four vertex lines and operator names from this lesson',
         approach=['BROADCAST_EDGE → map join.', 'CUSTOM_EDGE + BucketMapJoin:true → bucket map join.', 'Merge Join + Dummy Store in a Map → SMB; Merge Join in a Reducer with two SIMPLE_EDGEs → shuffle join.'],
         code='''plans = {
  "Map 1 <- Map 3 (BROADCAST_EDGE)": "map join",
  "Map 1 <- Map 3 (CUSTOM_EDGE) BucketMapJoin:true": "bucket map join",
  "Map 1: Merge Join Operator <-Dummy Store": "SMB join",
  "Reducer 2 <- Map 1 (SIMPLE_EDGE), Map 4 (SIMPLE_EDGE)": "shuffle join",
}
for p, kind in plans.items():
    print(f"{kind:16} <- {p}")
''', notes={3: 'SMB :: The join operator sits in the map vertex, not in a reducer.'},
         tryit='All four fragments are from this lesson’s real plans.'),
    dict(level='i', tag='Data engineering · skew', title='Find and isolate hot keys',
         problem='<p>List keys holding more than 5% of rows, so they can be joined separately.</p>',
         inp='top keys from GROUP BY customer_id: 7 → 20,016; 1044 → 31; 1492 → 28 (of 50,000)',
         approach=['Count rows per key.', 'Compare with a share threshold.', 'Generate the WHERE clauses for the split.'],
         code='''counts = {7: 20016, 1044: 31, 1492: 28}
total = 50000
hot = [k for k, n in counts.items() if n / total > 0.05]
print("hot keys:", hot)
print("WHERE o.customer_id NOT IN", tuple(hot) if len(hot) > 1 else f"({hot[0]})")
''', notes={3: 'Threshold :: 5% is a team choice; one key with 40% is unmistakable.'},
         tryit='The real split query in “Run on your PC” returned exactly the same result as the plain join.'),
    dict(level='a', tag='Architecture · layout', title='Pick bucket counts for SMB',
         problem='<p>orders (2 TB) and payments (600 GB) are joined hourly on order_id. Choose bucket counts so each bucket is about 1 GB and SMB is possible.</p>',
         inp='illustrative sizes; SMB needs the same number of buckets (Hive also accepts multiples for bucket map join)',
         approach=['Size the larger table.', 'Round to a power of two.', 'Use the same count for both.'],
         code='''import math
orders_gb, payments_gb, target_gb = 2000, 600, 1
n = 2 ** math.ceil(math.log2(orders_gb / target_gb))
print("buckets for both:", n)
print("payments bucket size:", round(payments_gb / n, 2), "GB")
''', notes={3: 'Power of two :: Keeps hash distribution and future re-bucketing simple.'},
         tryit='2048 buckets each. In our lab SMB also required managed (insert-only) tables, sorted on the key; check EXPLAIN on your version before migrating data.'),
]

QUIZ = mix([
    dict(q='Beginner: What does a map join avoid?', options=['Reading the big table', 'Shuffling rows by the join key', 'Using memory', 'Statistics'], answer=1,
         why='The small side is broadcast; the big side is joined where it is read.'),
    dict(q='Beginner: Which plan edge shows a map join?', options=['SIMPLE_EDGE', 'BROADCAST_EDGE', 'CUSTOM_SIMPLE_EDGE', 'ONE_TO_ONE_EDGE'], answer=1,
         why='Map 1 &lt;- Map 3 (BROADCAST_EDGE).'),
    dict(q='Beginner: Which setting is the size limit for automatic map joins?', options=['hive.mapjoin.size', 'hive.auto.convert.join.noconditionaltask.size', 'hive.exec.reducers.bytes.per.reducer', 'hive.tez.container.size'], answer=1,
         why='10,000,000 bytes in our lab.'),
    dict(q='Intermediate: How many bytes did the shuffle join move compared with the map join?', options=['About the same', '342,929 vs 31,867 (10.8×)', '2× more', 'Less'], answer=1,
         why='Real SHUFFLE_BYTES counters.'),
    dict(q='Intermediate: What does BucketMapJoin:true with a CUSTOM_EDGE mean?', options=['A shuffle join', 'Each task receives only the matching bucket of the small table', 'An SMB join', 'A hint was used'], answer=1,
         why='8 map tasks, one per bucket.'),
    dict(q='Intermediate: What happened to /*+ MAPJOIN(o) */?', options=['orders was broadcast', 'It was ignored (hive.ignore.mapjoin.hint=true)', 'Error', 'Shuffle join'], answer=1,
         why='Customers was still broadcast.'),
    dict(q='Advanced: Why did our SMB join use insert-only tables?', options=['Faster inserts', 'Full ACID tables cannot be SORTED BY', 'External tables are required', 'SMB needs Parquet'], answer=1,
         why='“cannot support full ACID functionality since it is sorted”.'),
    dict(q='Advanced: With skew-join settings on, what changed in the Tez plan?', options=['A skew join stage was added', 'Nothing in our lab; the hot-key split fixed it', 'The join became SMB', 'Error'], answer=1,
         why='Check EXPLAIN; a map join or a manual split handled the skew.'),
])

REVISION = [
    '<b>Shuffle join:</b> SIMPLE_EDGE from both sides into a reducer, <code>Merge Join Operator</code>. Always works; moves most data.',
    '<b>Map join:</b> small side under <code>hive.auto.convert.join.noconditionaltask.size</code> (10 MB in lab) → BROADCAST_EDGE. Lab: 31,867 vs 342,929 bytes.',
    '<b>Bucket map join:</b> both bucketed on the key → CUSTOM_EDGE, MULTICAST, <code>BucketMapJoin:true</code>, one task per bucket.',
    '<b>SMB:</b> bucketed + sorted, same count → Merge Join in the Map vertex with Dummy Store; no join shuffle.',
    'Lab conditions: external bucketed tables got no bucket join; full ACID cannot be sorted; insert-only sorted tables gave SMB.',
    'Hints (<code>MAPJOIN</code>, <code>STREAMTABLE</code>) are ignored by default (<code>hive.ignore.mapjoin.hint=true</code>).',
    '<b>Skew:</b> find hot keys with GROUP BY … ORDER BY COUNT(*) DESC; map join or split/salt the hot key. Skew settings did not change the Tez plan in 4.2.1.',
    'Never disable auto map joins globally; fix statistics (8.2) or adjust the threshold per query.',
]
FAQ = [
    ('Is a map join always faster?', 'Only when the small side is genuinely small. Every task builds the hash table, so a large “small side” costs memory and broadcast time, and if it does not fit, tasks fail or spill. That is why the threshold exists and why stale statistics (Lesson 8.2) are dangerous.'),
    ('What is the difference between a bucket map join and an SMB join?', 'A bucket map join still builds a hash table, but of one bucket of the small table per task. An SMB join needs both tables sorted as well, and merges the buckets without any hash table, so neither side has to fit in memory. SMB is the choice for two large tables.'),
    ('Why did Hive not use bucket joins for our external tables?', 'Hive can only rely on bucketing if every file follows the bucketing scheme. Files of external tables may be written by other tools. In Hive 4.2.1 our external bucketed tables never got a bucket map or SMB join, while managed transactional tables did. Behaviour can differ between versions, so verify with EXPLAIN.'),
    ('How do I join on more than one key or a non-equal condition?', 'Map, bucket and SMB joins work for equi-joins on the bucketing keys. Non-equi conditions (BETWEEN, &lt;) can be added after the join or, in Hive 4, used in the ON clause, but they generally lead to shuffle or cross-product style plans; check EXPLAIN and keep such joins on small inputs.'),
    ('What is salting?', 'Adding a random number (0…N-1) to the hot key on the big side and replicating the matching rows of the other side N times, so the hot key is spread over N tasks. It needs no special Hive feature and works in every engine.'),
]

PRACTICE_INTRO = 'Programs about join methods, buckets and skew, with the HiveQL in each explanation.'
PROBLEMS = [
    dict(level='easy', title='Shuffle reduction', stmt='How many times fewer bytes did the map join shuffle?', inp='342,929 and 31,867',
         code='''print(round(342929 / 31867, 1))
''', explain='10.8×. Measured with SET hive.tez.exec.print.summary=true.'),
    dict(level='easy', title='Fits the threshold?', stmt='Would 2,000 rows of width 95 be broadcast with the default threshold?', inp='threshold 10,000,000 bytes',
         code='''print(2000 * 95 <= 10_000_000)
''', explain='True: about 190 KB. That is why the default plan broadcast customers.'),
    dict(level='easy', title='Hot-key share', stmt='What share of orders_skew belongs to customer 7?', inp='20,016 of 50,000',
         code='''print(f"{20016 / 50000:.0%}")
''', explain='40%: in a shuffle join, one task gets at least 40% of the rows.'),
    dict(level='medium', title='Bucket pairing', stmt='For each bucket of orders (8 buckets), which bucket of customers does a bucket map join load?', inp='8 and 8 buckets',
         code='''for b in range(8):
    print(f"orders bucket {b} -> customers bucket {b}")
''', explain='With 8 and 4 buckets, bucket b of the big table would use bucket b mod 4 of the small one; SMB needs equal counts.'),
    dict(level='medium', title='Salting plan', stmt='Spread hot key 7 over 4 salts: list the big-side keys and the replicated small-side rows.', inp='key 7, 4 salts',
         code='''salts = 4
print("orders keys   :", [f"7_{s}" for s in range(salts)])
print("customer rows :", [f"7_{s}" for s in range(salts)], "(one row copied 4 times)")
''', explain="In SQL: CONCAT(customer_id, '_', CAST(FLOOR(RAND()*4) AS INT)) on orders, and a LATERAL VIEW explode over 0..3 on customers."),
    dict(level='medium', title='Join method from facts', stmt='Choose a join method from table facts.', inp='size of small side, bucketing, sorting',
         code='''def choose(small_bytes, both_bucketed, both_sorted, threshold=10_000_000):
    if small_bytes <= threshold: return "map join"
    if both_bucketed and both_sorted: return "SMB join"
    if both_bucketed: return "bucket map join (if one bucket fits)"
    return "shuffle join"
print(choose(190_000, False, False), "|", choose(5e9, True, True), "|", choose(5e9, False, False))
''', explain='A simplification of Hive’s choice; the real decision also depends on table type and settings, so always confirm in EXPLAIN.'),
    dict(level='business', title='Straggler cost', stmt='199 reducers finish in 2 minutes; the one with the hot key takes 60. What does fixing skew save per run?', inp='illustrative',
         code='''before, after = 60, 2
print("saved per run:", before - after, "minutes")
''', explain='58 minutes per run: job time is the time of the slowest task.'),
    dict(level='business', title='Broadcast traffic', stmt='A 50 MB dimension broadcast to 400 tasks: how much data moves, compared with shuffling a 10 GB fact table?', inp='illustrative',
         code='''broadcast_gb = 50 * 400 / 1000
print("broadcast:", broadcast_gb, "GB vs shuffle: 10 GB")
''', explain='20 GB of broadcast copies: more than the shuffle. Sizes and task counts matter, which is why Hive caps map joins by size.'),
]

SCN_INTRO = 'Join optimisation is the most asked Hive performance topic in interviews.'
SCENARIOS = (
    scn('Any company · Hive', 'Fresher', '“What is a map join?”',
        'Explain the map join and when Hive uses it.',
        'do you know why it is fast and its limit?',
        '<p>In a map join the small table is loaded into a hash table on every task that reads the big table, so the join happens in the map phase without shuffling the big table. Hive converts joins automatically when the small side is under <code>hive.auto.convert.join.noconditionaltask.size</code>. In EXPLAIN it appears as BROADCAST_EDGE and Map Join Operator.</p>', 'Saying it is for any join.') +
    scn('Data engineering', 'Mid-level', 'Bucketed but no bucket join',
        'You bucketed two tables on customer_id, but EXPLAIN still shows a broadcast or shuffle join.',
        'do you know the real conditions?',
        '''<ol>
          <li>Check both tables are bucketed on the join key with compatible counts (and sorted, for SMB).</li>
          <li>Check the table type: in our Hive 4.2.1 lab external bucketed tables never got bucket joins; managed transactional ones did.</li>
          <li>Check the size: if the small side fits, a plain map join may be chosen instead (often fine).</li>
        </ol>''', '“Add more buckets.”') +
    scn('Analytics', 'Mid-level', 'One reducer never ends',
        'A join job is stuck at 99% for an hour with one running task.',
        'can you diagnose and fix skew?',
        '''<ul>
          <li>Find hot keys: GROUP BY key ORDER BY COUNT(*) DESC LIMIT 10 on the big side.</li>
          <li>If the other side is small, make sure a map join is used.</li>
          <li>Otherwise join the hot keys separately (UNION ALL) or salt them; verify results match.</li>
        </ul>''', 'Raising the reducer count, which does not split one key.') +
    scn('Platform', 'Senior', 'Two 2 TB tables joined hourly',
        'Design storage so the hourly join avoids a full shuffle.',
        'can you design for SMB?',
        '''<ul>
          <li>Bucket and sort both tables on the join key with the same number of buckets (sized ~1 GB per bucket).</li>
          <li>Use a table type Hive trusts for bucketing (managed; insert-only if sorted), write only through Hive.</li>
          <li>Verify the SMB plan in CI, and keep statistics fresh.</li>
        </ul>''', 'Relying on map joins for two large tables.')
)
