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

def opbox(x, y, label, sub='', tone='card', w=128, h=26):
    o = box(x, y, w, h, tone) + t(x + w / 2, y + (11 if sub else 16), label, 7.2, 'ink', bold=True)
    if sub:
        o += t(x + w / 2, y + 21, sub, 6.4, 'ink2', mono=True)
    return o

# ---------------------------------------------------------------- story
sc = (box(10, 12, 270, 128, 'card') + t(145, 30, 'The SQL Kabir wrote', 8.8, bold=True) +
      ''.join(t(22, 52 + k * 15, s, 7.2, 'ink2', anchor='start', mono=True) for k, s in enumerate(['SELECT c.city, COUNT(*), SUM(o.amount)', 'FROM orders o JOIN customers c …', "WHERE o.order_date = '2026-10-05'", "  AND c.plan = 'Gold'", 'GROUP BY … ORDER BY rev DESC LIMIT 3'])) +
      arrow(286, 76, 326, 76, 'acc', 2.2) + box(332, 46, 70, 60, 'acc') + t(367, 72, 'EXPLAIN', 8.4, bold=True) + t(367, 88, 'ANALYZE', 8.4, bold=True) +
      arrow(408, 76, 444, 76, 'acc', 2.2) + box(450, 12, 180, 128, 'green') + t(540, 30, 'What Hive will do', 8.8, 'green', bold=True) +
      opbox(470, 40, 'Map 4: scan customers', 'est 3 · actual 517', 'red', 140) + opbox(470, 72, 'Map 1: scan + map join', 'est 25000 · actual 1621', 'red', 140) + opbox(470, 104, 'Reducers 2, 3: group, top 3', '', 'card', 140))
