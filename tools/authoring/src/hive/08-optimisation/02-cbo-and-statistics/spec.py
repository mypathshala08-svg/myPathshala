import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from hivekit import tables
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()
BODY = body(HERE)

def statlines(n, keys):
    return '\n'.join(l for l in capf(n).split('\n') if any(k in l for k in keys))

META = dict(
    module='08-optimisation', lesson='02-cbo-and-statistics', n='8.2',
    module_label='Module 8 · Query optimisation',
    title='The cost-based optimiser and statistics',
    desc='How Hive’s cost-based optimiser (Apache Calcite) uses table, partition and column statistics, with real Hive 4.2.1 results: ANALYZE TABLE and FOR COLUMNS, DESCRIBE FORMATTED, estimates before and after statistics (3 → 667 for 517 real rows), skew and the uniform assumption, exact estimates from partitions, stale statistics that still say COMPLETE, a join that flips from map join to shuffle join because of statistics, NOSCAN on ORC, and COUNT(*) answered from the metastore.',
    og_desc='Hive guessed 3 rows; there were 517. Then stale statistics changed a join. The cost-based optimiser and statistics in Hive 4.2.1, with real outputs.',
    minutes=40, level='Intermediate → Advanced',
    lead='Lesson 8.1 found estimates that were wildly off. This lesson shows <b>where estimates come from</b>: statistics in the metastore read by the <b>cost-based optimiser</b>. We gather them with ANALYZE, watch the plan improve, find where even complete statistics mislead, and run two experiments: stale statistics that still say COMPLETE, and a join that changes strategy because of them. <b>All outputs are real</b>, from Hive 4.2.1.',
    chips=['Real Hive 4.2.1 outputs', 'Stale-stats experiment', 'Join flipped by statistics', 'Runs in your browser (Python)'],
)

