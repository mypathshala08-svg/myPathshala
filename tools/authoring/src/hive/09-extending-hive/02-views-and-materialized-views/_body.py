import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return re.sub(r'; Query ID[^\n]*', '', open(CAP + n).read().rstrip())
def plain(n):
    lines = [l for l in capf(n).split('\n') if l.startswith('| ')]
    lines = [re.sub(r'\s*\|$', '', l[2:]).rstrip() for l in lines]
    return '\n'.join(l for l in lines if l.strip() not in ('Explain',)).strip('\n')
def grepl(n, keys):
    return '\n'.join(l for l in capf(n).split('\n') if any(k in l for k in keys))
def rows(n):
    """Last result table in a capture (skips EXPLAIN output)."""
    blocks, cur = [], []
    for l in capf(n).split('\n'):
        if l.startswith(('+', '|')):
            cur.append(l)
        elif cur:
            blocks.append(cur); cur = []
    if cur:
        blocks.append(cur)
    # split concatenated tables: a new table starts at a '+' line followed by a header after a closing '+'
    tables, t_ = [], []
    for b in blocks:
        for i, l in enumerate(b):
            t_.append(l)
            if l.startswith('+') and i + 1 < len(b) and b[i + 1].startswith('+'):
                tables.append(t_); t_ = []
        tables.append(t_); t_ = []
    good = [t_ for t_ in tables if t_ and not any('Explain' in x or 'Hive' in x or 'CBO PLAN' in x for x in t_) and any(x.startswith('| ') and x.strip('| ') for x in t_)]
    return '\n'.join(good[-1]) if good else ''
def squeeze(s):
    return re.sub(r' {3,}', '   ', s)

def opbox(x, y, label, sub='', tone='card', w=128, h=26):
    o = box(x, y, w, h, tone) + t(x + w / 2, y + (11 if sub else 16), label, 7.2, 'ink', bold=True)
    if sub:
        o += t(x + w / 2, y + 21, sub, 6.4, 'ink2', mono=True)
    return o

# ---------------------------------------------------------------- story
sc = (box(10, 12, 190, 128, 'card') + t(105, 30, 'Same join in 12 reports', 8.8, bold=True) +
      ''.join(t(22, 52 + k * 15, s, 7.2, 'ink2', anchor='start', mono=True) for k, s in enumerate(['orders JOIN customers', "WHERE plan = 'Gold'", 'GROUP BY city, day', '… copied 12 times', '5,000,000 rows each run'])) +
      arrow(206, 76, 246, 76, 'acc', 2.2) + box(252, 30, 110, 40, 'blue') + t(307, 54, 'VIEW', 9, bold=True) + box(252, 82, 110, 40, 'violet') + t(307, 106, 'MATERIALIZED VIEW', 7.2, bold=True) +
      arrow(368, 76, 404, 76, 'acc', 2.2) + box(410, 12, 220, 128, 'green') + t(520, 30, 'What each gives', 8.8, 'green', bold=True) +
      opbox(422, 42, 'View: one definition', 'no data stored', 'blue', 196) + opbox(422, 76, 'MV: stored result', '240 rows instead of 5M', 'violet', 196) + opbox(422, 108, 'Rewriting', 'queries use the MV by themselves', 'green', 196))