scene_svg = scene('Kabir’s SQL goes through EXPLAIN ANALYZE, which shows the plan Hive will run: a scan of customers broadcast into a map join with orders, then two reducers. Estimated row counts are far from the actual ones.', sc,
                  'EXPLAIN shows <tspan font-weight="700" class="s-acc">the plan, not the SQL</tspan>: what runs where, in what order, on how many rows.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“The query works. But what is Hive actually doing?”</h2>
  <div class="story">
    <p class="narration">Marketing wants the top three cities by revenue from Gold customers on 5 October. Kabir’s query returns the right answer, but on the production cluster a similar query takes twenty minutes. Before changing anything, Arjun Sir asks him to read the plan.</p>

{scene_svg}

K> Sir, the plan is 50 lines of operators. Where do I even start?
A> At the bottom. A Hive plan is a tree: data enters at the <b>TableScans</b> at the leaves and flows up to the <b>File Output</b> at the top. The “Vertex dependency” lines at the start tell you how the Tez stages connect. Then look at the row counts: Hive’s guesses decide the join strategy and the number of reducers.
R> And if the guesses are wrong?
A> <code>EXPLAIN ANALYZE</code> runs the query and prints <b>estimated/actual</b> rows next to each operator. Today we read one real plan line by line, then use EXPLAIN’s other forms: CBO, COST, the classic stage view, VECTORIZATION, DEPENDENCY and LOCKS. All outputs are real, from Hive 4.2.1.
  </div>
</section>
'''

lv = '''
LEVELS> Reading plans at three levels
L1> A recipe card
      <ul>
        <li>SQL says <i>what</i> you want; the plan says <i>how</i> Hive will cook it: which tables to read, in which order to join, where to group and sort.</li>
        <li><code>EXPLAIN</code> + your query prints the plan without running it. Read it from the <b>bottom up</b>: tables at the bottom, final result at the top.</li>
        <li>Each step is an <b>operator</b>: TableScan (read), Filter (WHERE), Select (columns), Join, Group By, Limit, File Output.</li>
      </ul>
L2> Vertices, edges and estimates
      <ul>
        <li>Hive on Tez runs a <b>DAG</b> of <b>vertices</b>: <code>Map n</code> (read files) and <code>Reducer n</code> (after a shuffle). <code>Map 1 &lt;- Map 4 (BROADCAST_EDGE)</code> means Map 4’s output is sent whole to every Map 1 task: a map join.</li>
        <li><b>Edges:</b> SIMPLE_EDGE (shuffle by key), BROADCAST_EDGE (copy to all), CUSTOM_SIMPLE_EDGE / CUSTOM_EDGE (special routing).</li>
        <li><code>(rows=25000 width=172)</code> are <b>estimates</b> from statistics. <code>Tbl:COMPLETE, Col:NONE</code> says table stats exist but column stats do not.</li>
        <li>A map-side <b>Group By</b> (partial, hash mode) feeds a reducer-side Group By (mergepartial): aggregation in two phases.</li>
      </ul>
L3> Every EXPLAIN form we used
      <ul>
        <li><code>EXPLAIN ANALYZE</code> runs the query: rows=<i>estimate/actual</i>. Our plan guessed 3 Gold customers (actual 517) and 25,000 orders on one day (actual 1,621).</li>
        <li><code>EXPLAIN CBO [COST]</code> shows the Calcite logical plan the cost-based optimiser chose, with its own row estimates and costs.</li>
        <li><code>SET hive.explain.user=false</code> switches to the classic stage view with full Statistics lines and Group By modes.</li>
        <li><code>EXPLAIN VECTORIZATION [ONLY] SUMMARY|DETAIL</code>, <code>EXPLAIN DEPENDENCY</code>, <code>EXPLAIN LOCKS</code>, <code>EXPLAIN EXTENDED</code>, <code>EXPLAIN AST</code> answer narrower questions.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>EXPLAIN and the query plan</h2>
''' + def_block(
    '<code>EXPLAIN</code> displays the <b>execution plan</b> Hive generates for a statement without running it: the stages (on Tez, a DAG of vertices connected by edges) and, for each vertex, the tree of <b>operators</b> (TableScan, Filter, Select, Join, Group By, Reduce Output, Limit, File Output) with estimated row counts and data sizes derived from table and column statistics. Variants add information: <code>ANALYZE</code> executes the query and shows actual row counts, <code>CBO</code> shows the cost-based optimiser’s logical plan, <code>VECTORIZATION</code> explains vectorised execution, <code>DEPENDENCY</code> lists inputs, <code>LOCKS</code> lists the locks a statement would take, and <code>EXTENDED</code> adds physical details.',
    'EXPLAIN prints Hive’s plan for your query: which tables it reads, how it joins and groups, how the work is split into Tez stages, and how many rows it expects at each step. It is the first thing to look at when a query is slow.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Operator', 'One step of the plan: TableScan, Filter, Join, Group By …'),
    ('Vertex', 'A Tez stage: Map n or Reducer n, run by many tasks.'),
    ('Edge', 'How data flows between vertices: SIMPLE (shuffle), BROADCAST …'),
    ('Shuffle', 'Rows sent across the network, grouped by key, to reducers.'),
    ('Estimate', '<code>rows=</code> in EXPLAIN: what statistics predict.'),
    ('Actual', 'The second number in EXPLAIN ANALYZE (estimate/actual).'),
    ('CBO', 'Cost-based optimiser (Apache Calcite) that picks join order and methods.'),
    ('Top N Key', 'Operator that drops rows early when only the top N are needed.'),
]) + '''

  <h3>EXPLAIN forms and when to use them</h3>
''' + table(['Form', 'Answers', 'Runs the query?'], [
    ['<code>EXPLAIN q</code>', 'Vertices, edges, operators, estimates', 'No'],
    ['<code>EXPLAIN ANALYZE q</code>', 'Estimate vs actual rows per operator', '<b>Yes</b>'],
    ['<code>EXPLAIN CBO [COST | JOINCOST] q</code>', 'Logical plan and costs chosen by Calcite', 'No'],
    ['<code>SET hive.explain.user=false; EXPLAIN q</code>', 'Classic stage view, statistics, Group By modes', 'No'],
    ['<code>EXPLAIN VECTORIZATION ONLY SUMMARY q</code>', 'Which vertices run vectorised, and why not', 'No'],
    ['<code>EXPLAIN DEPENDENCY q</code>', 'Tables and partitions read (JSON)', 'No'],
    ['<code>EXPLAIN LOCKS q</code>', 'Locks an ACID statement would take', 'No'],
    ['<code>EXPLAIN EXTENDED q</code> / <code>EXPLAIN AST q</code>', 'Physical paths and properties / parse tree', 'No'],
], minw=680) + lv + '''
EXAM> “How do you analyse a slow Hive query?” Start with EXPLAIN: read vertices and edges, find the join type (map join vs shuffle join), compare estimated rows with reality (EXPLAIN ANALYZE), check statistics (Col:NONE is a warning), partition pruning (EXPLAIN DEPENDENCY) and vectorisation. Then change one thing and compare.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Operators you will see in Hive plans</h2>
''' + table(['Operator', 'Does', 'Clue in our plan'], [
    ['TableScan [TS]', 'Reads a table', '<code>tiffingo@customers,c,Tbl:COMPLETE,Col:NONE</code>'],
    ['Filter Operator [FIL]', 'Applies WHERE (and pushed-down conditions)', "<code>predicate:((order_date = DATE'2026-10-05') and customer_id is not null)</code>"],
    ['Select Operator [SEL]', 'Keeps needed columns, computes expressions', '<code>Output:["_col0","_col1"]</code>'],
    ['Map Join Operator [MAPJOIN]', 'Joins against a broadcast hash table', '<code>Conds:SEL_29._col0=RS_27._col0(Inner)</code>'],
    ['Merge Join Operator', 'Joins two sorted, shuffled inputs (shuffle join)', 'Lesson 8.3'],
    ['Group By Operator [GBY]', 'Aggregates (hash on maps, mergepartial on reducers)', '<code>aggregations:["count()","sum(_col1)"]</code>'],
    ['Reduce Output / SHUFFLE [RS]', 'Sends rows to the next vertex', '<code>PartitionCols:_col0</code>'],
    ['Top N Key [TNK]', 'Keeps only rows that can be in the top N', '<code>keys:_col2,top n:3</code>'],
    ['Limit / File Output', 'Stops after N rows / writes the result', '<code>Number of rows:3</code>'],
], minw=740) + '''
WARN> Hive adds conditions you did not write, like <code>customer_id is not null</code> before an inner join (NULL keys can never match). That is the optimiser at work, not a mistake. Likewise <code>_col0</code>, <code>_col1</code> are internal names for the columns flowing between operators.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>One query, every kind of EXPLAIN</h2>
  <p>All outputs are real, from the Hive 4.2.1 lab (database <code>tiffingo</code>). Long lines are shortened with “…”.</p>
''' + stepper([
    ('Step 1 · The query and its answer',
     code('sql', 'Beeline', "SELECT c.city, COUNT(*) AS n, SUM(o.amount) AS rev\nFROM orders o JOIN customers c ON o.customer_id = c.customer_id\nWHERE o.order_date = '2026-10-05' AND c.plan = 'Gold'\nGROUP BY c.city ORDER BY rev DESC LIMIT 3;", capf('l81_run.txt')),
     'Bengaluru leads with 100 Gold orders that day. We will now see how Hive produced these three rows.'),
    ('Step 2 · Plain EXPLAIN: the DAG',
     code('sql', 'Beeline', "EXPLAIN SELECT c.city, COUNT(*) AS n, SUM(o.amount) AS rev … LIMIT 3;", plain('l81_explain.txt', 0, 10) + '\n…'),
     'Three things before any operator: the plan was <b>optimized by CBO</b>; there are four vertices; and <code>Map 1 &lt;- Map 4 (BROADCAST_EDGE)</code> means customers (Map 4) are broadcast to the tasks reading orders (Map 1): a <b>map join</b>. Reducer 2 groups by city after a shuffle, Reducer 3 sorts and keeps the top 3. The final Fetch Operator has <code>limit:3</code>.'),
    ('Step 3 · Read the operator tree bottom-up',
     code('sql', 'Beeline', "-- same EXPLAIN, the tree under Stage-1 (bottom = where data enters)", plain('l81_explain.txt', 10)),
     'From the bottom: Map 1 scans orders (50,000 rows), filters the date and NULL keys, keeps two columns, joins each row with the broadcast Gold customers, and pre-aggregates by city (map-side Group By). Rows are shuffled by city to Reducer 2 for the final count and sum; a <b>Top N Key</b> operator drops rows that cannot reach the top 3 before the last shuffle. Note <code>Col:NONE</code> on customers: no column statistics.'),
    ('Step 4 · EXPLAIN ANALYZE: estimated vs actual',
     code('sql', 'Beeline', "EXPLAIN ANALYZE SELECT c.city, COUNT(*) AS n, SUM(o.amount) AS rev … LIMIT 3;\n-- operator lines only", '\n'.join(l for l in plain('l81_analyze.txt').split('\n') if 'rows=' in l)),
     'Each operator shows <b>estimate/actual</b>. Hive expected 3 Gold customers (there are 517), 25,000 orders on 5 October (there are 1,621) and 27,500 rows after the join (there are 427). The plan was still fine here because the data is small, but estimates this wrong are exactly how real queries get the wrong join type or far too few reducers. Lesson 8.2 fixes them.'),
    ('Step 5 · EXPLAIN CBO and CBO COST: the optimiser’s view',
     code('sql', 'Beeline', "EXPLAIN CBO SELECT … ;\nEXPLAIN CBO COST SELECT … ;     -- first lines", plain('l81_cbo.txt') + '\n\n' + '\n'.join(l.split(', cumulative')[0] + (' …' if 'cumulative' in l else '') for l in plain('l81_cbocost.txt').split('\n')[1:5])),
     'This is the logical plan Apache Calcite chose before Hive turned it into Tez vertices: scans, filters, projections, the join and the aggregate. CBO COST adds row counts and cumulative cost; the CBO used its own estimates (1,991 customers, 269 Gold) which differ from the operator estimates in Step 4. Both come from statistics, at different stages of planning.'),
    ('Step 6 · The classic stage view',
     code('sql', 'Beeline', "SET hive.explain.user=false;\nEXPLAIN SELECT city, COUNT(*) FROM orders WHERE order_date = '2026-10-05' GROUP BY city;\n-- selected lines", '\n'.join(plain('l81_classic.txt').split('\n')[i] for i in [0, 1, 5, 6, 9, 12, 13, 14, 15, 16, 20, 21, 23, 24, 28, 29, 35, 38, 41, 42, 43, 44, 45, 46])),
     'With <code>hive.explain.user=false</code> Hive prints the older, more verbose format: <code>Statistics: Num rows … Basic stats: COMPLETE Column stats: COMPLETE</code> under every operator, and the Group By <b>mode</b>: <code>hash</code> on the map side, <code>mergepartial</code> on the reducer. Many blog posts and Stack Overflow answers show this format.'),
    ('Step 7 · EXPLAIN VECTORIZATION',
     code('sql', 'Beeline', "EXPLAIN VECTORIZATION ONLY SUMMARY SELECT c.city, … LIMIT 3;\n-- first lines", plain('l81_vec.txt', 0, 26) + '\n…'),
     'Both map vertices run <b>vectorised</b> (batches of rows at a time): Map 1 through the ORC vectorised reader, Map 4 by deserialising the text file into vectors. <code>allNative: false</code> means at least one operator in Map 1 uses a non-native vector implementation. Lesson 8.4 explains vectorisation in depth.'),
    ('Step 8 · EXPLAIN DEPENDENCY and EXPLAIN LOCKS',
     code('sql', 'Beeline', "EXPLAIN DEPENDENCY SELECT COUNT(*) FROM orders o JOIN customers c ON o.customer_id = c.customer_id;\nEXPLAIN LOCKS UPDATE orders_acid SET status = 'REFUNDED'\n  WHERE order_date = '2026-10-01' AND status = 'CANCELLED';", plain('l81_dep.txt') + '\n\n' + plain('l81_locks.txt')),
     'DEPENDENCY lists the tables and partitions read (here two unpartitioned external tables), useful for lineage and for checking partition pruning (Lesson 5.1). LOCKS shows that the UPDATE would take a shared read and a shared write lock on one partition only: other partitions stay free for other writers.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('> EXPLAIN SELECT c.city, COUNT(*), SUM(o.amount) …', W), ('Plan optimized by CBO.', G), ('Map 1 <- Map 4 (BROADCAST_EDGE)', G), ('Reducer 2 <- Map 1 (SIMPLE_EDGE)', G), ('Reducer 3 <- Reducer 2 (SIMPLE_EDGE)', G)], size=7.6),
    term([('TableScan [TS_3] (rows=1413 …)', W), ('  tiffingo@customers,…,Col:NONE', Y), ('Filter [FIL_25] plan = \'Gold\' (rows=3)', W), ('TableScan [TS_0] (rows=50000 …)', W), ('Filter [FIL_28] order_date = … (rows=25000)', W)], size=7.4),
    term([('Map Join Operator [MAPJOIN_30]', G), ('Group By Operator [GBY_31]  count(), sum()', G), ('SHUFFLE [RS_32] PartitionCols:_col0', G), ('Group By [GBY_33] · Top N Key [TNK_34]', G), ('Limit [LIM_37] Number of rows:3', G)], size=7.4),
    term([('> EXPLAIN ANALYZE …', W), ('Filter [FIL_25] (rows=3/517)', RD), ('Filter [FIL_28] (rows=25000/1621)', RD), ('Map Join [MAPJOIN_30] (rows=27500/427)', RD), ('Group By [GBY_33] (rows=13750/8)', Y)], size=7.4),
    term([('> EXPLAIN CBO …', W), ('HiveSortLimit(sort0=[$2], dir0=[DESC], fetch=[3])', G), ('  HiveAggregate(group=[{3}], …)', G), ('    HiveJoin(condition=[=($0, $2)], …)', G), ('      HiveFilter … HiveTableScan(orders)', G)], size=7.2),
]
def dag(hi=None):
    pos = {'Map 4': (30, 40), 'Map 1': (30, 100), 'Reducer 2': (190, 100), 'Reducer 3': (190, 40)}
    o = ''
    for name, (x, y) in pos.items():
        o += box(x, y, 120, 34, 'acc' if hi and name in hi else ('green' if name.startswith('Map') else 'blue')) + t(x + 60, y + 21, name, 8.4, bold=True)
    o += arrow(90, 74, 90, 98, 'acc', 2) + t(96, 90, 'BROADCAST', 6.6, 'acc', anchor='start', mono=True)
    o += arrow(152, 117, 188, 117, 'ink3', 2) + t(170, 112, 'shuffle', 6.4, 'ink2')
    o += arrow(250, 98, 250, 76, 'ink3', 2) + t(256, 90, 'shuffle', 6.4, 'ink2', anchor='start')
    return o
B1 = [
    t(180, 22, 'The DAG: four vertices', 9.4, bold=True) + dag() + cap('Read edges as “child &lt;- parent”.', '', 'blue', y=150, h=34),
    t(180, 22, 'Leaves: scans and filters', 9.4, bold=True) + dag(hi={'Map 4', 'Map 1'}) + cap('Data enters at the TableScans.', 'Col:NONE = no column statistics.', 'amber', y=150, h=46),
    t(180, 22, 'Join on the map side, group in two phases', 9.4, bold=True) + opbox(20, 42, 'Map Join', 'probe broadcast table', 'green', 150) + opbox(20, 74, 'Group By (hash)', 'partial per task', 'green', 150) +
    arrow(172, 87, 200, 87, 'ink3') + opbox(200, 74, 'Group By (merge)', 'final per city', 'blue', 140) + opbox(200, 42, 'Top N Key · Limit', 'keep top 3', 'blue', 140) + cap('Fewer rows travel at each step.', '', 'green', y=150, h=34),
    t(180, 22, 'Estimates vs reality', 9.4, bold=True) + ''.join(t(30, 54 + k * 20, s, 8, 'ink', anchor='start', mono=True) + fill(190, 44 + k * 20, max(2, round(140 * e / 27500)), 6, 'blue', rx=1) + fill(190, 51 + k * 20, max(2, round(140 * a / 27500)), 6, 'acc', rx=1) for k, (s, e, a) in enumerate([('Gold customers', 3, 517), ('orders on 10-05', 25000, 1621), ('after join', 27500, 427), ('groups', 13750, 8)])) +
    cap('blue = estimate · orange = actual', 'Wrong estimates → wrong join and reducer choices.', 'amber', y=150, h=46),
    t(180, 22, 'Two layers of planning', 9.4, bold=True) + opbox(30, 46, 'SQL → AST', '', 'card', 90) + arrow(122, 59, 138, 59, 'ink3') + opbox(140, 46, 'CBO (Calcite)', 'logical plan', 'violet', 100) + arrow(242, 59, 258, 59, 'ink3') + opbox(260, 46, 'Tez DAG', 'operators', 'green', 80) +
    cap('EXPLAIN CBO shows the middle, EXPLAIN the right.', '', 'blue', y=150, h=34),
]
see_caps = ['The plan starts with the vertex dependencies: four Tez vertices.',
            'At the bottom, the scans and filters, with row estimates.',
            'The join, the two-phase aggregation and the top-3 limit.',
            'EXPLAIN ANALYZE shows estimates that are far from reality.',
            'EXPLAIN CBO shows the logical plan chosen by Calcite.']
behind_caps = ['Map vertices read files; reducers receive shuffled rows; the broadcast edge copies a small input to every task.',
               'Data enters at the TableScans; filters are pushed as close to the scans as possible.',
               'The map join probes a hash table; partial aggregates shrink data before the shuffle.',
               'Estimates come from statistics; missing or uniform-assumption stats produce big errors.',
               'Hive parses SQL, Calcite optimises the logical plan, then Hive builds the physical Tez plan.']
two = anim_two('EXPLAIN', 'From SQL to a Tez DAG', 'Real EXPLAIN output', 'How to read the plan', see, B1, see_caps, behind_caps)

# ---- scenario 1: slow report triage
r1 = (t(180, 22, 'A daily report went from 2 to 20 minutes', 9.4, bold=True) + t(180, 56, 'first step: EXPLAIN, not guessing', 8.4, 'ink2') + cap('Save yesterday’s plan to compare.', '', 'blue', y=150, h=34))
r2 = (t(180, 22, 'Diff the plans', 9.4, bold=True) + t(180, 52, 'yesterday: Map 1 &lt;- Map 3 (BROADCAST_EDGE)', 7.8, 'green', mono=True) + t(180, 70, 'today:     Reducer 2 &lt;- Map 1, Map 3 (SIMPLE_EDGE)', 7.8, 'red', mono=True) + cap('The map join became a shuffle join.', '(illustrative)', 'amber', y=150, h=46))
r3 = (t(180, 22, 'Why? Check the estimates', 9.4, bold=True) + t(180, 56, 'small table now estimated far larger than reality', 8.2, 'ink2') + cap('Stale or missing statistics.', '', 'amber', y=150, h=34))
r4 = (t(180, 22, 'Fix the cause', 9.4, bold=True) + t(180, 56, 'ANALYZE TABLE … COMPUTE STATISTICS FOR COLUMNS', 8, 'ink', mono=True) + cap('Lesson 8.2.', '', 'green', y=150, h=34))
r5 = (t(180, 22, 'Keep plans in version control', 9.4, 'acc', bold=True) + t(180, 56, 'store EXPLAIN output of key jobs', 8.4, 'ink2') + cap('Plan changes become visible.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'A report suddenly ten times slower',
              'A typical investigation that starts and ends with EXPLAIN. (Illustrative plans.)',
              'Plan regression', 'Comparing today’s plan with yesterday’s shows a map join turned into a shuffle join because of wrong statistics', [r1, r2, r3, r4, r5],
              ['Start by capturing the plan.',
               'Comparing plans reveals the changed join strategy.',
               'Wrong estimates explain why the optimiser changed its mind.',
               'Refresh statistics.',
               'Keep plans of critical jobs to spot regressions.'],
              hid='scenario-regression')

# ---- scenario 2: EXPLAIN ANALYZE caution
a1 = (t(180, 22, 'EXPLAIN ANALYZE runs the query', 9.4, bold=True) + t(180, 56, 'on a 5 TB table that is a full job', 8.4, 'red') + cap('Do not run it casually on production data.', '', 'amber', y=150, h=34))
a2 = (t(180, 22, 'Shrink first', 9.4, bold=True) + t(180, 56, 'one partition, a TABLESAMPLE, or a staging copy', 8.2, 'ink2') + cap('Estimates errors show up on samples too.', '', 'green', y=150, h=34))
a3 = term([('Filter [FIL_25] (rows=3/517)', RD), ('Filter [FIL_28] (rows=25000/1621)', RD)], label='real output · Hive 4.2.1')
a4 = (t(180, 22, 'Also: Tez counters', 9.4, bold=True) + t(180, 56, 'SET hive.tez.exec.print.summary=true;', 8.2, 'ink', mono=True) + cap('Actual rows per vertex for the real run.', '', 'blue', y=150, h=34))
a5 = (t(180, 22, 'Rule', 9.4, 'acc', bold=True) + t(180, 56, 'EXPLAIN always · ANALYZE on samples · counters on runs', 8, 'ink2') + cap('Cheap to expensive.', '', 'green', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Using EXPLAIN ANALYZE safely',
              'EXPLAIN ANALYZE gives the best information but executes the query. Our output is real.',
              'EXPLAIN ANALYZE', 'Because EXPLAIN ANALYZE executes the query, run it on samples or single partitions and use Tez counters for real runs', [a1, a2, a3, a4, a5],
              ['EXPLAIN ANALYZE is a real run.',
               'Use a partition or sample to keep it cheap.',
               'Estimate/actual pairs show where statistics are wrong.',
               'Tez counters give actuals for normal runs too.',
               'Use the cheapest tool that answers your question.'],
              hid='scenario-analyze')

# ---- scenario 3: code review checklist
c1 = (t(180, 22, 'Code review: EXPLAIN checklist', 9.4, bold=True) + t(180, 56, 'before a new job goes to production', 8.4, 'ink2') + cap('Five questions, five minutes.', '', 'blue', y=150, h=34))
c2 = (t(180, 22, '1 · Are partitions pruned?', 9.4, bold=True) + t(180, 56, 'EXPLAIN DEPENDENCY → input_partitions', 8.4, 'ink', mono=True) + cap('Lesson 5.1.', '', 'green', y=150, h=34))
c3 = (t(180, 22, '2 · Which join type? 3 · Stats complete?', 9.4, bold=True) + t(180, 56, 'BROADCAST_EDGE or SIMPLE_EDGE · Col:COMPLETE?', 8.2, 'ink', mono=True) + cap('Lessons 8.2 and 8.3.', '', 'green', y=150, h=34))
c4 = (t(180, 22, '4 · Vectorised? 5 · Big shuffles?', 9.4, bold=True) + t(180, 56, 'Execution mode: vectorized · estimated rows into reducers', 7.8, 'ink', mono=True) + cap('Lessons 8.4 and 8.5.', '', 'green', y=150, h=34))
c5 = (t(180, 22, 'Attach the plan to the review', 9.4, 'acc', bold=True) + t(180, 56, 'reviewers read plans, not just SQL', 8.4, 'ink2') + cap('Many slow jobs are caught here.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'An EXPLAIN checklist for code reviews',
              'A practical checklist that ties this module together. (Typical team practice.)',
              'Plan review', 'Before deployment, check pruning, join type, statistics, vectorisation and shuffle size in the plan', [c1, c2, c3, c4, c5],
              ['Review the plan as well as the SQL.',
               'Check partition pruning.',
               'Check join type and statistics.',
               'Check vectorisation and shuffles.',
               'Attach plans to code reviews.'],
              hid='scenario-review')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Reading a real plan</h2>
  <p>Left: real EXPLAIN output. Right: how to read it.</p>
''' + two + '''
  <p>Three live scenarios follow: a plan regression, EXPLAIN ANALYZE safely, and a review checklist.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>EXPLAIN at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'EXPLAIN', 11, 'green', bold=True, mono=True) + t(60, 58, 'first step', 7.4, 'ink2'),
    '1. Performance investigations',
    'Platform teams ask for the EXPLAIN output before looking at any slow-query complaint; most problems are visible in the plan.',
    ['Slow query', '*EXPLAIN', 'Root cause']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'review', 11, 'blue', bold=True) + t(60, 58, 'before deploy', 7.4, 'ink2'),
    '2. Code review of pipelines',
    'Plans of new ETL jobs are reviewed for pruning, join strategy and shuffle size before they reach production.',
    ['New job', '*plan review', 'Safe deploy']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'upgrade', 11, 'violet', bold=True) + t(60, 58, 'plan diffs', 7.4, 'ink2'),
    '3. Upgrades and migrations',
    'Before upgrading Hive, teams capture plans of critical queries on the old and new versions and compare them.',
    ['Old plans', '*diff', 'No surprises']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'DEPENDENCY', 9, 'acc', bold=True, mono=True) + t(60, 58, 'lineage', 7.4, 'ink2'),
    '4. Lineage and impact analysis',
    'EXPLAIN DEPENDENCY output tells which tables and partitions a report reads, helping governance and change planning.',
    ['Report SQL', '*inputs list', 'Lineage']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'LOCKS', 11, 'acc', bold=True, mono=True) + t(60, 58, 'concurrency', 7.4, 'ink2'),
    '5. Planning concurrent writes',
    'EXPLAIN LOCKS shows whether two ACID jobs would block each other, so they can be scheduled or partitioned apart.',
    ['Two jobs', '*lock check', 'No blocking']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> recall how a query becomes a job (<a href="../../01-introduction/04-how-a-hive-query-becomes-a-job/">1.4</a>), joins (<a href="../../03-querying/03-joins/">3.3</a>) and GROUP BY (<a href="../../03-querying/02-group-by-and-grouping-sets/">3.2</a>).</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