MAIN = '''# How Hive estimates a filter from column statistics (simplified)
num_rows = 50000
ndv = {"city": 8, "plan": 3, "customer_id": 2000}
amount_min, amount_max = 40, 880                # real min / max from DESCRIBE FORMATTED

def eq_estimate(col):                           # col = value
    return round(num_rows / ndv[col])

def range_estimate(lo):                         # amount > lo, even spread
    return round(num_rows * (amount_max - lo) / (amount_max - amount_min))

print("city = 'Pune'  :", eq_estimate("city"), " (real 7,930)")
print("amount > 500   :", range_estimate(500), " (real 5,642)")
print("plan = 'Gold' on 2,000 customers:", round(2000 / ndv["plan"]), " (real 517)")
'''
RUN = dict(
    heading='Run the code: estimate like the optimiser',
    intro='<p>These programs reproduce the optimiser’s arithmetic with the real numbers from the lab. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('    return round(num_rows / ndv[col])', 'Equality: rows divided by the number of distinct values. 50,000 / 8 = 6,250, exactly what EXPLAIN printed for Pune.'),
        ('    return round(num_rows * (amount_max - lo) / (amount_max - amount_min))', 'Ranges: a straight line between min and max, assuming values are evenly spread. With the real min 40 and max 880 this gives 22,619, exactly Hive’s estimate.'),
    ],
    tasks=[
        dict(label='1 · Equality and ranges', hint='Press <b>Run</b>. The Pune and Gold numbers match the real EXPLAIN output (6,250 and 667). Real counts: 7,930 and 517.', code=None),
        dict(label='2 · Predict first: estimate error', hint='<b>Predict first:</b> which estimate is furthest from reality? Real pairs from the lab.',
             code='''pairs = {"Pune": (6250, 7930), "customer 1492": (24, 41), "amount > 500": (22619, 5642), "date = 10-05": (25000, 1621)}
for k, (e, a) in pairs.items():
    print(f"{k:14} x{max(e, a) / min(e, a):5.1f}")
'''),
        dict(label='3 · Map join or not', hint='Hive broadcasts the small side if its estimated size is under the threshold. Try the stale (33 rows) and fresh (667 rows) estimates.',
             code='''threshold = 20000          # bytes, as in our experiment
width = 95                 # bytes per row after Select
for rows in [33, 667]:
    size = rows * width
    print(rows, "rows ->", size, "bytes ->", "MAP JOIN" if size <= threshold else "SHUFFLE JOIN")
'''),
        dict(label='4 · Stale or fresh?', hint='Compare metastore numRows with a real count. Flag tables more than 20% off.',
             code='''tables = {"cust_stale": (100, 2000), "customers": (2000, 2000), "orders": (50000, 50000)}
for t, (stats, real) in tables.items():
    off = abs(stats - real) / real
    print(f"{t:11} stats {stats:>6} real {real:>6} ->", "STALE" if off > 0.2 else "ok")
'''),
        dict(label='5 · Spot the error', hint='This health check never finds stale tables. Fix the comparison.', expect='error',
             code='''stats, real = 100, 2000
stale = stats > real * 1.2           # bug: only catches tables that shrank
assert stale, "numRows can be too LOW as well: compare the absolute difference"
print("stale")
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: NOSCAN, partition statistics and column statistics',
    intro='<p>More statistics commands on the lab tables. <b>Outputs are real</b>, from Hive 4.2.1.</p>',
    items=[
        dict(title='1 · NOSCAN on an ORC table with stale numRows', cmd="-- cust_stale2: numRows was 100, real rows 2000\nANALYZE TABLE cust_stale2 COMPUTE STATISTICS NOSCAN;\nSHOW TBLPROPERTIES cust_stale2 ('numRows');\nSHOW TBLPROPERTIES cust_stale2 ('numFiles');", file='Beeline',
             output='\n'.join(capf('l82_noscan.txt').split('\n')[:10]),
             note='NOSCAN does not launch a job, yet numRows became 2,000. For ORC, Hive can read the row count from each file’s footer, so NOSCAN is a cheap fix for ORC/Parquet tables. On a text table it can only record file counts and sizes.'),
        dict(title='2 · Statistics of one partition', cmd="DESCRIBE FORMATTED orders_by_day PARTITION (order_date='2026-10-05');\n-- statistics lines", file='Beeline',
             output=statlines('l82_partstats.txt', ('numRows', 'numFiles', 'rawDataSize', 'totalSize')),
             note='Each partition keeps its own numRows: 1,621 for 5 October. That is why the estimate on the partitioned table was exact while the same filter on the unpartitioned table was estimated at 25,000.'),
        dict(title='3 · Column statistics of a DATE column', cmd='DESCRIBE FORMATTED orders order_date;', file='Beeline',
             output='\n'.join(capf('l82_colstats_orders.txt').split('\n')[:11] + [capf('l82_colstats_orders.txt').split('\n')[-1]]),
             note='min, max and 30 distinct values, all correct, gathered automatically when the table was loaded with INSERT. Hive 4.2.1 still estimated equality on this column at half the table; range filters on it did use min and max.'),
    ],
)

TRACE = dict(
    heading='Estimating the Gold filter, before and after ANALYZE',
    intro='<p>Follow the numbers the optimiser uses for <code>plan = \'Gold\'</code>.</p>',
    code='''num_rows = None             # no numRows in the metastore
size_estimate = 1413        # rows guessed from file size
ndv = None                  # no column statistics
est = 3                     # default selectivity: the plan said 3
num_rows = 2000             # after ANALYZE ... COMPUTE STATISTICS
ndv = 3                     # after ANALYZE ... FOR COLUMNS
est = round(num_rows / ndv)
print("estimate:", est, "real: 517")
''',
    notes={2: 'Guess :: hive.stats.estimate turned the file size into 1,413 rows.', 4: 'Before :: Without NDV, Hive falls back to default selectivities.', 7: 'After :: 2,000 / 3 = 667, close to the real 517.'},
)

WORKED_INTRO = 'Three statistics decisions you will face on a real platform.'
EXAMPLES = [
    dict(level='b', tag='Data engineering · loads', title='Which ANALYZE after which load?',
         problem='<p>For three loads, write the statistics command that should follow.</p>',
         inp='A: INSERT into ORC table by Hive · B: Spark writes a new partition d=2026-10-27 · C: text files copied with hdfs dfs -put',
         approach=['Hive writes gather statistics automatically.', 'Other writers: analyse the new partition.', 'Text files: a full ANALYZE is needed for row counts.'],
         code='''loads = {
  "A Hive INSERT (ORC)": "nothing: autogather",
  "B Spark partition":   "ANALYZE TABLE t PARTITION (d='2026-10-27') COMPUTE STATISTICS FOR COLUMNS;",
  "C hdfs put (text)":   "ANALYZE TABLE t COMPUTE STATISTICS; ... FOR COLUMNS;",
}
for k, v in loads.items():
    print(f"{k:20} -> {v}")
''', notes={3: 'Partition :: Analyse only what changed.'},
         tryit='For ORC or Parquet, NOSCAN already fixed numRows in our lab (from file footers); column statistics still need FOR COLUMNS.'),
    dict(level='i', tag='Platform · monitoring', title='Find stale tables',
         problem='<p>Compare metastore numRows with real counts for a list of tables and report the worst first.</p>',
         inp='cust_stale: 100 vs 2,000 · customers: 2,000 vs 2,000 · orders: 50,000 vs 50,000',
         approach=['Get numRows from SHOW TBLPROPERTIES.', 'Get COUNT(*) (on samples for big tables).', 'Sort by the ratio.'],
         code='''t = {"cust_stale": (100, 2000), "customers": (2000, 2000), "orders": (50000, 50000)}
for name, (s, r) in sorted(t.items(), key=lambda kv: -max(kv[1]) / min(kv[1])):
    print(f"{name:11} x{max(s, r) / min(s, r):.1f}")
''', notes={2: 'Order :: The worst ratio first: that table will mislead the planner most.'},
         tryit='Real: cust_stale was 20× off while EXPLAIN said Tbl:COMPLETE. A nightly job like this catches it before users do.'),
    dict(level='a', tag='Architecture · memory', title='Why stale stats can crash a map join',
         problem='<p>A dimension table grew from 1 MB to 2 GB, but statistics still say 1 MB. The map-join threshold is 10 MB (the lab default). What happens?</p>',
         inp='stats 1 MB · real 2 GB · threshold 10,000,000 bytes',
         approach=['Planner compares the estimate with the threshold.', 'Estimate says broadcast.', 'Every task must build a 2 GB hash table.'],
         code='''threshold = 10_000_000
stats_size, real_size = 1_000_000, 2_000_000_000
plan = "MAP JOIN" if stats_size <= threshold else "SHUFFLE JOIN"
print("plan:", plan)
print("hash table each task must hold:", real_size // 1_000_000, "MB")
''', notes={3: 'Decision :: Made from statistics only, before any data is read.'},
         tryit='Illustrative sizes. Our lab showed the same mechanism at small scale: stale stats → BROADCAST_EDGE, fresh stats → merge join. Hive has run-time safeguards for some cases, but fresh statistics are the real fix.'),
]

QUIZ = mix([
    dict(q='Beginner: Which command gathers column statistics?', options=['ANALYZE TABLE t COMPUTE STATISTICS', 'ANALYZE TABLE t COMPUTE STATISTICS FOR COLUMNS', 'DESCRIBE t', 'MSCK REPAIR TABLE t'], answer=1,
         why='Without FOR COLUMNS only basic statistics (rows, sizes) are collected.'),
    dict(q='Beginner: Where does Hive keep statistics?', options=['In the data files only', 'In the Hive Metastore', 'In HiveServer2 memory', 'In YARN'], answer=1,
         why='As table/partition parameters and column statistics tables in the metastore.'),
    dict(q='Beginner: What does Col:NONE in EXPLAIN mean?', options=['No columns read', 'No column statistics available', 'Columns are null', 'Vectorisation is off'], answer=1,
         why='customers had Col:NONE before ANALYZE.'),
    dict(q='Intermediate: After ANALYZE, why was plan = \'Gold\' estimated at 667?', options=['Random', '2,000 rows / 3 distinct values', 'From a histogram', 'From the previous run'], answer=1,
         why='Equality selectivity = 1 / NDV, assuming an even spread.'),
    dict(q='Intermediate: An INSERT ran with hive.stats.autogather=false. What did EXPLAIN show?', options=['Tbl:NONE', 'Tbl:COMPLETE with the old row count (100 instead of 2,000)', 'An error', 'The real count'], answer=1,
         why='COMPLETE means statistics exist, not that they are current.'),
    dict(q='Intermediate: Why was the filter on the partitioned table estimated exactly (1,621)?', options=['Luck', 'Each partition has its own numRows', 'It used a histogram', 'Partitions disable CBO'], answer=1,
         why='Pruning picks one partition, whose numRows is exact.'),
    dict(q='Advanced: Same SQL, same threshold; stale stats gave a map join and fresh stats a merge join. Why?', options=['A bug', 'The join type is chosen from the estimated size of the small side', 'Merge join is always better', 'Vectorisation changed'], answer=1,
         why='33 rows estimated (under the threshold) vs 667 (over it).'),
    dict(q='Advanced: Why did COUNT(*) on the external orders table still run a job?', options=['Stats were missing', 'Hive only answers from statistics where it controls all writes, not for external tables', 'COUNT(*) never uses stats', 'The table was too big'], answer=1,
         why='The ACID table was answered by a Fetch operator in 0.0 s.'),
])

REVISION = [
    '<b>CBO</b> (Calcite, <code>hive.cbo.enable</code>) picks join order and join types by estimated cost; estimates come from <b>metastore statistics</b>.',
    '<b>Basic:</b> numRows, numFiles, totalSize, rawDataSize. <b>Column:</b> NDV (HLL), nulls, min, max, lengths.',
    '<b>Gather:</b> autogather on Hive writes; <code>ANALYZE TABLE t [PARTITION (…)] COMPUTE STATISTICS [NOSCAN | FOR COLUMNS [c…]]</code>.',
    '<b>Check:</b> <code>DESCRIBE FORMATTED t [col]</code>, <code>SHOW TBLPROPERTIES</code>, EXPLAIN <code>Tbl:/Col: COMPLETE|PARTIAL|NONE</code>.',
    '<b>Estimates:</b> equality = rows / NDV; ranges interpolated min→max; values assumed evenly spread → skew is under-estimated.',
    'Lab: Gold 3 → 667 (real 517) after ANALYZE; DATE equality still 25,000 (real 1,621); partition → exact 1,621.',
    '<b>Stale stats</b> still say COMPLETE (100 vs 2,000) and can flip joins (map join ↔ merge join). Analyse after every non-Hive load.',
    '<b>compute.query.using.stats:</b> COUNT(*) from metastore for managed/ACID tables (Fetch only); external tables still run a job.',
]
FAQ = [
    ('Does ANALYZE TABLE lock or slow down the table?', 'It reads the data (except NOSCAN) and writes only metadata. Queries can keep running. On big tables analyse new partitions only, and list the important columns in FOR COLUMNS to save time.'),
    ('Are statistics gathered automatically?', 'For data written through Hive (INSERT, CTAS, and in Hive 4 also column statistics on INSERT), yes, when autogather is on. Not for files placed by other tools: Spark (unless it updates Hive statistics), DistCp, hdfs dfs -put, or LOAD DATA in some cases.'),
    ('What are KLL histograms in Hive 4?', 'Hive 4 can store KLL sketches as histograms for numeric columns (<code>hive.stats.kll.enable</code>). They are meant to improve range estimates on skewed data. In our lab, switching it on and re-analysing did not change the estimates of our queries, so measure on your own data before relying on it.'),
    ('Does Spark use Hive statistics?', 'Spark SQL reads table statistics from the metastore when its own CBO is enabled, and has its own ANALYZE TABLE command that writes statistics in Spark’s format. Engines do not always read each other’s column statistics, so analyse with the engine that will query the table.'),
    ('Can I set statistics by hand?', 'Yes, for example <code>ALTER TABLE t SET TBLPROPERTIES (\'numRows\'=\'…\')</code> or ALTER TABLE … UPDATE STATISTICS. It is useful for testing plans, but in production hand-written numbers become stale too; prefer ANALYZE.'),
]

PRACTICE_INTRO = 'Programs that reproduce the optimiser’s statistics arithmetic, with the HiveQL in each explanation.'
PROBLEMS = [
    dict(level='easy', title='Equality estimate', stmt='Estimate rows for plan = \'Gold\' with 2,000 rows and 3 distinct plans.', inp='2,000 and 3',
         code='''print(round(2000 / 3))
''', explain='667, the estimate after ANALYZE TABLE customers COMPUTE STATISTICS FOR COLUMNS.'),
    dict(level='easy', title='Estimate error', stmt='How many times off was the date estimate?', inp='estimate 25,000, actual 1,621',
         code='''print(round(25000 / 1621, 1))
''', explain='15.4×. Partitioning by date gave an exact estimate.'),
    dict(level='easy', title='Stale ratio', stmt='Metastore says 100 rows, COUNT(*) says 2,000. How stale?', inp='100 and 2,000',
         code='''print(2000 / 100, "x more rows than the statistics say")
''', explain='Fix with ANALYZE TABLE cust_stale COMPUTE STATISTICS (or NOSCAN for ORC).'),
    dict(level='medium', title='Distinct per column', stmt='Compute NDV per column from a small sample, like FOR COLUMNS does.', inp='sample rows',
         code='''rows = [("Pune", "Gold"), ("Mumbai", "Basic"), ("Pune", "Silver"), ("Delhi", "Gold")]
for i, col in enumerate(["city", "plan"]):
    print(col, len({r[i] for r in rows}))
''', explain='Hive uses HyperLogLog sketches to approximate NDV without keeping every value.'),
    dict(level='medium', title='Range estimate', stmt='Estimate rows for order_date > \'2026-10-28\' with 30 days between min and max.', inp='50,000 rows, 10-01 to 10-30',
         code='''rows, days_total, days_after = 50000, 29, 2
print(round(rows * days_after / days_total))
''', explain='3,448: exactly what Hive 4.2.1 printed for this range filter.'),
    dict(level='medium', title='Partitions to analyse', stmt='List partitions loaded today by Spark that need ANALYZE.', inp='load log',
         code='''log = [("2026-10-26", "hive"), ("2026-10-27", "spark"), ("2026-10-27b", "spark")]
for p, engine in log:
    if engine != "hive":
        print(f"ANALYZE TABLE orders PARTITION (d='{p}') COMPUTE STATISTICS FOR COLUMNS;")
''', explain='Hive writes are covered by autogather; other engines are not.'),
    dict(level='business', title='Broadcast risk', stmt='For each dimension, would a stale estimate cause a broadcast of a table that is really too big?', inp='stats size, real size, 10 MB threshold',
         code='''threshold = 10_000_000
dims = {"stores": (2e6, 3e6), "customers": (5e6, 900e6), "plans": (1e4, 1e4)}
for d, (s, r) in dims.items():
    risky = s <= threshold < r
    print(f"{d:10}", "RISK" if risky else "ok")
''', explain='customers is the risk: analyse it before the next report run.'),
    dict(level='business', title='Cost of ANALYZE vs benefit', stmt='ANALYZE of a new partition takes about 1 s; a wrong join plan costs 10 minutes once a week. Worth it?', inp='illustrative',
         code='''analyze_s_per_day = 1
bad_plan_s_per_week = 600
print("ANALYZE per week:", analyze_s_per_day * 7, "s  vs  bad plan:", bad_plan_s_per_week, "s")
''', explain='7 seconds against 10 minutes: refreshing statistics is almost always cheaper than a bad plan. Our partition ANALYZE took about 1 second.'),
]

SCN_INTRO = 'Statistics questions separate people who tune by guessing from people who read plans.'
SCENARIOS = (
    scn('Any company · Hive', 'Fresher', '“What is the CBO in Hive?”',
        'Explain the cost-based optimiser.',
        'do you connect CBO with statistics?',
        '<p>The cost-based optimiser, based on Apache Calcite, chooses join order and join methods by estimating the cost of different plans. Costs come from statistics in the metastore: row counts and column statistics like distinct values, nulls, min and max. Gather them with ANALYZE TABLE … COMPUTE STATISTICS and … FOR COLUMNS; check them with DESCRIBE FORMATTED and in EXPLAIN.</p>', 'Describing CBO without mentioning statistics.') +
    scn('Data engineering', 'Mid-level', 'Join started failing with out-of-memory',
        'A daily join suddenly fails in map tasks with memory errors. The SQL did not change; a dimension table grew a lot.',
        'can you connect a memory failure to statistics?',
        '''<ol>
          <li>EXPLAIN: is the dimension broadcast (BROADCAST_EDGE, Map Join)? What size does the plan think it has?</li>
          <li>Compare numRows/totalSize in the metastore with reality: likely stale (files written by another tool).</li>
          <li>ANALYZE the table; the planner switches to a shuffle join. Add ANALYZE to the loading job.</li>
        </ol>''', 'Only raising container memory.') +
    scn('Analytics', 'Mid-level', 'Estimates wrong even with statistics',
        'EXPLAIN ANALYZE shows estimates 10× off on a table with full column statistics.',
        'do you know the limits of statistics?',
        '''<ul>
          <li>Statistics are averages: skewed values and correlated filters break the even-spread assumption.</li>
          <li>Check whether the filter is on a partition column (exact counts) or could be.</li>
          <li>If the plan choice is still right, accept the gap; if not, use hints or settings for that query, or redesign (partitioning, skew handling).</li>
        </ul>''', '“Run ANALYZE again” when statistics are already fresh.') +
    scn('Platform', 'Senior', 'Statistics policy',
        'Define how statistics are maintained across a warehouse fed by Hive, Spark and file drops.',
        'can you design a process, not a one-off fix?',
        '''<ul>
          <li>Autogather on for Hive writes; per-partition ANALYZE … FOR COLUMNS (key columns) at the end of every non-Hive load.</li>
          <li>Nightly health check comparing numRows with sampled counts; alert on large gaps.</li>
          <li>Plan checks in CI flag Col:NONE/PARTIAL on critical tables.</li>
        </ul>''', 'Analysing every table nightly regardless of change.')
)
