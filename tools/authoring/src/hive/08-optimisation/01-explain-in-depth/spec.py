import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from hivekit import tables
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()
def inner(n):
    out = []
    for l in capf(n).split('\n'):
        if l.startswith('+') or 'Explain' in l:
            continue
        out.append(l.strip().strip('|').rstrip())
    return '\n'.join(out).rstrip()
BODY = body(HERE)

_np = inner('l81_noprune.txt')
NOPRUNE = _np[:260] + ' …\n(' + str(len(re.findall('partitionName', _np))) + ' partitionName entries in total)'

META = dict(
    module='08-optimisation', lesson='01-explain-in-depth', n='8.1',
    module_label='Module 8 · Query optimisation',
    title='EXPLAIN in depth: reading Hive query plans',
    desc='How to read Hive 4 query plans with real Hive 4.2.1 outputs: the Tez vertex DAG, operators read bottom-up, BROADCAST and SIMPLE edges, map join, EXPLAIN ANALYZE estimated vs actual rows, EXPLAIN CBO and CBO COST, the classic plan view, EXPLAIN VECTORIZATION, DEPENDENCY for partition pruning, LOCKS, and a checklist for reviewing plans at work.',
    og_desc='Estimated 3 rows, actually 517. Learn to read Hive query plans and spot the problem before the query runs, with real Hive 4.2.1 outputs.',
    minutes=40, level='Intermediate → Advanced',
    lead='Module 8 is about making queries fast, and every tuning job starts with the plan. This lesson takes one real report query and reads it with <b>every kind of EXPLAIN</b>: the Tez DAG, the operator tree, estimated vs actual rows, the cost-based optimiser’s plan, vectorisation, pruning and locks. <b>All outputs are real</b>, from Hive 4.2.1.',
    chips=['Real Hive 4.2.1 plans', 'Estimated vs actual rows', 'Plan review checklist', 'Runs in your browser (Python)'],
)