scene_svg = scene('The same join and aggregation is copied into twelve reports. A view stores the definition once; a materialized view stores the result, and Hive can rewrite queries to read it automatically.', sc,
                  'A view saves <tspan font-weight="700" class="s-acc">typing</tspan>; a materialized view saves <tspan font-weight="700" class="s-acc">work</tspan>.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Twelve reports, one join, copied twelve times”</h2>
  <div class="story">
    <p class="narration">Every TiffinGo report starts with the same join of orders and customers and the same daily totals by city. When the definition of a “Gold order” changed last month, Kabir had to fix twelve copies, and missed two.</p>

{scene_svg}

K> Sir, can I write the join once and let reports use it like a table?
A> That is a <b>view</b>: a saved query with a name. It stores no data; Hive pastes its definition into every query that uses it. If the work itself is expensive, a <b>materialized view</b> stores the result as a real table, and Hive 4 can even <b>rewrite</b> queries on the base table to read it, without changing the reports.
R> And when new orders arrive?
A> Then the materialized view is <b>stale</b>. We will see exactly what Hive does about that: refuse to use it, use it anyway inside a time window, and rebuild it incrementally or fully. All outputs are real, from Hive 4.2.1, including a few rules the tutorials leave out.
  </div>
</section>
'''

lv = '''
LEVELS> Views at three levels
L1> A saved recipe vs a cooked dish
      <ul>
        <li>A <b>view</b> is a saved recipe: every time you use it, Hive cooks the query again from the base tables.</li>
        <li>A <b>materialized view</b> is a cooked dish kept in the fridge: fast to serve, but it gets old when new ingredients arrive.</li>
        <li>Both let many reports share one definition.</li>
      </ul>
L2> How they behave
      <ul>
        <li><code>CREATE VIEW v AS SELECT …</code>: stored in the metastore as text (<code>VIRTUAL_VIEW</code>); queries on <code>v</code> are expanded into the base query. No data, always current.</li>
        <li><code>CREATE MATERIALIZED VIEW mv AS SELECT …</code>: stores the result (ORC, transactional) and its source tables’ snapshot.</li>
        <li><b>Rewriting:</b> with <code>hive.materializedview.rewriting=true</code>, Calcite replaces matching parts of a query with the MV.</li>
        <li><b>Refresh:</b> <code>ALTER MATERIALIZED VIEW mv REBUILD</code>, incremental when possible.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li><code>SELECT *</code> views freeze the column list at creation; dropping the base table broke the view only when it was queried.</li>
        <li>An MV with rewriting was refused on an external source (“cannot be enabled if the materialized view uses non-transactional tables”); <code>DISABLE REWRITE</code> worked.</li>
        <li>Rewriting read 240 rows instead of 5,000,000. After an INSERT the stale MV was ignored; a 10-minute window made Hive use it and return an <b>outdated</b> total. Incremental rebuild after INSERT, full rebuild after DELETE.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Views and materialized views</h2>
''' + def_block(
    'A <b>view</b> is a named, stored query (<code>CREATE VIEW name AS SELECT …</code>) recorded in the metastore as a <code>VIRTUAL_VIEW</code>; it holds no data, and references to it are expanded into the underlying query at compile time. A <b>materialized view</b> (<code>CREATE MATERIALIZED VIEW</code>) stores the query result as a managed table and records the state of its source tables. When the sources are transactional, the cost-based optimiser can <b>automatically rewrite</b> queries to use an up-to-date materialized view (<code>hive.materializedview.rewriting</code>), and <code>ALTER MATERIALIZED VIEW … REBUILD</code> refreshes it, incrementally when only inserts occurred since the last rebuild.',
    'A view is a saved query you can select from like a table; it always shows current data. A materialized view saves the query’s result, so reading it is fast, but it must be rebuilt when the source data changes. Hive can use a materialized view automatically to speed up queries on the base tables.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('View', 'A stored query; no data; expanded at compile time.'),
    ('Materialized view (MV)', 'A stored query result, kept as a table.'),
    ('Query rewriting', 'The optimiser replaces part of a query with an MV.'),
    ('Stale / outdated', 'Sources changed since the MV was last built.'),
    ('Rebuild', 'ALTER MATERIALIZED VIEW … REBUILD: refresh the stored result.'),
    ('Incremental rebuild', 'Merge only the new rows into the MV.'),
    ('Time window', 'How long a stale MV may still be used for rewriting.'),
    ('Results cache', 'Hive 4 reuses the result of an identical earlier query.'),
]) + '''

  <h3>View vs materialized view vs table</h3>
''' + table(['', 'View', 'Materialized view', 'Table (CTAS)'], [
    ['Stores data', 'No', 'Yes', 'Yes'],
    ['Always current', 'Yes', 'Only after REBUILD', 'Only after reload'],
    ['Used automatically by other queries', 'No', 'Yes (rewriting)', 'No'],
    ['Source requirements', 'Any', 'Transactional for rewriting', 'Any'],
    ['Refresh', '—', 'REBUILD (incremental or full)', 'INSERT OVERWRITE'],
    ['Good for', 'Reuse, security, simplicity', 'Expensive repeated aggregates', 'Snapshots, ETL steps'],
], minw=700) + lv + '''
EXAM> “Difference between a view and a materialized view in Hive?” A view stores only the query and is expanded when used, so it is always current but saves no work. A materialized view stores the result, needs REBUILD after source changes, and with transactional sources can be used automatically by the optimiser through query rewriting.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Commands and settings</h2>
''' + table(['Statement / setting', 'Purpose'], [
    ['<code>CREATE [OR REPLACE] VIEW v [(cols)] AS SELECT …</code>', 'Define a view'],
    ['<code>ALTER VIEW v AS SELECT …</code> · <code>DROP VIEW v</code>', 'Change or remove it'],
    ['<code>SHOW VIEWS</code> · <code>SHOW CREATE TABLE v</code>', 'List views; see the stored text'],
    ['<code>CREATE MATERIALIZED VIEW mv [DISABLE REWRITE] AS SELECT …</code>', 'Store a result'],
    ['<code>ALTER MATERIALIZED VIEW mv REBUILD</code>', 'Refresh'],
    ['<code>ALTER MATERIALIZED VIEW mv ENABLE | DISABLE REWRITE</code>', 'Allow automatic use'],
    ['<code>SHOW MATERIALIZED VIEWS</code>', 'Name, rewrite, mode, incremental'],
    ['<code>hive.materializedview.rewriting</code> (true)', 'Global switch for rewriting'],
    ['<code>hive.materializedview.rewriting.time.window</code> (0min)', 'Allowed staleness for rewriting'],
    ['<code>hive.materializedview.rebuild.incremental</code> (true)', 'Try incremental rebuilds'],
], minw=680) + '''
WARN> Hive 4 also has a <b>query results cache</b> (<code>hive.query.results.cache.enabled=true</code>): an identical query on unchanged transactional tables returned in <b>0.0 s</b> in our lab. Turn it off when you measure, or every second run looks miraculous.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>From a view to a self-refreshing summary</h2>
  <p>All outputs are real, from Hive 4.2.1. <code>orders_tx</code> is a transactional copy of the 5,000,000-row table from Lesson 8.4.</p>
''' + stepper([
    ('Step 1 · A view for Gold orders',
     code('sql', 'Beeline', "CREATE OR REPLACE VIEW v_gold_orders AS\nSELECT o.order_id, o.order_date, o.amount, c.city, c.customer_id\nFROM orders o JOIN customers c ON o.customer_id = c.customer_id\nWHERE c.plan = 'Gold';\n\nSELECT city, COUNT(*) AS n, SUM(amount) AS rev FROM v_gold_orders\nWHERE order_date = '2026-10-05' GROUP BY city ORDER BY rev DESC LIMIT 3;", capf('l92_view.txt')),
     'Exactly the answer of Lesson 8.1’s long query (Bengaluru 100, Mumbai 71, Pune 60), now with a two-line report. The definition of “Gold order” lives in one place.'),
    ('Step 2 · What Hive stored, and what it reads',
     code('sql', 'Beeline', "SHOW CREATE TABLE v_gold_orders;\nDESCRIBE FORMATTED v_gold_orders;   -- table type\nEXPLAIN DEPENDENCY SELECT COUNT(*) FROM v_gold_orders;", capf('l92_viewshow.txt') + '\n' + squeeze(grepl('l92_viewdesc.txt', ('Table Type',))) + '\n\n' + plain('l92_viewplan.txt')),
     'Hive stored the <b>expanded</b> text: every column qualified, the database added. The table type is <code>VIRTUAL_VIEW</code>. The query really reads <code>orders</code> and <code>customers</code>, listed with <code>tableParents: v_gold_orders</code>, which is handy for lineage and for granting access to the view without the base tables.'),
    ('Step 3 · Two view traps: SELECT * and dropped tables',
     code('sql', 'Beeline', "CREATE TABLE cust_copy STORED AS ORC AS SELECT customer_id, name, city FROM customers;\nCREATE VIEW v_cust_all AS SELECT * FROM cust_copy;\nALTER TABLE cust_copy ADD COLUMNS (plan STRING);\nDESCRIBE cust_copy;\nDESCRIBE v_cust_all;\nSHOW CREATE TABLE v_cust_all;\n\nDROP TABLE cust_copy;\nSELECT * FROM v_cust_all LIMIT 1;", capf('l92_star.txt') + '\n\n' + capf('l92_broken.txt')),
     '<code>SELECT *</code> was expanded into three named columns at creation, so the new <code>plan</code> column never appears in the view. Dropping the base table succeeded silently; the view only failed when someone queried it. List columns explicitly in views, and check dependent views (EXPLAIN DEPENDENCY, lineage tools) before dropping tables.'),
    ('Step 4 · Materialized views need transactional sources',
     code('sql', 'Beeline', "CREATE MATERIALIZED VIEW mv_ext AS SELECT city, COUNT(*) AS n FROM orders GROUP BY city;   -- orders is external\n\nCREATE MATERIALIZED VIEW mv_ext DISABLE REWRITE AS SELECT city, COUNT(*) AS n FROM orders GROUP BY city;\nSHOW MATERIALIZED VIEWS;", capf('l92_mv_ext.txt') + '\n\n' + rows('l92_mv_ext2.txt')),
     'Hive refused automatic rewriting on an external source: it cannot know when external files change, so it could never tell whether the MV is up to date. With <code>DISABLE REWRITE</code> the MV was created, but only as a stored result you query by name, with “Manual refresh” and incremental rebuild “Not available”.'),
    ('Step 5 · An MV on a transactional table, and rewriting',
     code('sql', 'Beeline', "CREATE MATERIALIZED VIEW mv_city_day AS\nSELECT city, order_date, COUNT(*) AS n, SUM(amount) AS rev\nFROM orders_tx GROUP BY city, order_date;\nSHOW MATERIALIZED VIEWS;\nSELECT COUNT(*) AS mv_rows FROM mv_city_day;\n\n-- a report written against the BASE table:\nEXPLAIN CBO SELECT city, SUM(amount) AS rev, COUNT(*) AS n FROM orders_tx\nWHERE order_date BETWEEN '2026-10-01' AND '2026-10-07' GROUP BY city ORDER BY rev DESC LIMIT 3;", capf('l92_mv_create.txt') + '\n\n' + plain('l92_rewrite_cbo.txt')),
     '5,000,000 orders became <b>240 rows</b> (8 cities × 30 days). The report never mentions the MV, yet the plan scans <code>mv_city_day</code>: Calcite proved the query can be answered from it, rolled the daily totals up to cities, and turned <code>COUNT(*)</code> into <code>SUM(n)</code> (the <code>COALESCE(…, 0)</code> keeps empty groups at 0).'),
    ('Step 6 · Same answer, far fewer rows',
     code('sql', 'Beeline', "SET hive.query.results.cache.enabled=false;   -- measure honestly\nSET hive.tez.exec.print.summary=true;\n-- the same report with hive.materializedview.rewriting=true, then false", capf('l92_result.txt') + '\n\n' + capf('l92_records.txt') + '\n\n' + capf('l92_times.txt')),
     'Identical results with and without the MV (we compared them). The MV run read <b>240</b> rows instead of <b>5,000,000</b>. On our single-node lab both ran in about 1 second, because 5 million ORC rows are cheap and start-up dominates; on billions of rows or with joins in the MV, the difference becomes minutes.'),
    ('Step 7 · Staleness: correct by default, stale by choice',
     code('sql', 'Beeline', "INSERT INTO orders_tx VALUES (999000001, 7, 'Pune', 1000.00, DATE '2026-10-03', 'DELIVERED');\nEXPLAIN CBO SELECT … ;                                -- same report\nDESCRIBE FORMATTED mv_city_day;                        -- after a second insert\n\nSET hive.materializedview.rewriting.time.window=10min;\nSELECT … ;                                             -- uses the MV\nSET hive.materializedview.rewriting.time.window=0min;\nSELECT … ;                                             -- base table", grepl('l92_stale_cbo.txt', ('HiveTableScan',)) + '\n' + squeeze(grepl('l92_outdated.txt', ('Outdated',))) + '\n\n-- with a 10-minute window:\n' + grepl('l92_window.txt', ('HiveTableScan',)) + '\n' + rows('l92_window.txt') + '\n\n-- fresh (base table):\n' + rows('l92_fresh.txt')),
     'After the insert, Hive marked the MV <b>Outdated for Rewriting</b> and quietly went back to <code>orders_tx</code>: correct, but slow again. With a 10-minute staleness window it used the MV anyway and returned Pune <b>176,200</b> orders and 52,265,000, while the truth was <b>176,201</b> and 52,266,000. A window is a deliberate trade of freshness for speed; agree on it with the report’s owners.'),
    ('Step 8 · Rebuild: incremental after INSERT, full after DELETE',
     code('sql', 'Beeline', "EXPLAIN CBO ALTER MATERIALIZED VIEW mv_city_day REBUILD;     -- after the INSERT\nALTER MATERIALIZED VIEW mv_city_day REBUILD;\n\nDELETE FROM orders_tx WHERE order_id = 999000001;\nEXPLAIN CBO ALTER MATERIALIZED VIEW mv_city_day REBUILD;     -- after the DELETE\nALTER MATERIALIZED VIEW mv_city_day REBUILD;", '-- after INSERT\n' + plain('l92_rebuild_plan.txt') + '\n\n-- after DELETE\n' + plain('l92_rebuild_del_plan.txt') + '\n\n' + capf('l92_rebuild.txt')),
     'After an INSERT, the rebuild plan is <b>incremental</b>: aggregate only rows with a newer <code>writeid</code> than the last build, UNION them with the existing MV rows and re-aggregate. After a DELETE it is a <b>full</b> recomputation. In our lab both still scanned all 5,000,000 rows of <code>orders_tx</code> (the writeid filter is applied after reading) and took about 2.1 s; the incremental one saved the aggregation work, not the scan.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('> SELECT … FROM v_gold_orders …', W), ('Bengaluru  100  26600.00', G), ('Table Type: VIRTUAL_VIEW', Y), ('input: orders, customers', W), ('  tableParents: v_gold_orders', W)], size=7.4),
    term([('ALTER TABLE cust_copy ADD COLUMNS (plan)', W), ('DESCRIBE v_cust_all: 3 columns', Y), ('DROP TABLE cust_copy;   -- OK', W), ("Table not found 'cust_copy'", RD), ('  in definition of VIEW v_cust_all', RD)], size=7.2),
    term([('CREATE MATERIALIZED VIEW … FROM orders', W), ('cannot be enabled if the MV uses', RD), ('  non-transactional tables', RD), ('mv_city_day  Yes  Manual refresh', G), ('mv_rows 240', G)], size=7.4),
    term([('HiveTableScan(table=[[tiffingo, mv_city_day]])', G), ('rewriting=true   RECORDS_IN 240', G), ('rewriting=false  RECORDS_IN 5000000', Y), ('same result', G)], size=7.2),
    term([('Outdated for Rewriting: Yes', Y), ('window 10min → Pune 176200 (stale)', RD), ('fresh        → Pune 176201', G), ('INSERT → incremental rebuild (UNION)', G), ('DELETE → full rebuild', Y)], size=7.2),
]
def lanes(mode):
    o = opbox(20, 50, 'orders + customers' if mode == 'view' else 'orders_tx', 'base tables' if mode == 'view' else '5,000,000 rows', 'card', 110)
    o += opbox(230, 50, 'report', 'GROUP BY city', 'blue', 110)
    if mode == 'view':
        o += arrow(132, 63, 228, 63, 'ink3', 1.8) + t(180, 56, 'expand', 7, 'ink2')
    else:
        o += opbox(120, 100, 'mv_city_day', '240 rows', 'violet' if mode != 'stale' else 'amber', 110)
        o += arrow(75, 76, 120, 108, 'ink3', 1.4)
        o += arrow(232, 113, 285, 76, 'green' if mode == 'mv' else 'red', 1.8)
    return o
B1 = [
    t(180, 22, 'A view is expanded into the query', 9.4, bold=True) + lanes('view') + cap('No data stored; always current.', '', 'blue', y=150, h=34),
    t(180, 22, 'Views store text, not data', 9.4, bold=True) + opbox(40, 56, 'metastore', 'expanded SQL', 'green', 120) + opbox(200, 56, 'base table', 'dropped', 'red', 120) + cap('Errors appear only when the view is used.', '', 'amber', y=150, h=34),
    t(180, 22, 'MV: a stored, transactional result', 9.4, bold=True) + lanes('mv') + cap('Hive knows the source snapshot it was built from.', '', 'violet', y=150, h=34),
    t(180, 22, 'Rewriting: the optimiser picks the MV', 9.4, bold=True) + lanes('mv') + cap('Report unchanged; 240 rows read instead of 5M.', '', 'green', y=150, h=34),
    t(180, 22, 'New rows make the MV stale', 9.4, bold=True) + lanes('stale') + cap('Ignored by default; REBUILD to refresh.', 'A time window allows stale answers.', 'amber', y=140, h=46),
]
see_caps = ['A view gave the same answer as the long query.',
            'A SELECT * view froze its columns, then broke when its table was dropped.',
            'An MV on an external table was refused; on a transactional one it worked.',
            'Rewriting read 240 rows instead of 5,000,000.',
            'Stale MVs: ignored, used inside a window, rebuilt incrementally or fully.']
behind_caps = ['References to a view are replaced by its stored query.',
               'Only the expanded SQL is stored; nothing tracks dependents.',
               'The MV records which transactions of its sources it contains.',
               'Calcite proves the query can be answered from the MV.',
               'New write IDs in the sources mark the MV as outdated.']
two = anim_two('Views and MVs', 'Reuse a query, or reuse its result', 'Real lab outputs', 'What Hive does', see, B1, see_caps, behind_caps)

# ---- scenario 1: dashboard acceleration
d1 = (t(180, 22, 'Daily sales dashboard: 40 tiles', 9.4, bold=True) + t(180, 56, 'all group a 2 TB orders table by city and day', 8, 'ink2') + cap('Same aggregation, 40 times.', '', 'blue', y=150, h=34))
d2 = (t(180, 22, 'One MV at the finest grain needed', 9.4, bold=True) + t(180, 56, 'GROUP BY city, order_date, plan', 8.2, 'ink', mono=True) + cap('Coarser queries roll up from it.', '', 'green', y=150, h=34))
d3 = (t(180, 22, 'Tiles keep their SQL', 9.4, bold=True) + t(180, 56, 'rewriting reads the MV automatically', 8.2, 'ink2') + cap('Check with EXPLAIN CBO.', '', 'green', y=150, h=34))
d4 = (t(180, 22, 'Rebuild after each load', 9.4, bold=True) + t(180, 56, 'ALTER MATERIALIZED VIEW … REBUILD', 8.2, 'ink', mono=True) + cap('Insert-only loads → incremental.', '', 'blue', y=150, h=34))
d5 = (t(180, 22, 'Agree on freshness', 9.4, 'acc', bold=True) + t(180, 56, 'window 0 = always correct · 15min = faster', 8, 'ink2') + cap('A business decision, not a default.', '', 'amber', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Accelerating a dashboard without touching it',
              'A common use of MVs. (Sizes illustrative; behaviour as in our lab.)',
              'MV for dashboards', 'One materialized view at the finest grain serves many dashboard queries through rewriting, rebuilt after each load', [d1, d2, d3, d4, d5],
              ['Many tiles share one aggregation.',
               'Build an MV at the finest grain.',
               'Rewriting needs no SQL changes.',
               'Rebuild after loads.',
               'Decide how stale answers may be.'],
              hid='scenario-dashboard')

# ---- scenario 2: views for security
v1 = (t(180, 22, 'Analysts must not see phone numbers', 9.4, bold=True) + t(180, 56, 'customers has name, phone, city, plan', 8.4, 'ink2') + cap('Hide columns, keep the data useful.', '', 'blue', y=150, h=34))
v2 = (t(180, 22, 'A view without the sensitive column', 9.4, bold=True) + t(180, 56, 'CREATE VIEW v_customers AS SELECT customer_id, city, plan …', 7.2, 'ink', mono=True) + cap('Or mask it: mask(phone).', '', 'green', y=150, h=34))
v3 = (t(180, 22, 'Grant the view, not the table', 9.4, bold=True) + t(180, 56, 'GRANT SELECT ON v_customers TO ROLE analyst', 7.8, 'ink', mono=True) + cap('Authorization in Lesson 10.2.', '', 'green', y=150, h=34))
v4 = (t(180, 22, 'Name columns explicitly', 9.4, bold=True) + t(180, 56, 'SELECT * would freeze — and expose — columns', 8, 'ink2') + cap('Lab: SELECT * froze the column list.', '', 'amber', y=150, h=34))
v5 = (t(180, 22, 'Larger platforms: Ranger', 9.4, 'acc', bold=True) + t(180, 56, 'column masking and row filters as policies', 8, 'ink2') + cap('Policies instead of many views.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Views as a security layer',
              'Views hide columns and rows. (Typical practice; Lesson 10.2 covers authorization.)',
              'Secure views', 'A view exposes only allowed columns and rows; analysts get access to the view, not the table', [v1, v2, v3, v4, v5],
              ['Some columns are sensitive.',
               'Create a view without them.',
               'Grant access to the view only.',
               'Avoid SELECT * in views.',
               'Ranger policies scale this up.'],
              hid='scenario-secure')

# ---- scenario 3: why is the MV not used?
w1 = (t(180, 22, '“The MV exists but queries are still slow”', 9.4, bold=True) + t(180, 56, 'EXPLAIN CBO shows the base table', 8.4, 'red', mono=True) + cap('Rewriting did not happen.', '', 'amber', y=150, h=34))
w2 = (t(180, 22, 'Check 1: outdated?', 9.4, bold=True) + t(180, 56, 'DESCRIBE FORMATTED mv → Outdated for Rewriting: Yes', 7.6, 'ink', mono=True) + cap('Rebuild, or allow a window.', '', 'blue', y=150, h=34))
w3 = (t(180, 22, 'Check 2: rewrite enabled?', 9.4, bold=True) + t(180, 56, 'SHOW MATERIALIZED VIEWS · global setting', 8.2, 'ink', mono=True) + cap('DISABLE REWRITE MVs are never used.', '', 'blue', y=150, h=34))
w4 = (t(180, 22, 'Check 3: can the query be derived?', 9.4, bold=True) + t(180, 56, 'needs columns / grain the MV dropped?', 8.2, 'ink2') + cap('An MV by city cannot answer by customer.', '', 'amber', y=150, h=34))
w5 = (t(180, 22, 'Check 4: non-deterministic parts', 9.4, 'acc', bold=True) + t(180, 56, 'current_date(), rand() in the query', 8.2, 'ink2') + cap('Rewrite skipped for safety.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Why is my materialized view not used?',
              'A checklist for rewriting problems. (The first two checks are from our lab.)',
              'MV troubleshooting', 'Check staleness, rewrite flags, whether the query is derivable from the MV, and non-deterministic functions', [w1, w2, w3, w4, w5],
              ['The plan shows the base table.',
               'Is the MV outdated?',
               'Is rewriting enabled for it?',
               'Can the MV answer this query at all?',
               'Non-deterministic functions block rewriting.'],
              hid='scenario-notused')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Reusing queries and results</h2>
  <p>Left: real outputs. Right: what Hive does.</p>
''' + two + '''
  <p>Three live scenarios follow: dashboard acceleration, views for security, and an MV that is not used.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Views and MVs at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'semantic', 10, 'green', bold=True) + t(60, 58, 'layer', 7.4, 'ink2'),
    '1. A semantic layer',
    'Views give business names and agreed definitions (“active customer”, “Gold order”) on top of raw tables.',
    ['Raw tables', '*views', 'Shared metrics']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'secure', 11, 'blue', bold=True) + t(60, 58, 'columns', 7.4, 'ink2'),
    '2. Column and row restriction',
    'Views without personal columns, or filtered to one region, are granted to analysts instead of base tables.',
    ['Table', '*restricted view', 'Safe access']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'MV', 12, 'violet', bold=True, mono=True) + t(60, 58, 'BI speed', 7.4, 'ink2'),
    '3. BI acceleration',
    'Materialized views pre-aggregate fact tables so dashboards get fast answers through automatic rewriting.',
    ['Fact table', '*MV', 'Fast tiles']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'compat', 11, 'acc', bold=True) + t(60, 58, 'migrations', 7.4, 'ink2'),
    '4. Schema migrations',
    'When tables are renamed or split, views with the old names keep existing reports working during the transition.',
    ['Old name', '*view', 'No broken reports']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'join', 11, 'acc', bold=True) + t(60, 58, 'denormalise', 7.4, 'ink2'),
    '5. Pre-joined datasets',
    'MVs that pre-join facts with dimensions save repeated joins for data science feature queries.',
    ['Facts + dims', '*MV join', 'Fast features']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> ACID tables (<a href="../../07-acid-and-iceberg/01-acid-tables-update-delete/">7.1</a>), EXPLAIN CBO (<a href="../../08-optimisation/01-explain-in-depth/">8.1</a>) and the CBO (<a href="../../08-optimisation/02-cbo-and-statistics/">8.2</a>).</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
