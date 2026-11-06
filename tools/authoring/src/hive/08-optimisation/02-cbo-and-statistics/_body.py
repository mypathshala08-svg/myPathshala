import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()
def plain(n, start=0, end=None):
    """Explain output without the Beeline table borders."""
    lines = [l for l in capf(n).split('\n') if l.startswith('| ')]
    lines = [re.sub(r'\s*\|$', '', l[2:]).rstrip() for l in lines]
    lines = [l for l in lines if l.strip() not in ('Explain',)]
    return '\n'.join(lines[start:end]).strip('\n')
def rowlines(n, keep=('rows=', 'tiffingo@', '<-')):
    return '\n'.join(l for l in plain(n).split('\n') if any(k in l for k in keep))
def countout():
    c = capf('l82_count2b.txt').split('\n')
    res = [l for l in c if l.startswith('|') and '4886' in l]
    ex = [l for l in c if 'Completed executing' in l]
    return '+-------+\n|  _c0  |\n+-------+\n' + res[0] + '\n+-------+\n' + 'INFO  : Completed executing command(…); ' + ex[0].split('; ')[-1]
def setlines(n):
    return '\n'.join(re.sub(r'[|\s]', '', l) for l in capf(n).split('\n') if '=' in l and l.startswith('|'))

def opbox(x, y, label, sub='', tone='card', w=128, h=26):
    o = box(x, y, w, h, tone) + t(x + w / 2, y + (11 if sub else 16), label, 7.2, 'ink', bold=True)
    if sub:
        o += t(x + w / 2, y + 21, sub, 6.4, 'ink2', mono=True)
    return o