MAIN = '''# EXPLAIN ANALYZE pairs from the real plan: (operator, estimated rows, actual rows)
plan = [
    ("TableScan orders",     50000, 50000),
    ("Filter order_date",    25000,  1621),
    ("TableScan customers",   1413,  2000),
    ("Filter plan='Gold'",       3,   517),
    ("Map Join",             27500,   427),
    ("Group By (final)",     13750,     8),
]
for op, est, act in plan:
    ratio = max(est, act) / max(1, min(est, act))
    flag = "  <-- check statistics" if ratio >= 10 else ""
    print(f"{op:22} est {est:>6}  actual {act:>6}  x{ratio:>7.1f}{flag}")
'''
RUN = dict(
    heading='Run the code: read a plan like a reviewer',
    intro='<p>These programs work with the real numbers from our plans. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('    ("Filter plan=\'Gold\'",       3,   517),', 'The worst estimate in the plan: 3 rows expected, 517 real. Customers had no column statistics.'),
        ('    flag = "  <-- check statistics" if ratio >= 10 else ""', 'A common rule of thumb: an estimate off by 10× or more is worth investigating.'),
    ],
    tasks=[
        dict(label='1 · Estimate vs actual', hint='Press <b>Run</b>. Four operators are off by 10× or more. Which table do they all depend on?', code=None),
        dict(label='2 · Predict first: read order', hint='<b>Predict first:</b> plans print top-down, but rows flow bottom-up. Reverse the list to get execution order.',
             code='''printed = ["File Output", "Limit", "Select", "Top N Key", "Group By", "Map Join", "Filter", "TableScan"]
print(" -> ".join(reversed(printed)))
'''),
        dict(label='3 · Which side is broadcast?', hint='Hive broadcasts the smaller input to every map task. Change the sizes.',
             code='''sizes = {"orders (after filter)": 25000 * 116, "customers (Gold)": 3 * 346}   # rows x width
small = min(sizes, key=sizes.get)
print("broadcast:", small)
print("stream   :", max(sizes, key=sizes.get))
'''),
        dict(label='4 · Vertex DAG', hint='Edges from the real plan. Print each vertex with what it waits for.',
             code='''edges = [("Map 4", "Map 1", "BROADCAST_EDGE"), ("Map 1", "Reducer 2", "SIMPLE_EDGE"), ("Reducer 2", "Reducer 3", "SIMPLE_EDGE")]
for src, dst, kind in edges:
    print(f"{dst:9} <- {src:6} ({kind})")
'''),
        dict(label='5 · Spot the error', hint='This review script says the plan is fine. Fix the comparison so it flags the Gold filter.', expect='error',
             code='''est, act = 3, 517
ratio = est / act                        # bug: small/large is always <= 1
assert ratio >= 10, f"ratio {ratio:.3f}: use max/min, not est/act"
print("flag the Gold filter")
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: pruning, a bad OR and the JSON plan',
    intro='<p>More EXPLAIN variants on the lab tables. <b>Outputs are real</b>, from Hive 4.2.1.</p>',
    items=[
        dict(title='1 · DEPENDENCY shows partition pruning', cmd="EXPLAIN DEPENDENCY\nSELECT COUNT(*) FROM orders_by_day\nWHERE order_date BETWEEN '2026-10-05' AND '2026-10-06';", file='Beeline',
             output=inner('l81_prune.txt'),
             note='Only 2 of the 30 daily partitions are inputs. Hive even pruned when we wrapped the column in a function, <code>date_format(order_date,\'dd\') IN (\'05\',\'06\')</code>: the pruner evaluates deterministic expressions on partition values.'),
        dict(title='2 · An OR with a normal column switches pruning off', cmd="EXPLAIN DEPENDENCY\nSELECT COUNT(*) FROM orders_by_day\nWHERE order_date = '2026-10-05' OR amount > 900;", file='Beeline',
             output=NOPRUNE,
             note='Any row in any partition could have amount &gt; 900, so all 30 partitions are read. This is a classic finding in plan reviews: rewrite as two queries or a UNION ALL if only one day is really wanted.'),
        dict(title='3 · EXPLAIN FORMATTED: the plan as JSON', cmd="EXPLAIN FORMATTED\nSELECT city, COUNT(*) FROM customers WHERE plan = 'Gold' GROUP BY city;", file='Beeline',
             output=inner('l81_formatted.txt')[:420] + ' …',
             note='One long JSON document (7.9 KB for this small query, shortened here). Tools and plan-diff scripts parse this format; people read the default tree.'),
    ],
)

TRACE = dict(
    heading='Rows flowing through the plan, bottom-up',
    intro='<p>Rows start at the TableScans at the bottom of the plan and move up. Watch the row count change at each operator (actual counts from EXPLAIN ANALYZE).</p>',
    code='''rows = 50000                     # TableScan orders
rows = 1621                      # Filter order_date = 2026-10-05
gold = 517                       # Map 4: Gold customers, broadcast
rows = 427                       # Map Join keeps orders of Gold customers
rows = 8                         # Group By city
rows = 3                         # Limit 3 after ORDER BY rev DESC
print("result rows:", rows)
''',
    notes={2: 'Filter :: Only orders of 5 October survive.', 4: 'Join :: 427 of the 1,621 orders belong to Gold customers.', 6: 'Limit :: The Top N Key operator already kept only the best candidates before the shuffle.'},
)

WORKED_INTRO = 'Three plan-reading tasks you will meet at work.'
EXAMPLES = [
    dict(level='b', tag='Analytics · reading', title='Which vertex does what?',
         problem='<p>From the vertex list of the real plan, write one sentence per vertex for a teammate.</p>',
         inp='Map 1 <- Map 4 (BROADCAST_EDGE) · Reducer 2 <- Map 1 (SIMPLE_EDGE) · Reducer 3 <- Reducer 2 (SIMPLE_EDGE)',
         approach=['Map vertices read tables.', 'BROADCAST_EDGE means the input is copied to every task: a map join.', 'SIMPLE_EDGE is a shuffle to reducers.'],
         code='''roles = {
  "Map 4": "scans customers, keeps Gold, broadcasts them",
  "Map 1": "scans orders of 5 Oct, joins in memory, partial group by",
  "Reducer 2": "final group by city",
  "Reducer 3": "sort by revenue and keep top 3",
}
for v, r in roles.items():
    print(f"{v:9}: {r}")
''', notes={3: 'Map join :: The join happens inside Map 1; no reducer is needed for it.'},
         tryit='Two shuffles (SIMPLE_EDGE) is normal for GROUP BY + ORDER BY. A third would make you ask why.'),
    dict(level='i', tag='Data engineering · statistics', title='Find the bad estimate',
         problem='<p>A query got slower after a data load. EXPLAIN ANALYZE gives estimate/actual pairs. Find the first operator, bottom-up, where the estimate is off by 10× or more.</p>',
         inp='TableScan customers 1413/2000 · Filter Gold 3/517 · Map Join 27500/427',
         approach=['Walk bottom-up.', 'Compute max/min of each pair.', 'The first big gap is where to look: its input table’s statistics.'],
         code='''pairs = [("TableScan customers", 1413, 2000), ("Filter Gold", 3, 517), ("Map Join", 27500, 427)]
for op, e, a in pairs:
    if max(e, a) / max(1, min(e, a)) >= 10:
        print("first bad estimate:", op, f"{e} vs {a}")
        break
''', notes={3: 'Rule :: Errors multiply upward, so fix the lowest one first.'},
         tryit='The plan line said <code>Col:NONE</code> for customers: no column statistics. Lesson 8.2 runs ANALYZE and the estimate becomes 667.'),
    dict(level='a', tag='Platform · CI', title='Plan regression check',
         problem='<p>Before a release, compare the plan of a key query with the stored plan. Flag a lost map join or lost pruning.</p>',
         inp='old and new EXPLAIN text',
         approach=['Store EXPLAIN text in the repo.', 'Check for key markers.', 'Fail the build if a marker disappears.'],
         code='''old = "Map 1 <- Map 4 (BROADCAST_EDGE)  Map Join Operator  input_partitions: 2"
new = "Reducer 2 <- Map 1 (SIMPLE_EDGE), Map 3 (SIMPLE_EDGE)  Merge Join Operator  input_partitions: 30"
for marker in ["BROADCAST_EDGE", "Map Join Operator", "input_partitions: 2"]:
    if marker in old and marker not in new:
        print("REGRESSION: lost", marker)
''', notes={3: 'Markers :: Simple string checks catch most plan regressions without parsing JSON.'},
         tryit='The “new” plan here is illustrative: it shows what a shuffle join and lost pruning look like. Teams run such checks with EXPLAIN in a test environment.'),
]

QUIZ = mix([
    dict(q='Beginner: In which direction do rows flow in a Hive EXPLAIN tree?', options=['Top to bottom', 'Bottom to top: from TableScan up to File Output', 'Left to right', 'Random'], answer=1,
         why='The output operator is printed first; the scans are at the bottom.'),
    dict(q='Beginner: What does “Map 1 &lt;- Map 4 (BROADCAST_EDGE)” mean?', options=['Map 4 waits for Map 1', 'Map 4’s output is copied to every task of Map 1, typically for a map join', 'A shuffle', 'An error'], answer=1,
         why='Our plan broadcast the Gold customers to the orders scan.'),
    dict(q='Beginner: Does plain EXPLAIN run the query?', options=['Yes', 'No, it only compiles and prints the plan', 'Only the first stage', 'Only on Tez'], answer=1,
         why='EXPLAIN ANALYZE is the variant that runs it to collect actual row counts.'),
    dict(q='Intermediate: In EXPLAIN ANALYZE, what does rows=3/517 mean?', options=['3 files, 517 rows', '3 rows estimated, 517 actual', '3 reducers', '3% done'], answer=1,
         why='Estimated before, actual after the run.'),
    dict(q='Intermediate: What does Col:NONE on a TableScan tell you?', options=['No columns are read', 'There are no column statistics for the table', 'The table is empty', 'Columns are encrypted'], answer=1,
         why='Our customers table had no column stats, so the Gold filter estimate was 3.'),
    dict(q='Intermediate: Which EXPLAIN shows which partitions a query reads?', options=['EXPLAIN LOCKS', 'EXPLAIN DEPENDENCY', 'EXPLAIN VECTORIZATION', 'EXPLAIN AST'], answer=1,
         why='input_partitions listed 2 partitions for the BETWEEN query and 30 for the OR query.'),
    dict(q='Advanced: Why did an OR with amount &gt; 900 read all 30 partitions?', options=['A bug', 'Rows matching amount &gt; 900 can be in any partition, so none can be skipped', 'OR is not supported', 'Statistics were missing'], answer=1,
         why='Pruning needs a condition that excludes partitions on its own.'),
    dict(q='Advanced: What does EXPLAIN LOCKS show for an UPDATE on an ACID table?', options=['Nothing', 'The locks it would take: SHARED_READ / SHARED_WRITE on table and partitions', 'Exclusive table lock always', 'Row locks'], answer=1,
         why='Real output: SHARED_WRITE on orders_acid and its 2026-10-01 partition.'),
])

REVISION = [
    '<b>EXPLAIN</b> compiles and prints the plan; it does not run the query. <b>EXPLAIN ANALYZE</b> runs it and prints <code>rows=estimated/actual</code>.',
    '<b>Read bottom-up:</b> TableScan → Filter → Select → Join → Group By → Reduce Sink → … → File Output.',
    '<b>Vertices:</b> Map = reads data, Reducer = after a shuffle. <code>BROADCAST_EDGE</code> = small side copied (map join); <code>SIMPLE_EDGE</code> = shuffle.',
    '<b>TableScan line:</b> <code>Tbl:COMPLETE, Col:NONE</code> tells you which statistics exist. Missing column stats → bad estimates.',
    '<b>EXPLAIN CBO [COST]:</b> the Calcite plan with row counts and cumulative cost, before physical operators.',
    '<b>hive.explain.user=false</b> gives the classic stage view with Statistics lines; <b>VECTORIZATION</b> shows whether each vertex is vectorised and why not.',
    '<b>DEPENDENCY</b> lists input tables and partitions (check pruning); <b>LOCKS</b> lists locks for ACID statements; <b>FORMATTED</b> gives JSON.',
    '<b>Review checklist:</b> partitions read, join type, number of shuffles, estimate gaps ≥10×, vectorisation, Col:NONE.',
]
FAQ = [
    ('Why are there several kinds of EXPLAIN?', 'Each answers a different question. Plain EXPLAIN: what will run. ANALYZE: how good were the estimates. CBO: what did the optimiser decide and why (costs). VECTORIZATION: is the fast path used. DEPENDENCY: which partitions. LOCKS: what will be locked. In practice you use plain EXPLAIN most and ANALYZE when the plan looks right but the query is slow.'),
    ('Is EXPLAIN ANALYZE safe on production?', 'It runs the full query, so it costs the same as running it. For INSERT statements check the docs for your version and test on a copy: the point is to collect actual counts, not to write data. For very long queries, run it on a sample or a smaller partition.'),
    ('Why does the CBO plan show 272,144 join rows while the physical plan shows 27,500?', 'They are estimates from different stages with different inputs (the CBO used its own selectivity for the date filter, 6,750 rows, and its own join formula). Neither was close to the real 427. Use the estimates to find where statistics are missing, not as exact predictions.'),
    ('What is the Top N Key operator?', 'An optimisation for ORDER BY … LIMIT: tasks drop rows that cannot reach the top N before shuffling them. In our plan it appeared before the final shuffle with <code>top n:3</code>.'),
    ('Does Tez UI or the Hive web UI show the same thing?', 'They show the executed DAG with real counters per vertex and task (time, records, spills). EXPLAIN is what Hive planned; the UIs show what happened. Lesson 8.5 uses both to troubleshoot slow queries.'),
]

PRACTICE_INTRO = 'Programs that read and check plans, with the HiveQL in each explanation.'
PROBLEMS = [
    dict(level='easy', title='Count the shuffles', stmt='Count SIMPLE_EDGE entries in a vertex list.', inp='the real vertex list',
         code='''edges = ["Map 1 <- Map 4 (BROADCAST_EDGE)", "Reducer 2 <- Map 1 (SIMPLE_EDGE)", "Reducer 3 <- Reducer 2 (SIMPLE_EDGE)"]
print(sum("SIMPLE_EDGE" in e for e in edges))
''', explain='2 shuffles: one for GROUP BY, one for ORDER BY.'),
    dict(level='easy', title='Estimate error', stmt='Compute how many times the estimate was off.', inp='Filter on order_date: 25,000 estimated, 1,621 actual',
         code='''print(round(25000 / 1621, 1))
''', explain='15.4× too high: the plan assumed half of the rows match one date. Lesson 8.2 shows why.'),
    dict(level='easy', title='Pruned share', stmt='What share of partitions does the BETWEEN query read?', inp='2 of 30',
         code='''print(f"{2/30:.1%}")
''', explain='6.7% of the data, before any file-level skipping.'),
    dict(level='medium', title='Find Col:NONE', stmt='List tables without column statistics from TableScan lines.', inp='two TableScan lines',
         code='''lines = ["tiffingo@customers,c,Tbl:COMPLETE,Col:NONE", "tiffingo@orders,o,Tbl:COMPLETE,Col:COMPLETE"]
print([l.split(",")[0] for l in lines if "Col:NONE" in l])
''', explain="Fix with ANALYZE TABLE customers COMPUTE STATISTICS FOR COLUMNS; (Lesson 8.2)."),
    dict(level='medium', title='Parse ANALYZE pairs', stmt='Extract estimated/actual pairs from plan lines.', inp='rows=e/a text',
         code='''import re
lines = ["Filter Operator [FIL_25] (rows=3/517 width=346)", "Map Join Operator [MAPJOIN_30] (rows=27500/427 width=116)"]
for l in lines:
    e, a = map(int, re.search(r"rows=(\\d+)/(\\d+)", l).groups())
    print(l.split(" [")[0], e, a)
''', explain='The same parsing works on saved EXPLAIN ANALYZE output in a monitoring job.'),
    dict(level='medium', title='Lock summary', stmt='Group the locks from EXPLAIN LOCKS by type.', inp='real lock lines',
         code='''locks = [("orders_acid.order_date=2026-10-01", "SHARED_READ"), ("orders_acid.order_date=2026-10-01", "SHARED_WRITE"), ("orders_acid", "SHARED_WRITE")]
from collections import Counter
print(Counter(t for _, t in locks))
''', explain='No EXCLUSIVE lock: other readers and writers can continue, which is how Hive ACID allows concurrency.'),
    dict(level='business', title='Cost of lost pruning', stmt='A daily report reads one day of a table. If an OR breaks pruning, how much more data is read?', inp='30 days kept, each 2 GB (illustrative)',
         code='''day_gb, days = 2, 30
print("with pruning:", day_gb, "GB · without:", day_gb * days, "GB ·", days, "times more")
''', explain='30× more data for the same answer. This is why plan reviews check input_partitions first.'),
    dict(level='business', title='Review checklist score', stmt='Score a plan against the review checklist.', inp='plan facts',
         code='''facts = {"pruned": True, "map join for small dim": True, "estimates within 10x": False, "vectorized": True}
for k, ok in facts.items():
    print(("OK   " if ok else "FIX  ") + k)
''', explain='One item to fix: run ANALYZE on customers before the query goes to production.'),
]

SCN_INTRO = 'Plan reading is asked at every level; seniors are expected to explain estimates and costs.'
SCENARIOS = (
    scn('Any company · Hive', 'Fresher', '“How do you see how Hive will run a query?”',
        'Explain EXPLAIN and what you look for.',
        'do you know EXPLAIN and the basic parts of a plan?',
        '<p>Prefix the query with EXPLAIN. It shows the stages and, on Tez, the vertices (Map and Reducer) and their edges, and inside each vertex the operators: TableScan, Filter, Join, Group By, Reduce Sink and so on, read bottom-up. I check which tables and partitions are read, the join type and the number of shuffles.</p>', 'Saying EXPLAIN runs the query.') +
    scn('Data engineering', 'Mid-level', 'Same query, different speed',
        'A join query took 2 minutes last month and 20 minutes now. Nothing changed in the SQL.',
        'can you use plans to find a regression?',
        '''<ol>
          <li>Compare EXPLAIN now with the old plan (saved or from logs): look for a map join turned into a shuffle join, or more partitions read.</li>
          <li>Run EXPLAIN ANALYZE and find the first estimate off by 10× or more.</li>
          <li>Check statistics of that table (Col:NONE, stale numRows) and refresh them with ANALYZE.</li>
        </ol>''', 'Increasing memory and reducers without looking at the plan.') +
    scn('Analytics', 'Mid-level', 'Report reads the whole table',
        'A daily report filters one date but scans every partition.',
        'do you know how to prove and fix lost pruning?',
        '''<ul>
          <li>Prove it with EXPLAIN DEPENDENCY: input_partitions lists all of them.</li>
          <li>Look for an OR with a normal column or a non-deterministic function on the partition column.</li>
          <li>Rewrite so the partition condition stands alone (AND, or UNION ALL of two queries).</li>
        </ul>''', '“Add more partitions.”') +
    scn('Platform', 'Senior', 'Plan reviews as a team practice',
        'Set up a lightweight plan review for the 20 most expensive queries.',
        'can you turn plan reading into a process?',
        '''<ul>
          <li>Store EXPLAIN (FORMATTED for tooling) of each query in the repo; diff it in CI against a test environment with production-like statistics.</li>
          <li>Checklist: partitions read, join strategy, shuffles, Col:NONE, vectorisation, estimate gaps from a weekly EXPLAIN ANALYZE sample.</li>
          <li>Keep statistics fresh as part of the load jobs, so plans stay stable.</li>
        </ul>''', 'Reviewing only when users complain.')
)
