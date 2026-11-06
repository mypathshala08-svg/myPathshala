import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
BODY = body(HERE)

META = dict(
    module='01-introduction', lesson='04-how-a-hive-query-becomes-a-job', n='1.4',
    module_label='Module 1 · Start here: why Hive?',
    title='How a Hive query becomes a job',
    desc='How Hive turns HiveQL into distributed tasks: parse, semantic analysis, logical plan, optimisation (predicate pushdown, column pruning, partial aggregation, join strategies), physical plan as a Tez DAG, execution in YARN containers, and how to read EXPLAIN. With animations, runnable Python and interview scenarios.',
    og_desc='Five lines of SQL become 21 tasks. Follow the five phases and learn to read EXPLAIN before you run.',
    minutes=34, level='Beginner → Advanced',
    lead='Between pressing Enter and the first container starting, a small factory inside HiveServer2 parses your SQL, checks it, rewrites it to do less work, cuts it into stages at every shuffle and hands the stages to YARN. This lesson walks through each phase with a real example, compares MapReduce and Tez, and teaches you to read <code>EXPLAIN</code> before spending cluster time.',
    chips=['5 phases', '4 animations', 'EXPLAIN reading guide', 'Runs in your browser (Python)'],
)

DATA = '''orders = [(1, "Pune", 220), (2, "Thane", 150), (3, "Pune", 180), (4, "Mumbai", 310),
          (5, "Thane", 90), (6, "Pune", 60), (7, "Mumbai", 140), (8, "Pune", 100)]
blocks = [orders[0:3], orders[3:6], orders[6:8]]        # three HDFS blocks
'''
MAIN = '''# SELECT city, SUM(amount) AS total FROM orders WHERE amount > 100 GROUP BY city ORDER BY total DESC
''' + DATA + '''
def map_task(block):                       # Map 1: scan, filter, partial group by
    partial = {}
    for _id, city, amount in block:
        if amount > 100:
            partial[city] = partial.get(city, 0) + amount
    return partial

partials = [map_task(b) for b in blocks]
print("Map 1 outputs      :", partials)

merged = {}                                # Reducer 2: merge partial sums
for p in partials:
    for city, v in p.items():
        merged[city] = merged.get(city, 0) + v
print("Reducer 2 merged   :", merged)

result = sorted(merged.items(), key=lambda kv: -kv[1])   # Reducer 3: total order
print("Reducer 3 (sorted) :", result)
'''
RUN = dict(
    heading='Run a query plan by hand: Map 1, Reducer 2, Reducer 3',
    intro='<p>This program executes the plan from the lesson on the 8 sample orders split into three blocks: a map task per block (scan, filter, partial aggregation), a reducer that merges the partial sums, and a final reducer that sorts. Then try the challenges: count the shuffled rows, make <code>AVG</code> correct, take the top 2, and see a classic mistake.</p>',
    code=MAIN,
    anno=[
        ('if amount > 100:', 'The filter runs <b>inside the map task</b>, right at the scan (predicate pushdown). Rows that fail it are never shuffled.'),
        ('partial[city] = partial.get(city, 0) + amount', 'Partial aggregation: each map task sums its own rows (<code>mode: hash</code> in EXPLAIN).'),
        ('sorted(merged.items(), key=lambda kv: -kv[1])', 'ORDER BY needs all results together, so it happens in a final single-reducer stage.'),
    ],
    tasks=[
        dict(label='1 · Run the plan', hint='Press <b>Run</b>. Then change the filter to <code>amount &gt; 0</code> and see how the totals change.', code=None),
        dict(label='2 · Rows shuffled', hint='<b>Predict first:</b> how many rows cross the shuffle with and without partial aggregation? (Only rows that pass the filter count.)',
             code=DATA + '''
passing = [r for b in blocks for r in b if r[2] > 100]
without = len(passing)
with_partial = sum(len({r[1] for r in b if r[2] > 100}) for b in blocks)
print("rows shuffled without partial aggregation:", without)
print("rows shuffled with partial aggregation   :", with_partial)
'''),
        dict(label='3 · AVG the cluster way', hint='A map task cannot send its local average: the reducer needs <b>sum and count</b> from each block. Predict the average amount for Pune, then run.',
             code=DATA + '''
partials = []
for b in blocks:
    d = {}
    for _id, city, amount in b:
        s, c = d.get(city, (0, 0))
        d[city] = (s + amount, c + 1)
    partials.append(d)
total = {}
for d in partials:
    for city, (s, c) in d.items():
        ts, tc = total.get(city, (0, 0))
        total[city] = (ts + s, tc + c)
for city, (s, c) in sorted(total.items()):
    print(city, "AVG =", s / c)
'''),
        dict(label='4 · ORDER BY … LIMIT 2', hint='Top-N is cheaper than a full sort: each reducer only needs its own top 2. Change the limit to 1 and then 3.',
             code='''totals = {"Mumbai": 450, "Pune": 400, "Thane": 150, "Nashik": 80}
top2 = sorted(totals.items(), key=lambda kv: -kv[1])[:2]
print(top2)
'''),
        dict(label='5 · Spot the error', hint='This combines the block averages by averaging them. It looks plausible but is wrong, and the assertion fails. Fix it by combining sums and counts.', expect='error',
             code='''block_avgs = [(3, 100.0), (2, 400.0)]       # (rows, average) per block
avg_of_avgs = sum(a for _, a in block_avgs) / len(block_avgs)
true_avg = sum(n * a for n, a in block_avgs) / sum(n for n, _ in block_avgs)
print(avg_of_avgs, true_avg)
assert avg_of_avgs == true_avg, "average of averages is not the average"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: read a real plan',
    intro='<p>With Hive on your machine, run <code>EXPLAIN</code> on the query from this lesson, then run it and watch the Tez progress table. <b>The outputs below are typical examples written for this lesson, not a recording of a particular run</b>: your plan text, task counts and times will differ.</p>',
    items=[
        dict(title='1 · Which engine am I using?', cmd='SET hive.execution.engine;', file='Beeline',
             output='+---------------------------+\n|            set           |\n+---------------------------+\n| hive.execution.engine=tez |\n+---------------------------+',
             note='<code>tez</code> is expected in modern Hive. <code>mr</code> means a legacy MapReduce setup.'),
        dict(title='2 · Explain the query before running it', cmd='EXPLAIN\nSELECT city, SUM(amount) AS total\nFROM orders WHERE amount > 100\nGROUP BY city ORDER BY total DESC;', file='Beeline',
             output='STAGE PLANS:\n  Stage: Stage-1\n    Tez\n      Edges:\n        Reducer 2 <- Map 1 (SIMPLE_EDGE)\n        Reducer 3 <- Reducer 2 (SIMPLE_EDGE)\n      Vertices:\n        Map 1\n            TableScan  alias: orders\n              Filter Operator  predicate: (amount > 100)\n                Group By Operator  aggregations: sum(amount)  keys: city  mode: hash\n                  Reduce Output Operator\n        Reducer 2\n            Group By Operator  aggregations: sum(VALUE._col0)  keys: KEY._col0  mode: mergepartial\n        Reducer 3\n            Select Operator -> File Output Operator\n... (trimmed)',
             note='Find the three vertices, the two <code>SIMPLE_EDGE</code> shuffles, the early <code>Filter Operator</code> and <code>mode: hash</code> (partial aggregation). The layout is simplified here; your Hive version prints more detail.'),
        dict(title='3 · Run it and watch the vertices', cmd='SELECT city, SUM(amount) AS total FROM orders WHERE amount > 100 GROUP BY city ORDER BY total DESC;', file='Beeline',
             output='----------------------------------------------------------------------------------------------\n        VERTICES      MODE        STATUS  TOTAL  COMPLETED  RUNNING  PENDING  FAILED  KILLED\n----------------------------------------------------------------------------------------------\nMap 1 .......... container     SUCCEEDED     16         16        0        0       0       0\nReducer 2 ...... container     SUCCEEDED      4          4        0        0       0       0\nReducer 3 ...... container     SUCCEEDED      1          1        0        0       0       0\n----------------------------------------------------------------------------------------------\nVERTICES: 03/03  [==========================>>] 100%  ELAPSED TIME: 19.31 s',
             note='Each row is a vertex; the TOTAL column is the number of tasks. 16 + 4 + 1 = 21 tasks for this example.'),
    ],
)

TRACE = dict(
    heading='A two-stage plan, one line at a time',
    intro='<p>Watch the map stage build partial sums for each block and the reduce stage merge them. The variables <code>partials</code> and <code>merged</code> show exactly what travels between the stages.</p>',
    code='''blocks = [[("Pune", 220), ("Thane", 150)], [("Pune", 180), ("Mumbai", 310)]]
partials = []
for block in blocks:
    d = {}
    for city, amt in block:
        d[city] = d.get(city, 0) + amt
    partials.append(d)
merged = {}
for d in partials:
    for city, amt in d.items():
        merged[city] = merged.get(city, 0) + amt
print(merged)
''',
    notes={3: 'Map 1 :: One map task per block: scan the rows and build a partial result.', 9: 'Reducer 2 :: The shuffle has delivered the partial results; merge them by key.'},
)

WORKED_INTRO = 'Three tasks a Hive developer does when a query misbehaves: count the stages of a plan, measure what partial aggregation saves, and decide which join strategy Hive will use. Each runs live and is traced in memory.'
EXAMPLES = [
    dict(level='b', tag='Plan reading · stages', title='How many vertices does this plan have?',
         problem='<p>A plan is a list of operators. A new vertex starts after every <b>ReduceSink</b>. Count the vertices and print the operators of each.</p>',
         inp='TableScan, Filter, GroupBy, ReduceSink, GroupBy, ReduceSink, Select, FileSink',
         approach=['Walk through the operators.', 'Add each to the current vertex.', 'After a ReduceSink, close the vertex and start a new one.'],
         code='''plan = ["TableScan", "Filter", "GroupBy", "ReduceSink", "GroupBy", "ReduceSink", "Select", "FileSink"]
vertices, cur = [], []
for op in plan:
    cur.append(op)
    if op == "ReduceSink":
        vertices.append(cur)
        cur = []
vertices.append(cur)
print("vertices:", len(vertices))
for i, v in enumerate(vertices, 1):
    print(i, v)
''', notes={5: 'Boundary :: A shuffle ends the vertex.'},
         tryit='Remove the second ReduceSink (a query without ORDER BY). How many vertices remain? Fewer shuffles mean a cheaper query.'),
    dict(level='i', tag='Optimisation · shuffle volume', title='What does partial aggregation save?',
         problem='<p>A daily table has <b>24,000,000</b> qualifying rows over <b>120</b> map tasks and <b>40</b> cities. Compute how many rows cross the shuffle without and with map-side aggregation, and the reduction factor.</p>',
         inp='24,000,000 rows · 120 map tasks · 40 cities',
         approach=['Without: every row is shuffled.', 'With: each map task sends at most one row per city.', 'Divide to get the reduction.'],
         code='''rows, maps, cities = 24_000_000, 120, 40
without = rows
with_partial = maps * cities
print("without:", without)
print("with   :", with_partial)
print("reduction:", without // with_partial, "times fewer rows")
''', notes={3: 'Compare :: Rows in the shuffle: all rows versus one per city per task.'},
         tryit='Raise the number of cities to 500,000 (customer ids). The saving collapses, because partial aggregation helps only when the key has few distinct values.'),
    dict(level='a', tag='Joins · strategy', title='Shuffle join or map join?',
         problem='<p>Hive converts a join to a map join when the smaller table fits under a threshold (say <b>256 MB</b> here). For three joins decide the strategy and estimate the data shuffled (sum of both table sizes for a shuffle join, 0 for a map join).</p>',
         inp='orders 2,000 GB × cities 0.2 MB · orders 2,000 GB × customers 40,000 MB · orders 2,000 GB × products 120 MB',
         approach=['The small side is the smaller of the two tables.', 'If it is under the threshold use a map join, else a shuffle join.', 'Print strategy and shuffle volume.'],
         code='''threshold_mb = 256
joins = [("cities", 2_000_000, 0.2), ("customers", 2_000_000, 40_000), ("products", 2_000_000, 120)]
for name, big_mb, small_mb in joins:
    if small_mb <= threshold_mb:
        print(f"orders JOIN {name:10}: map join, shuffle 0 MB")
    else:
        print(f"orders JOIN {name:10}: shuffle join, shuffle ~{big_mb + small_mb:,.0f} MB")
''', notes={4: 'Decide :: Small enough to broadcast?'},
         tryit='Raise the threshold to 64,000 MB. The customers join becomes a map join on paper, but every task would need 40 GB of memory. Thresholds protect memory as well as the network.'),
]

QUIZ = mix([
    dict(q='What is the correct order of Hive’s query phases?', options=['Execute → parse → optimise → analyse', 'Parse → semantic analysis → optimise → physical plan → execute', 'Optimise → execute → parse → fetch', 'Analyse → execute → parse → plan'], answer=1,
         why='Text is parsed to a tree, analysed against the metastore, optimised, turned into a physical DAG, then executed.'),
    dict(q='Where does a Tez plan get cut into separate vertices?', options=['At every TableScan', 'At every Reduce Sink (shuffle) operator', 'At every WHERE clause', 'At every column'], answer=1,
         why='Data must be regrouped across machines at a Reduce Sink, so each one ends a vertex.'),
    dict(q='What does “mode: hash” on a Group By Operator in a map vertex mean?', options=['The table is bucketed', 'A partial (map-side) aggregation happens before the shuffle', 'The query uses MD5', 'Reducers are disabled'], answer=1,
         why='Hash-mode group-by builds partial aggregates in each map task; the reducer later merges them (mode: mergepartial).'),
    dict(q='Which statement shows a query’s plan without running it?', options=['SHOW PLAN', 'EXPLAIN', 'DESCRIBE QUERY', 'ANALYZE'], answer=1,
         why='<code>EXPLAIN</code> compiles the query and prints the plan; no containers are used.'),
    dict(q='Why is Tez generally faster than the MapReduce engine for multi-stage queries?', options=['It uses less SQL', 'It runs the plan as one DAG without writing intermediate results to HDFS between stages', 'It skips the metastore', 'It only works on small data'], answer=1,
         why='MapReduce ran one job per stage with HDFS writes between them; Tez streams data between vertices in one job.'),
    dict(q='When does Hive prefer a map (broadcast) join?', options=['When both tables are huge', 'When one table is small enough to copy to every task', 'When there is no WHERE clause', 'Only when tables are partitioned'], answer=1,
         why='A small table can be broadcast, so the big table does not need to be shuffled.'),
    dict(q='Why does ORDER BY on a huge result often become a bottleneck?', options=['It needs a total order, so the final stage often runs on a single reducer', 'It disables Tez', 'It forces MapReduce', 'It rewrites the table'], answer=0,
         why='A global sort needs all rows ordered together; the last vertex may have one task. Use LIMIT or SORT BY when a global order is not needed.'),
])

REVISION = [
    'Phases: <b>parse → semantic analysis (metastore) → optimise → physical plan (DAG) → execute (Tez on YARN)</b>.',
    'A <b>Reduce Sink</b> ends a vertex; vertices are joined by shuffle edges (<code>SIMPLE_EDGE</code>); broadcast edges send small tables.',
    'Optimisations: <b>predicate pushdown</b>, <b>column pruning</b>, <b>partition pruning</b>, <b>partial aggregation</b>, <b>cost-based join choice</b>.',
    'Logical order: FROM → WHERE → GROUP BY → SELECT → ORDER BY → LIMIT.',
    '<b>EXPLAIN</b> (plan), <b>EXPLAIN EXTENDED</b> (paths, partitions), <b>EXPLAIN ANALYZE</b> (actual rows), <b>EXPLAIN DEPENDENCY</b> (inputs).',
    '<b>Tez</b> = one DAG, no HDFS writes between stages; <b>MapReduce</b> = deprecated, a job per stage.',
    '<b>Map join</b> = small table broadcast, no shuffle; <b>shuffle join</b> = both sides repartitioned. Keep <b>statistics</b> fresh: <code>ANALYZE TABLE</code>.',
    'Watch for <b>skew</b> (one slow reducer) and a <b>single-reducer ORDER BY</b>.',
]
FAQ = [
    ('What are the phases of query processing in Hive?', 'Parsing (HiveQL to AST), semantic analysis using the metastore (AST to a logical plan of operators), optimisation (rule-based and cost-based, using Calcite), physical plan generation (a DAG of vertices cut at shuffle boundaries) and execution by an engine such as Tez on YARN, followed by fetching the results through HiveServer2.'),
    ('How do I know how many tasks a query will use?', 'EXPLAIN shows the vertices; the number of map tasks depends on the number of input splits (roughly the data size divided by the split size) and reducer tasks are estimated from the data volume and can be adjusted at run time. The actual counts appear in the Tez progress table and in the Tez UI.'),
    ('What is the difference between EXPLAIN and EXPLAIN ANALYZE?', 'EXPLAIN only compiles and prints the plan with estimates. EXPLAIN ANALYZE actually runs the query and then shows real row counts next to the estimates, so you can find where the optimiser’s statistics were wrong.'),
    ('Why does my simple query take 20 seconds on a tiny table?', 'Fixed overheads dominate: compiling, getting a Tez session and containers from YARN, starting tasks and returning results. They are the same for 1 MB or 1 TB. Interactive-latency features such as LLAP reduce them, and engines like Trino are often used for fast interactive queries.'),
    ('What is a cost-based optimiser and why do I run ANALYZE TABLE?', 'The cost-based optimiser (built with Apache Calcite) compares possible plans using table and column statistics such as row counts and distinct values, to choose join order and join type. Without up-to-date statistics it guesses, which can lead to a slow shuffle join or a map join that runs out of memory. ANALYZE TABLE … COMPUTE STATISTICS refreshes them.'),
]

PRACTICE_INTRO = 'Programs on plans, partial aggregation, join strategy and reducer counts: the arithmetic behind reading EXPLAIN.'
PROBLEMS = [
    dict(level='easy', title='Logical order of clauses', stmt='Print the logical evaluation order of the six SQL clauses.', inp='SELECT FROM WHERE GROUP BY ORDER BY LIMIT',
         code='''for i, c in enumerate(["FROM", "WHERE", "GROUP BY", "SELECT", "ORDER BY", "LIMIT"], 1):
    print(i, c)
''', explain='SELECT is evaluated late even though it is written first. This is why an alias defined in SELECT can be used in ORDER BY but not in WHERE.'),
    dict(level='easy', title='Tasks in total', stmt='A plan has Map 1 with 16 tasks, Reducer 2 with 4 and Reducer 3 with 1. How many tasks in total?', inp='16 + 4 + 1',
         code='print(16 + 4 + 1, "tasks")\n', explain='21 tasks, each running in one YARN container (containers can be re-used across tasks).'),
    dict(level='easy', title='Map tasks for a file', stmt='A table is 50 GB and Hive uses 256 MB splits. How many map tasks (roughly)?', inp='51,200 MB ÷ 256 MB',
         code='''import math
print(math.ceil(51200 / 256), "map tasks")
''', explain='200 splits make about 200 map tasks. Larger splits give fewer, longer tasks; smaller splits give more, shorter ones.'),
    dict(level='medium', title='Reducer estimate', stmt='Hive estimates reducers as input size ÷ 256 MB per reducer, with a maximum of 1,009. For 10 GB, 600 GB and 1 TB of reducer input, print the estimates.', inp='10 GB · 600 GB · 1,024 GB',
         code='''import math
for gb in [10, 600, 1024]:
    est = min(1009, max(1, math.ceil(gb * 1024 / 256)))
    print(gb, "GB ->", est, "reducers")
''', explain='The cap protects the cluster from an enormous number of tiny tasks. The numbers are a model of Hive’s estimate; exact defaults depend on version and settings.'),
    dict(level='medium', title='Average of two blocks, the right way', stmt='Block 1 has 3 rows with average 100; block 2 has 2 rows with average 400. Compute the true overall average and the wrong “average of averages”.', inp='(3, 100) and (2, 400)',
         code='''blocks = [(3, 100.0), (2, 400.0)]
wrong = sum(a for _, a in blocks) / len(blocks)
right = sum(n * a for n, a in blocks) / sum(n for n, _ in blocks)
print("wrong:", wrong, "| right:", right)
''', explain='Right: (300 + 800) ÷ 5 = 220. Averaging the averages gives 250. That is why distributed AVG keeps (sum, count) pairs.'),
    dict(level='medium', title='Filter early or late?', stmt='A table has 10 million rows; 2% pass the filter. How many rows are processed by the group-by if the filter runs first versus last?', inp='10,000,000 rows · 2% pass',
         code='''rows = 10_000_000
print("filter first:", int(rows * 0.02), "rows grouped")
print("filter last :", rows, "rows grouped")
''', explain='200,000 versus 10,000,000. Hive pushes filters down automatically, but a filter written on a computed column or after a join can sometimes defeat it: always check EXPLAIN.'),
    dict(level='business', title='Cloud cost of a scan', stmt='A job reads 2,000 GB at a cost of Rs 0.4 per GB scanned. After partition pruning and column pruning it reads 120 GB. How much does one run cost before and after, and what is saved over 30 nightly runs?', inp='2,000 GB → 120 GB at Rs 0.4/GB',
         code='''before, after, rate = 2000, 120, 0.4
print("before: Rs", before * rate, "| after: Rs", after * rate)
print("saved in 30 runs: Rs", round((before - after) * rate * 30))
''', explain='Rs 800 versus Rs 48 per run; Rs 22,560 saved in a month for one job. Small plan improvements add up across hundreds of jobs.'),
    dict(level='business', title='Skew check', stmt='Reducer run times in minutes are [3, 4, 3, 62, 4]. Compute the median, the maximum and flag skew if the maximum is more than 5 times the median.', inp='[3, 4, 3, 62, 4]',
         code='''times = [3, 4, 3, 62, 4]
med = sorted(times)[len(times) // 2]
print("median", med, "| max", max(times), "| skew:", max(times) > 5 * med)
''', explain='The job takes 62 minutes because of one reducer, though the median is 4. This is the signature of a skewed key.'),
]

SCN_INTRO = 'Questions about query execution show up in every Hive interview. Each of these starts from something you would really see on a cluster.'
SCENARIOS = (
    scn('Any company · concepts', 'Fresher', '“What happens when I run a query in Hive?”',
        'The interviewer says: “Walk me through everything between pressing Enter and getting the result.”',
        'can you describe the phases and the components in order?',
        '''<ol>
          <li>Beeline sends the statement to HiveServer2; the Driver starts the query.</li>
          <li>The compiler parses it, checks tables and columns with the metastore, builds a logical plan and optimises it.</li>
          <li>The physical plan, a DAG of vertices, is submitted to YARN, where Tez runs tasks in containers reading blocks from HDFS.</li>
          <li>Results are written to a temporary location and fetched back through HiveServer2.</li>
        </ol>''', 'jumping straight to “it runs MapReduce”; mention the compile phases and the metastore.') +
    scn('Performance · tuning', 'Mid-level', 'One reducer runs for an hour',
        'A nightly query has 200 reducers. 199 finish in two minutes; one takes an hour.',
        'do you recognise skew and know where to look?',
        '''<ul>
          <li>This is <b>data skew</b>: one key has far more rows than the others, so the reducer that receives it is overloaded.</li>
          <li>Confirm in the Tez UI (task times per vertex) and with a <code>GROUP BY key ORDER BY COUNT(*) DESC</code> query on the join or group key.</li>
          <li>Fix options: filter or handle the hot key separately, salt the key, enable Hive’s skew-join settings, or change the design so the hot key is spread out.</li>
        </ul>''', 'adding more reducers: the single hot key still goes to one reducer.') +
    scn('Performance · tuning', 'Fresher', 'A join that should be fast is slow',
        'A report joins a 2 TB orders table with a 200 KB cities table and takes 40 minutes. EXPLAIN shows a shuffle join (SIMPLE_EDGE on both sides).',
        'do you know map joins and statistics?',
        '''<ol>
          <li>The small table should be broadcast (map join). Hive chooses this when it believes the table is under the threshold, using statistics.</li>
          <li>Run <code>ANALYZE TABLE cities COMPUTE STATISTICS</code> (and for columns) so the optimiser sees the real size, then re-check EXPLAIN for a BROADCAST_EDGE.</li>
          <li>Verify <code>hive.auto.convert.join</code> is on and the threshold is suitable for your memory per container.</li>
        </ol>''', 'rewriting the query before checking the statistics and the plan.') +
    scn('Operations · cost', 'Mid-level', 'EXPLAIN before scheduling',
        'A colleague wants to schedule a new report that scans a 3-year, 60 TB table. How do you review it?',
        'do you use EXPLAIN as a pre-flight check?',
        '''<ul>
          <li>Run <code>EXPLAIN EXTENDED</code> and confirm partitions are pruned (only the needed dates are listed) and only the required columns are read.</li>
          <li>Look for early filters, partial aggregation, and the join strategy of any joins; check the number of vertices and shuffle edges.</li>
          <li>Estimate the data read; if it is large, ask whether a summary table or a narrower date range would answer the same question.</li>
        </ul>''', 'scheduling first and looking at the bill afterwards.')
)