# ---------------------------------------------------------------- story
sc = (box(10, 12, 190, 128, 'card') + t(105, 30, 'Metastore statistics', 8.8, bold=True) +
      ''.join(t(22, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([('customers: numRows ?', 'red'), ('plan: distinct ?', 'red'), ('orders: 50,000 rows', 'green'), ('order_date: 30 distinct', 'green'), ('min 10-01 · max 10-30', 'green')])) +
      arrow(206, 76, 246, 76, 'acc', 2.2) + box(252, 46, 110, 60, 'violet') + t(307, 72, 'Cost-based', 8.4, bold=True) + t(307, 88, 'optimiser', 8.4, bold=True) +
      arrow(368, 76, 404, 76, 'acc', 2.2) + box(410, 12, 220, 128, 'amber') + t(520, 30, 'Its guesses', 8.8, bold=True) +
      opbox(422, 40, 'Gold customers', 'est 3 · real 517', 'red', 196) + opbox(422, 72, 'after ANALYZE', 'est 667 · real 517', 'green', 196) + opbox(422, 104, 'join strategy', 'chosen from these numbers', 'card', 196))
scene_svg = scene('The cost-based optimiser reads statistics from the metastore. Customers had no row count or column statistics, so it guessed 3 Gold customers instead of 517; after ANALYZE it guessed 667.', sc,
                  'The optimiser is only as good as <tspan font-weight="700" class="s-acc">the statistics it reads</tspan>.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Why does Hive think there are only 3 Gold customers?”</h2>
  <div class="story">
    <p class="narration">In Lesson 8.1, EXPLAIN ANALYZE showed Kabir that Hive expected 3 Gold customers when there were 517. Riya wants to know where such numbers come from, and whether a wrong guess can really make a query slow.</p>

{scene_svg}

R> Sir, Hive scans the table anyway. Why does it need to guess?
A> Because it decides the plan <b>before</b> reading any data: join order, map join or shuffle join, number of reducers. For that it uses <b>statistics</b> stored in the metastore: row counts, sizes, and per column the number of distinct values, nulls, minimum and maximum. The <b>cost-based optimiser</b> (CBO, built on Apache Calcite) turns them into estimates for every operator.
K> And our customers table had none?
A> Only the file size. We will run <code>ANALYZE TABLE</code>, watch the estimates change, then do two experiments the tutorials skip: stale statistics that still say <code>COMPLETE</code>, and a join that changes strategy just because the statistics changed. All outputs are real, from Hive 4.2.1.
  </div>
</section>
'''

lv = '''
LEVELS> Statistics at three levels
L1> A shopkeeper’s guess
      <ul>
        <li>Before packing for a trip, you guess how many bags you need. Hive does the same before running a query: it guesses how many rows each step will produce.</li>
        <li>The guesses come from <b>statistics</b>: facts about each table saved in the metastore, like “50,000 rows” or “30 different dates”.</li>
        <li>Good statistics → good plan. Missing or old statistics → Hive can pick a slow plan.</li>
      </ul>
L2> What is stored and how it is used
      <ul>
        <li><b>Table / partition (basic) stats:</b> <code>numRows</code>, <code>numFiles</code>, <code>totalSize</code>, <code>rawDataSize</code>. Seen with <code>DESCRIBE FORMATTED</code> or <code>SHOW TBLPROPERTIES</code>.</li>
        <li><b>Column stats:</b> <code>distinct_count</code> (NDV), <code>num_nulls</code>, <code>min</code>/<code>max</code>, <code>avg_col_len</code>/<code>max_col_len</code>, true/false counts. Seen with <code>DESCRIBE FORMATTED t col</code>.</li>
        <li>Gathered automatically on INSERT (<code>hive.stats.autogather</code>, <code>hive.stats.column.autogather</code>) or by hand with <code>ANALYZE TABLE … COMPUTE STATISTICS [FOR COLUMNS]</code>.</li>
        <li>Selectivity rules of thumb: <code>col = v</code> → rows / NDV; ranges → interpolated between min and max; values are assumed evenly spread.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li><code>Tbl:COMPLETE</code> means statistics <i>exist</i>, not that they are <i>correct</i>: after an INSERT with autogather off, Hive said COMPLETE with 100 rows for a 2,000-row table.</li>
        <li>Statistics alone flipped a join: stale stats → map join; fresh stats → shuffle (merge) join, same SQL, same threshold.</li>
        <li>Even complete stats mislead: equality on our DATE column was estimated at half the table (25,000 for 1,621), and skewed values (Pune) are under-estimated. A partition gave an exact 1,621.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>The cost-based optimiser and statistics</h2>
''' + def_block(
    'Hive’s <b>cost-based optimiser</b> (CBO), enabled by <code>hive.cbo.enable=true</code>, uses Apache Calcite to rewrite a query’s logical plan and to choose join order and join algorithms by comparing estimated costs. The costs are derived from <b>statistics</b> kept in the Hive Metastore at table, partition and column level: row counts and sizes (basic statistics) and, per column, number of distinct values, nulls, minimum and maximum. Statistics are collected automatically when data is written through Hive (<code>hive.stats.autogather</code>, <code>hive.stats.column.autogather</code>) or explicitly with <code>ANALYZE TABLE … COMPUTE STATISTICS [FOR COLUMNS]</code>, and can also answer some queries directly (<code>hive.compute.query.using.stats</code>).',
    'Before running a query, Hive estimates how many rows each step will produce, using facts about the data stored in the metastore. The optimiser picks the plan with the lowest estimated cost. If the facts are missing or old, the estimates and the plan can be badly wrong; ANALYZE TABLE refreshes them.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('CBO', 'Cost-based optimiser (Apache Calcite) in Hive.'),
    ('Basic stats', 'numRows, numFiles, totalSize, rawDataSize per table or partition.'),
    ('Column stats', 'NDV, nulls, min, max, lengths per column.'),
    ('NDV', 'Number of distinct values (Hive uses the HyperLogLog sketch).'),
    ('Selectivity', 'Fraction of rows a filter is expected to keep.'),
    ('Cardinality', 'Estimated number of rows out of an operator.'),
    ('Stale stats', 'Statistics that no longer match the data.'),
    ('Autogather', 'Collecting statistics automatically while writing data.'),
]) + '''

  <h3>Settings that matter</h3>
''' + table(['Setting', 'Lab value (Hive 4.2.1)', 'Effect'], [
    ['<code>hive.cbo.enable</code>', 'true', 'Use Calcite cost-based planning'],
    ['<code>hive.stats.autogather</code>', 'true', 'Basic stats on INSERT / CTAS'],
    ['<code>hive.stats.column.autogather</code>', 'true', 'Column stats on INSERT'],
    ['<code>hive.stats.fetch.column.stats</code>', 'true', 'Planner reads column stats'],
    ['<code>hive.compute.query.using.stats</code>', 'true', 'Answer COUNT/MIN/MAX from stats when they are trusted'],
    ['<code>hive.stats.estimate</code>', 'true', 'Estimate rows from file size when numRows is missing'],
    ['<code>hive.stats.ndv.algo</code>', 'hll', 'HyperLogLog for distinct counts'],
    ['<code>hive.auto.convert.join.noconditionaltask.size</code>', '10000000', 'Bytes below which the small side is broadcast (map join)'],
], minw=700) + lv + '''
EXAM> “What is CBO in Hive and why does it need statistics?” CBO (Calcite) chooses join order and join types by estimated cost; costs come from row counts and column statistics in the metastore. Collect them with ANALYZE TABLE … COMPUTE STATISTICS and … FOR COLUMNS, or automatically on INSERT. Check with DESCRIBE FORMATTED and in EXPLAIN (Tbl:/Col: COMPLETE, PARTIAL or NONE).
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Ways to gather and check statistics</h2>
''' + table(['Command', 'Gathers / shows', 'Notes'], [
    ['<code>ANALYZE TABLE t COMPUTE STATISTICS</code>', 'numRows, sizes', 'Reads the data (a job)'],
    ['<code>ANALYZE TABLE t COMPUTE STATISTICS NOSCAN</code>', 'numFiles, totalSize only', 'Fast: no data read'],
    ['<code>ANALYZE TABLE t COMPUTE STATISTICS FOR COLUMNS [c1, c2]</code>', 'Column stats', 'All columns if none listed'],
    ["<code>ANALYZE TABLE t PARTITION (d='…') COMPUTE STATISTICS …</code>", 'One partition', 'Use after loading a partition'],
    ['<code>DESCRIBE FORMATTED t</code> / <code>SHOW TBLPROPERTIES t</code>', 'Basic stats, COLUMN_STATS_ACCURATE', 'Table level'],
    ['<code>DESCRIBE FORMATTED t col</code>', 'Column stats of one column', 'Add PARTITION (…) for a partition'],
    ['<code>EXPLAIN q</code>', '<code>Tbl:</code> / <code>Col:</code> COMPLETE · PARTIAL · NONE', 'What the planner sees'],
], minw=720) + '''
WARN> <code>COMPLETE</code> in EXPLAIN only says that statistics are present. If files were added outside Hive (external tables), or an INSERT ran with autogather off, the numbers can be old and Hive will not notice. Refresh statistics as part of every load job.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>From a bad estimate to a different join</h2>
  <p>All outputs are real, from the Hive 4.2.1 lab (database <code>tiffingo</code>). Plan outputs keep only the lines with row counts.</p>
''' + stepper([
    ('Step 1 · What is switched on, and what customers has',
     code('sql', 'Beeline', "SET hive.cbo.enable; SET hive.stats.autogather; SET hive.stats.column.autogather;\nSET hive.compute.query.using.stats; SET hive.stats.fetch.column.stats;\nSET hive.stats.kll.enable; SET hive.stats.estimate;\nSHOW TBLPROPERTIES customers;", setlines('l82_set.txt') + '\n\n' + capf('l82_tblprops.txt')),
     'Every statistics feature is on. But <code>customers</code> is an external text table whose file was placed there, not written by an INSERT, so it has only <code>numFiles</code> and <code>totalSize</code>: <b>no numRows</b>. That is why the plan in Lesson 8.1 showed 1,413 rows, a guess from the file size (<code>hive.stats.estimate</code>).'),
    ('Step 2 · No column statistics → a guess of 3',
     code('sql', 'Beeline', "DESCRIBE FORMATTED customers plan;\n-- and from Lesson 8.1, EXPLAIN ANALYZE:", capf('l82_colstats_cust.txt') + '\n\n' + rowlines('l81_analyze.txt', ('FIL_25', 'TS_3', 'Col:NONE'))),
     'Every column statistic is empty. Without the number of distinct values of <code>plan</code>, Hive cannot compute “rows / distinct values” and falls back to default selectivities, which here produced <b>3</b> Gold customers out of an estimated 1,413. The real number is 517.'),
    ('Step 3 · ANALYZE TABLE',
     code('sql', 'Beeline', "ANALYZE TABLE customers COMPUTE STATISTICS;\nANALYZE TABLE customers COMPUTE STATISTICS FOR COLUMNS;\nDESCRIBE FORMATTED customers plan;", capf('l82_analyze.txt')),
     'The first command counts rows; the second computes column statistics for every column. Now <code>plan</code> has <b>3 distinct values</b> and 0 nulls, and <code>COLUMN_STATS_ACCURATE</code> lists every column as true.'),
    ('Step 4 · The same EXPLAIN ANALYZE, after statistics',
     code('sql', 'Beeline', "EXPLAIN ANALYZE SELECT c.city, COUNT(*) AS n, SUM(o.amount) AS rev … LIMIT 3;\n-- operator lines with rows=estimate/actual", '\n'.join(l for l in plain('l82_after.txt').split('\n') if 'rows=' in l or 'Col:' in l)),
     'customers: <b>2000/2000</b> exact, Col:COMPLETE. Gold: <b>667/517</b> (2,000 / 3 distinct plans). Join: 8,338/427, group by: 8/8. Huge improvement, from 172× off to 1.3× off on Gold. But the date filter is still <b>25000/1621</b> although orders has full column statistics. Next step looks at that.'),
    ('Step 5 · Complete statistics, still wrong estimates',
     code('sql', 'Beeline', "-- estimates from EXPLAIN vs real COUNT(*) on orders (50,000 rows, Col:COMPLETE)\nEXPLAIN SELECT COUNT(*) FROM orders_by_day WHERE order_date = '2026-10-05';   -- partitioned copy", capf('l82_estimates.txt') + '\n\n' + rowlines('l82_part.txt', ('TS_0', 'tiffingo@'))),
     'Equality on a normal column uses rows / NDV: <code>city = \'Pune\'</code> → 50,000 / 8 = 6,250, but Pune really has 7,930 (data is <b>skewed</b>). <code>amount &gt; 500</code> interpolates between min and max assuming an even spread: 22,619 vs 5,642. Equality on our DATE column was estimated at <b>half the table</b> in Hive 4.2.1, while a range on the same column used min/max (<code>&gt; \'2026-10-28\'</code> → 3,448). On the <b>partitioned</b> copy the estimate is exact, 1,621, because each partition has its own numRows.'),
    ('Step 6 · Stale statistics that say COMPLETE',
     code('sql', 'Beeline', "CREATE TABLE cust_stale STORED AS ORC AS SELECT * FROM customers WHERE customer_id <= 100;\nSET hive.stats.autogather=false;\nINSERT INTO cust_stale SELECT * FROM customers WHERE customer_id > 100;\nSELECT COUNT(*) AS real_rows FROM cust_stale;\nSHOW TBLPROPERTIES cust_stale;\nEXPLAIN SELECT city, COUNT(*) FROM cust_stale WHERE plan = 'Gold' GROUP BY city;", capf('l82_stale1.txt').split('+------------------------------------+')[0].rstrip() + '\n\n' + rowlines('l82_stale2.txt', ('TS_0', 'FIL_9', 'tiffingo@'))),
     'The table really has <b>2,000</b> rows, but numRows still says <b>100</b>, and EXPLAIN shows <code>Tbl:COMPLETE,Col:COMPLETE</code> with rows=100. Nothing warns you. After <code>ANALYZE TABLE cust_stale COMPUTE STATISTICS</code> and <code>… FOR COLUMNS</code>, the same EXPLAIN shows 2,000 and Gold 667. In real platforms this happens when files are copied in by Spark, DistCp or <code>hdfs dfs -put</code>, or autogather is switched off for speed.'),
    ('Step 7 · Statistics alone change the join',
     code('sql', 'Beeline', "SET hive.auto.convert.join.noconditionaltask.size=20000;   -- small, to show the effect\nEXPLAIN SELECT c.city, SUM(o.amount) FROM orders o JOIN cust_stale2 c   -- stale: numRows 100\n  ON o.customer_id = c.customer_id WHERE c.plan = 'Gold' GROUP BY c.city;\nEXPLAIN … JOIN cust_stale c …                                            -- fresh: 2,000", '-- stale statistics\n' + rowlines('l82_join_cust_stale2.txt', ('<-', 'Join', 'width=184')) + '\n\n-- fresh statistics\n' + rowlines('l82_join_cust_stale.txt', ('<-', 'Join', 'width=184'))),
     'Same SQL, same data, same threshold. With stale statistics Hive believes the Gold side is 33 rows (about 3 KB) and <b>broadcasts</b> it: map join. With fresh statistics it is 667 rows (about 63 KB), above our 20,000-byte limit, so Hive picks a <b>shuffle (merge) join</b> with an extra reducer stage. At production scale the dangerous case is the first: a table believed small but really huge gets broadcast and tasks run out of memory.'),
    ('Step 8 · Answers straight from statistics',
     code('sql', 'Beeline', "EXPLAIN SELECT COUNT(*) FROM orders;        -- external table\nEXPLAIN SELECT COUNT(*) FROM orders_acid;   -- managed ACID table\nSELECT COUNT(*) FROM orders_acid;", plain('l82_count.txt', 0, 6) + '\n…\n\n' + plain('l82_count2.txt') + '\n\n' + countout()),
     'With <code>hive.compute.query.using.stats=true</code>, COUNT(*) on the ACID table is answered from the metastore: the plan is only a Fetch Operator and the query took 0.0 seconds of execution (4,886 rows). On the external <code>orders</code> table Hive still runs a Map and a Reducer, because files of an external table can change without Hive knowing. Hive trusts statistics for answers only where it controls every write.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('> SHOW TBLPROPERTIES customers;', W), ('numFiles     1', G), ('totalSize    91618', G), ('numRows      (missing)', RD), ('> DESCRIBE FORMATTED customers plan;', W), ('distinct_count   (empty)', RD)], size=7.6),
    term([('> EXPLAIN ANALYZE …', W), ("Filter plan = 'Gold' (rows=3/517)", RD), ('TableScan customers (rows=1413/2000)', Y), ('  Tbl:COMPLETE, Col:NONE', Y)], size=7.6),
    term([('> ANALYZE TABLE customers COMPUTE STATISTICS;', W), ('> ANALYZE … FOR COLUMNS;', W), ('distinct_count   3', G), ('num_nulls        0', G), ('COLUMN_STATS_ACCURATE … true', G)], size=7.4),
    term([('> EXPLAIN ANALYZE …', W), ('TableScan customers (rows=2000/2000)', G), ("Filter plan = 'Gold' (rows=667/517)", G), ('Map Join (rows=8338/427)', Y), ('Filter order_date (rows=25000/1621)', RD)], size=7.4),
    term([('numRows 100   (real rows 2000)', RD), ('Tbl:COMPLETE,Col:COMPLETE', Y), ('stale  -> Map 1 <- Map 3 (BROADCAST_EDGE)', G), ('fresh  -> Reducer 2 <- Map 1, Map 4', G), ('          (SIMPLE_EDGE): merge join', G)], size=7.2),
]
def flow(hi):
    o = ''
    for k, (name, sub, tone) in enumerate([('Metastore', 'numRows · NDV', 'green'), ('Selectivity', 'rows / NDV', 'violet'), ('Cardinality', 'per operator', 'blue'), ('Plan', 'join · reducers', 'amber')]):
        x = 14 + k * 86
        o += opbox(x, 50, name, sub, 'acc' if k == hi else tone, 78, 30)
        if k:
            o += arrow(x - 7, 65, x - 1, 65, 'ink3', 1.6)
    return o
B1 = [
    t(180, 22, 'Where estimates come from', 9.4, bold=True) + flow(0) + cap('No numRows, no NDV → guesses.', 'Only file size was known.', 'amber', y=140, h=46),
    t(180, 22, 'A default selectivity', 9.4, bold=True) + flow(1) + t(180, 110, '1,413 estimated rows → 3 Gold', 8.4, 'red', mono=True) + cap('Without NDV, Hive cannot compute rows / NDV.', '', 'amber', y=150, h=34),
    t(180, 22, 'ANALYZE fills the metastore', 9.4, bold=True) + flow(0) + t(180, 110, 'plan: NDV = 3, nulls = 0', 8.4, 'green', mono=True) + cap('Basic stats + column stats.', '', 'green', y=150, h=34),
    t(180, 22, 'rows / NDV = 2000 / 3 = 667', 9.4, bold=True) + flow(2) + t(180, 110, 'actual 517: close enough', 8.4, 'green', mono=True) + cap('Uniform assumption: good, not perfect.', 'Skewed values still surprise.', 'blue', y=140, h=46),
    t(180, 22, 'Estimates choose the join', 9.4, bold=True) + flow(3) + t(180, 110, 'small side under threshold → broadcast', 8.2, 'ink', mono=True) + cap('Stale numbers, different plan.', '', 'amber', y=150, h=34),
]
see_caps = ['customers has no row count and no column statistics.',
            'The plan guessed 3 Gold customers; there are 517.',
            'ANALYZE TABLE computes basic and column statistics.',
            'Estimates are now close; the date filter is still far off.',
            'Stale statistics made Hive broadcast; fresh ones made it shuffle.']
behind_caps = ['The optimiser reads statistics from the metastore before any data is read.',
               'With nothing to go on, Hive applies default selectivities.',
               'Statistics are stored in the metastore and reused by every query.',
               'Equality filters use rows divided by distinct values, assuming an even spread.',
               'Join type and reducer counts follow from the estimated sizes.']
two = anim_two('Statistics', 'From metastore numbers to a plan', 'Real outputs', 'How the optimiser uses them', see, B1, see_caps, behind_caps)

# ---- scenario 1: stale stats after an external load
r1 = (t(180, 22, 'Nightly Spark job adds files', 9.4, bold=True) + t(180, 56, 'to an external Hive table', 8.4, 'ink2') + cap('Hive did not write them, so no autogather.', '', 'blue', y=150, h=34))
r2 = (t(180, 22, 'Statistics still say last month', 9.4, bold=True) + t(180, 56, 'numRows 100 · real 2,000 (our lab)', 8.2, 'red', mono=True) + cap('EXPLAIN still shows Tbl:COMPLETE.', '', 'amber', y=150, h=34))
r3 = (t(180, 22, 'Plan built on old numbers', 9.4, bold=True) + t(180, 56, '“small” table broadcast to every task', 8.4, 'red') + cap('At scale: memory errors or slow map joins.', '', 'amber', y=150, h=34))
r4 = (t(180, 22, 'Fix in the pipeline', 9.4, bold=True) + t(180, 56, 'ANALYZE TABLE … PARTITION (…) COMPUTE STATISTICS', 7.6, 'ink', mono=True) + cap('Right after each load, per new partition.', '', 'green', y=150, h=34))
r5 = (t(180, 22, 'Check it', 9.4, 'acc', bold=True) + t(180, 56, 'compare numRows with COUNT(*) on a sample of tables', 8, 'ink2') + cap('A weekly statistics health check.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Files written by another engine',
              'Statistics go stale when data arrives without Hive. Lab numbers are real; the platform story is typical.',
              'Stale statistics', 'Files loaded by Spark leave Hive statistics stale, the plan uses old numbers, and an ANALYZE step in the pipeline fixes it', [r1, r2, r3, r4, r5],
              ['Data arrives without Hive.',
               'Statistics keep their old values.',
               'The optimiser trusts them.',
               'Refresh statistics after each load.',
               'Monitor statistics health.'],
              hid='scenario-stale')

# ---- scenario 2: skew
k1 = (t(180, 22, 'Uniform assumption', 9.4, bold=True) + t(180, 56, "city = 'Pune' → 50,000 / 8 cities = 6,250", 8.2, 'ink', mono=True) + cap('Every city assumed equal.', '', 'blue', y=150, h=34))
k2 = (t(180, 22, 'Reality', 9.4, bold=True) + fill(60, 50, 160, 12, 'blue', rx=2) + t(230, 60, 'estimate 6,250', 8, 'ink2', anchor='start') + fill(60, 72, 203, 12, 'acc', rx=2) + t(270, 82, 'actual 7,930', 8, 'ink2', anchor='start') + cap('Real lab numbers.', '', 'amber', y=150, h=34))
k3 = (t(180, 22, 'Ranges too', 9.4, bold=True) + t(180, 56, 'amount > 500: est 22,619 · actual 5,642', 8.2, 'red', mono=True) + cap('Min–max interpolation assumes even spread.', '', 'amber', y=150, h=34))
k4 = (t(180, 22, 'What helps', 9.4, bold=True) + t(180, 52, 'partition on the filter column (exact numRows)', 8, 'ink', mono=True) + t(180, 70, 'skew-aware joins (Lesson 8.3)', 8, 'ink', mono=True) + cap('Design for the real distribution.', '', 'green', y=150, h=34))
k5 = (t(180, 22, 'Rule', 9.4, 'acc', bold=True) + t(180, 56, 'small gaps rarely change the plan', 8.2, 'ink2') + cap('Investigate the big gaps first.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Skewed data and the uniform assumption',
              'Even with complete statistics, estimates assume values are evenly spread. All numbers are real lab outputs.',
              'Skewed estimates', 'Column statistics give averages; skewed values and ranges are estimated with an even-spread assumption', [k1, k2, k3, k4, k5],
              ['Equality uses rows divided by distinct values.',
               'Pune is more common than average.',
               'Ranges are interpolated between min and max.',
               'Partitions and skew handling help.',
               'Focus on the largest estimate errors.'],
              hid='scenario-skew')

# ---- scenario 3: stats strategy
p1 = (t(180, 22, 'A statistics policy for a warehouse', 9.4, bold=True) + t(180, 56, '300 tables, daily partitions', 8.4, 'ink2') + cap('Keep stats fresh without huge cost.', '', 'blue', y=150, h=34))
p2 = (t(180, 22, 'Hive writes → autogather', 9.4, bold=True) + t(180, 56, 'hive.stats.autogather · column.autogather = true', 7.8, 'ink', mono=True) + cap('Free for INSERT and CTAS.', '', 'green', y=150, h=34))
p3 = (t(180, 22, 'Other engines → ANALYZE per partition', 9.4, bold=True) + t(180, 56, "ANALYZE … PARTITION (d='…') … FOR COLUMNS", 7.8, 'ink', mono=True) + cap('Only the new partition: ~1 s in our lab.', '', 'green', y=150, h=34))
p4 = (t(180, 22, 'Columns that matter', 9.4, bold=True) + t(180, 56, 'join keys, filter columns, group-by columns', 8.2, 'ink2') + cap('FOR COLUMNS c1, c2 to save time on wide tables.', '', 'blue', y=150, h=34))
p5 = (t(180, 22, 'Verify in EXPLAIN', 9.4, 'acc', bold=True) + t(180, 56, 'no Col:NONE / PARTIAL on key tables', 8.4, 'ink2') + cap('Part of the plan review checklist.', '', 'green', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'A statistics policy for a whole warehouse',
              'A practical policy many teams follow. (Typical practice; the 1-second partition ANALYZE is from our lab.)',
              'Statistics policy', 'Autogather for Hive writes, per-partition ANALYZE for other loads, key columns first, verified in EXPLAIN', [p1, p2, p3, p4, p5],
              ['Define a policy, not one-off fixes.',
               'Let Hive gather stats on its own writes.',
               'Analyze new partitions loaded by other tools.',
               'Prioritise columns used by joins and filters.',
               'Check plans for missing statistics.'],
              hid='scenario-policy')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>How statistics turn into a plan</h2>
  <p>Left: real outputs. Right: what the optimiser does with them.</p>
''' + two + '''
  <p>Three live scenarios follow: stale statistics, skewed data, and a statistics policy.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Statistics at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'ANALYZE', 11, 'green', bold=True, mono=True) + t(60, 58, 'after each load', 7.4, 'ink2'),
    '1. ETL pipelines',
    'Load jobs end with ANALYZE on the new partition, so downstream reports are planned with current numbers.',
    ['Load', '*ANALYZE', 'Fresh plans']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'joins', 11, 'blue', bold=True) + t(60, 58, 'right strategy', 7.4, 'ink2'),
    '2. Stable join plans',
    'Accurate sizes keep map joins for truly small tables and shuffle joins for big ones, avoiding memory failures.',
    ['Stats', '*join choice', 'No OOM']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'COUNT(*)', 10, 'violet', bold=True, mono=True) + t(60, 58, 'from metastore', 7.4, 'ink2'),
    '3. Instant metadata answers',
    'On managed (ACID) tables, COUNT(*), MIN and MAX can be answered from statistics without running a job.',
    ['Query', '*stats', 'Instant']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'profiling', 10, 'acc', bold=True) + t(60, 58, 'data quality', 7.4, 'ink2'),
    '4. Cheap data profiling',
    'Column statistics (nulls, distinct counts, min and max) give data quality teams a quick profile of every column.',
    ['Column stats', '*profile', 'Quality checks']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'health', 11, 'acc', bold=True) + t(60, 58, 'stats monitor', 7.4, 'ink2'),
    '5. Platform health checks',
    'Platform teams flag tables whose numRows is missing or far from reality before users notice slow queries.',
    ['Metastore', '*check', 'Alerts']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> read <a href="../01-explain-in-depth/">8.1 EXPLAIN in depth</a>; recall partitions (<a href="../../05-partitioning-and-bucketing/01-partitioning/">5.1</a>) and the metastore (<a href="../../01-introduction/03-hive-architecture-and-metastore/">2.2</a>).</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
