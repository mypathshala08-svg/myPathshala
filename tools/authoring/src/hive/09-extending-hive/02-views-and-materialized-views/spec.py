import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from hivekit import tables
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return re.sub(r'; Query ID[^\n]*', '', open(CAP + n).read().rstrip())
def squeeze(s):
    return re.sub(r' {3,}', '   ', s)
BODY = body(HERE)

META = dict(
    module='09-extending-hive', lesson='02-views-and-materialized-views', n='9.2',
    module_label='Module 9 · Extending Hive',
    title='Views and materialized views',
    desc='Hive views and materialized views with real Hive 4.2.1 outputs: what a view stores (expanded SQL, VIRTUAL_VIEW), SELECT * freezing columns, views broken by dropped tables, why materialized-view rewriting requires transactional sources, automatic query rewriting (240 rows read instead of 5,000,000), staleness and the rewriting time window, incremental rebuild after INSERT vs full rebuild after DELETE, DISABLE REWRITE and the Hive 4 query results cache.',
    og_desc='A materialized view answered a 5-million-row query from 240 rows, without changing the SQL. Views and MVs in Hive 4.2.1, with the staleness traps shown.',
    minutes=40, level='Beginner → Advanced',
    lead='Views let many reports share one definition; <b>materialized views</b> let them share one <b>result</b>, and Hive 4 can use that result automatically. This lesson builds both for TiffinGo, then makes the MV stale on purpose to see what Hive does: refuse it, use it inside a time window, and rebuild it incrementally or fully. <b>All outputs are real</b>, from Hive 4.2.1.',
    chips=['Real Hive 4.2.1 outputs', 'Automatic query rewriting', 'Stale MV, wrong answer shown', 'Runs in your browser (Python)'],
)

MAIN = '''# A materialized view as a dictionary: (city, day) -> (count, revenue)
orders = [("Pune", "10-03", 500), ("Pune", "10-03", 700), ("Mumbai", "10-03", 400),
          ("Pune", "10-04", 300), ("Mumbai", "10-05", 900)]

mv = {}
for city, day, amt in orders:                       # CREATE MATERIALIZED VIEW ... GROUP BY city, day
    n, rev = mv.get((city, day), (0, 0))
    mv[(city, day)] = (n + 1, rev + amt)

# A query "by city" rewritten to roll up the MV: COUNT(*) becomes SUM(n)
by_city = {}
for (city, day), (n, rev) in mv.items():
    c, r = by_city.get(city, (0, 0))
    by_city[city] = (c + n, r + rev)
print("MV rows:", len(mv), "  base rows:", len(orders))
print(by_city)
'''
RUN = dict(
    heading='Run the code: build, use and rebuild an MV',
    intro='<p>These programs model what Hive did in the lab: store an aggregate, roll it up, go stale and rebuild. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('    mv[(city, day)] = (n + 1, rev + amt)', 'The MV keeps one row per (city, day): our real MV turned 5,000,000 orders into 240 rows.'),
        ('    by_city[city] = (c + n, r + rev)', 'Rewriting rolls daily rows up to cities. COUNT(*) on the base table becomes SUM(n) on the MV, as the real plan showed.'),
    ],
    tasks=[
        dict(label='1 · Roll-up', hint='Press <b>Run</b>. 5 orders became 4 MV rows; the city totals are the same as aggregating the orders directly.', code=None),
        dict(label='2 · Predict first: stale answer', hint='<b>Predict first:</b> a new Pune order of 1,000 arrives after the MV was built. What does a stale MV report for Pune?',
             code='''mv_pune = (176200, 52265000)          # real MV values in the lab
new = (1, 1000)
print("stale MV:", mv_pune)
print("truth   :", (mv_pune[0] + new[0], mv_pune[1] + new[1]))
'''),
        dict(label='3 · Incremental rebuild', hint='After INSERTs only, Hive aggregates the new rows and merges them with the MV (the UNION plan).',
             code='''mv = {("Pune", "10-03"): (2, 1200)}
new_rows = [("Pune", "10-03", 1000), ("Thane", "10-03", 250)]
delta = {}
for city, day, amt in new_rows:
    n, r = delta.get((city, day), (0, 0)); delta[(city, day)] = (n + 1, r + amt)
for k, (n, r) in delta.items():
    a, b = mv.get(k, (0, 0)); mv[k] = (a + n, b + r)
print(mv)
'''),
        dict(label='4 · Why DELETE forces a full rebuild', hint='A deleted row has to be subtracted. With only (count, sum) stored, MIN/MAX could not be fixed without recomputing; Hive recomputed everything in our lab.',
             code='''mv = {("Pune", "10-03"): (3, 2200)}     # count, sum
deleted = ("Pune", "10-03", 1000)
n, r = mv[deleted[:2]]
print("subtract works for COUNT/SUM:", (n - 1, r - deleted[2]))
print("but a stored MAX of 1000 could not be corrected without rescanning")
'''),
        dict(label='5 · Spot the error', hint='This check decides whether the MV may be used. It ignores staleness. Fix it.', expect='error',
             code='''mv_built_at, last_source_write, window_min = 10.00, 10.05, 0
usable = True                               # bug
assert usable == (last_source_write <= mv_built_at or window_min > 0), "a stale MV must not be used when the window is 0"
print("use MV")
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: MV metadata, disabling rewriting and the results cache',
    intro='<p>More statements on the lab MV. <b>Outputs are real</b>, from Hive 4.2.1.</p>',
    items=[
        dict(title='1 · Describe the materialized view', cmd='DESCRIBE FORMATTED mv_city_day;   -- selected lines', file='Beeline',
             output=squeeze('\n'.join(l for l in capf('l92_mvdesc.txt').split('\n') if any(k in l for k in ('Table Type', 'numRows', 'Original Query', 'Rewrite Enabled', 'Outdated', 'Source table')))),
             note='Table type MATERIALIZED_VIEW, 240 rows, rewrite enabled and not outdated (after the last rebuild). The section “Source table information” lists the tables and transaction state it was built from.'),
        dict(title='2 · Switch rewriting off for one MV', cmd="ALTER MATERIALIZED VIEW mv_city_day DISABLE REWRITE;\nSHOW MATERIALIZED VIEWS;\nEXPLAIN CBO SELECT city, SUM(amount) AS rev FROM orders_tx GROUP BY city;\nALTER MATERIALIZED VIEW mv_city_day ENABLE REWRITE;", file='Beeline',
             output='\n'.join(l for l in capf('l92_disable.txt').split('\n') if any(k in l for k in ('mv_', 'rewrite_enabled', 'HiveTableScan', '+-'))),
             note='With rewriting disabled, the query went back to orders_tx. Useful while you investigate a suspicious MV without dropping it.'),
        dict(title='3 · The query results cache', cmd="-- run the same report twice, cache enabled (the default)\nSELECT city, SUM(amount) AS rev, COUNT(*) AS n FROM orders_tx\nWHERE order_date BETWEEN '2026-10-01' AND '2026-10-07' GROUP BY city ORDER BY rev DESC LIMIT 3;", file='Beeline (INFO)',
             output=capf('l92_cachehit_clean.txt'),
             note='The second run took 0.0 seconds: HiveServer2 returned the cached result of the identical query (hive.query.results.cache.enabled=true). It is invalidated when the transactional source changes. Different from an MV: it only helps identical queries.'),
    ],
)

TRACE = dict(
    heading='Incremental rebuild after an INSERT',
    intro='<p>Follow the plan Hive showed for <code>ALTER MATERIALIZED VIEW … REBUILD</code>: aggregate rows newer than the last build, union with the MV, aggregate again.</p>',
    code='''mv = {"Pune|10-03": (176200, 52265000)}
last_build_writeid = 1
rows = [("Pune|10-03", 1000, 1), ("Pune|10-03", 1000, 2)]       # (key, amount, writeid)
new = [r for r in rows if r[2] > last_build_writeid]
n, rev = mv["Pune|10-03"]
for key, amt, w in new:
    n, rev = n + 1, rev + amt
print({"Pune|10-03": (n, rev)})
''',
    notes={4: 'Filter :: HiveFilter(condition=[<(1, $8.writeid)]) in the real plan.', 6: 'Merge :: UNION with the MV rows, then re-aggregate.', 8: 'Result :: 176,201 orders, as the fresh query returned.'},
)

WORKED_INTRO = 'Three decisions about views and materialized views.'
EXAMPLES = [
    dict(level='b', tag='Analytics · reuse', title='View, MV or table?',
         problem='<p>Choose the right object for four needs.</p>',
         inp='four requests from TiffinGo teams',
         approach=['Only reuse a definition → view.', 'Expensive aggregate, transactional source → MV.', 'A frozen snapshot → table.'],
         code='''needs = {"one definition of 'Gold order'": "view",
         "daily city totals for 40 dashboard tiles": "materialized view",
         "month-end snapshot for auditors": "table (CTAS)",
         "hide phone numbers from analysts": "view"}
for k, v in needs.items():
    print(f"{v:18} <- {k}")
''', notes={2: 'Source :: MV rewriting needs transactional sources, as Step 4 showed.'},
         tryit='A month-end snapshot must not change when the source changes, so neither a view nor a rebuilt MV fits.'),
    dict(level='i', tag='Data engineering · grain', title='Pick the MV grain',
         problem='<p>Dashboards group by city, by day, and by city and day. One MV should serve all of them.</p>',
         inp='queries: GROUP BY city · GROUP BY order_date · GROUP BY city, order_date',
         approach=['Union of all grouping columns.', 'Keep additive measures (COUNT, SUM).', 'Coarser queries roll up.'],
         code='''queries = [{"city"}, {"order_date"}, {"city", "order_date"}]
grain = set().union(*queries)
print("MV GROUP BY:", sorted(grain))
print("store: COUNT(*) AS n, SUM(amount) AS rev   (AVG = rev / n)")
''', notes={4: 'Additive :: Averages cannot be rolled up; store sum and count instead.'},
         tryit='Exactly our mv_city_day: 240 rows serving all three dashboards.'),
    dict(level='a', tag='Platform · freshness', title='Set a staleness policy',
         problem='<p>Loads arrive every 15 minutes; rebuild takes 2 minutes. Dashboards tolerate 20 minutes of delay. Choose the window and rebuild schedule.</p>',
         inp='load every 15 min, rebuild 2 min, tolerance 20 min (illustrative)',
         approach=['Rebuild after each load.', 'Window covers load + rebuild time.', 'Never exceed the tolerance.'],
         code='''load_every, rebuild, tolerance = 15, 2, 20
window = load_every + rebuild
print("rebuild after every load; window =", window, "min", "(OK)" if window <= tolerance else "(too stale)")
print(f"SET hive.materializedview.rewriting.time.window={window}min;")
''', notes={3: 'Window :: Covers the gap between a load and the next finished rebuild.'},
         tryit='With a window of 0 (the lab default), every load makes Hive fall back to the base table until the rebuild finishes: always correct, sometimes slow.'),
]

QUIZ = mix([
    dict(q='Beginner: Does a Hive view store data?', options=['Yes, a copy', 'No, only the query text', 'Only statistics', 'Only on first use'], answer=1,
         why='Table type VIRTUAL_VIEW; the query is expanded when used.'),
    dict(q='Beginner: Which statement refreshes a materialized view?', options=['REFRESH mv', 'ALTER MATERIALIZED VIEW mv REBUILD', 'MSCK REPAIR', 'ANALYZE mv'], answer=1,
         why='Incremental when possible, otherwise full.'),
    dict(q='Beginner: A column was added to the base table of a SELECT * view. Does the view show it?', options=['Yes', 'No, the column list was fixed at creation', 'Only after REBUILD', 'Error'], answer=1,
         why='Hive stored the expanded column list.'),
    dict(q='Intermediate: Why was rewriting refused for an MV on orders?', options=['Too many rows', 'orders is non-transactional (external)', 'Missing statistics', 'GROUP BY not allowed'], answer=1,
         why='Hive cannot track changes to external files.'),
    dict(q='Intermediate: How many rows did the rewritten query read?', options=['5,000,000', '240', '8', '0'], answer=1,
         why='240 MV rows instead of 5,000,000 base rows.'),
    dict(q='Intermediate: What happened after an INSERT into the source with the window at 0?', options=['The stale MV was used', 'Hive ignored the outdated MV and read the base table', 'Error', 'The MV rebuilt itself'], answer=1,
         why='Outdated for Rewriting: Yes.'),
    dict(q='Advanced: With a 10-minute window, what did the report return for Pune?', options=['The correct new count', 'The old count (176,200 instead of 176,201)', 'NULL', 'An error'], answer=1,
         why='Staleness traded for speed.'),
    dict(q='Advanced: Which rebuild did Hive plan after a DELETE?', options=['Incremental', 'Full recomputation', 'None', 'Partial by partition'], answer=1,
         why='After INSERT only it planned the incremental UNION.'),
])

REVISION = [
    '<b>View:</b> stored, expanded SQL (VIRTUAL_VIEW); no data; always current. Name columns, avoid SELECT *.',
    'Dropping a base table does not drop views; they fail when queried. Check dependents first.',
    '<b>MV:</b> <code>CREATE MATERIALIZED VIEW mv AS SELECT …</code> stores the result; <code>SHOW MATERIALIZED VIEWS</code>.',
    'Rewriting needs <b>transactional</b> sources; otherwise <code>DISABLE REWRITE</code>.',
    'Rewriting is automatic (<code>hive.materializedview.rewriting=true</code>): lab 240 vs 5,000,000 rows; COUNT(*) → SUM(n).',
    '<b>Stale:</b> Outdated for Rewriting → ignored at window 0; <code>…rewriting.time.window</code> allows stale answers.',
    '<b>REBUILD:</b> incremental (UNION of new writeids) after INSERT; full after DELETE/UPDATE.',
    'Hive 4 <b>results cache</b> returns identical queries instantly; disable it when measuring.',
]
FAQ = [
    ('Can I INSERT into a view?', 'No. Hive views are read-only. Load the base tables; the view shows the new data automatically.'),
    ('Can a materialized view use Iceberg tables?', 'Yes, in Hive 4 Iceberg tables can be MV sources and MVs can be stored as Iceberg; Cloudera documents incremental rebuilds for Iceberg MVs. Check your version’s documentation and EXPLAIN the rebuild.'),
    ('Is there an automatic rebuild?', 'Hive can schedule queries (<code>CREATE SCHEDULED QUERY … EXECUTED AS … AS ALTER MATERIALIZED VIEW mv REBUILD</code>) when the scheduled-query service is running. Many teams instead add the REBUILD as the last step of their load job.'),
    ('Do views slow queries down?', 'No: a view is expanded into the query and optimised as a whole, so filters on the view are pushed into the base tables. Very deep stacks of views make plans hard to read, though.'),
    ('What about Spark and Trino?', 'Both can read Hive views stored in the metastore with some limitations (the SQL dialect must be understood by the engine). Hive materialized views and their rewriting are specific to Hive; other engines just see a table.'),
]

PRACTICE_INTRO = 'Programs that model views and MVs, with the HiveQL in each explanation.'
PROBLEMS = [
    dict(level='easy', title='MV size', stmt='How many rows does an MV grouped by 8 cities and 30 days have?', inp='8 × 30',
         code='''print(8 * 30)
''', explain='240, the real row count of mv_city_day.'),
    dict(level='easy', title='Reduction factor', stmt='How many times fewer rows does the rewritten query read?', inp='5,000,000 vs 240',
         code='''print(round(5_000_000 / 240))
''', explain='About 20,833× fewer rows.'),
    dict(level='easy', title='Stale difference', stmt='How far off was the stale Pune revenue?', inp='52,265,000 vs 52,266,000',
         code='''print(52_266_000 - 52_265_000)
''', explain='Exactly the 1,000 inserted after the last rebuild.'),
    dict(level='medium', title='Roll-up average', stmt='Compute the average order value per city from MV rows (n, rev).', inp='two daily rows for Pune',
         code='''rows = [(100, 30000), (50, 20000)]
n = sum(r[0] for r in rows); rev = sum(r[1] for r in rows)
print(round(rev / n, 2))
''', explain='Never average the daily averages: 333.33, not 350.'),
    dict(level='medium', title='Can the MV answer it?', stmt='Decide if an MV grouped by (city, day) can answer each query.', inp='three GROUP BY lists',
         code='''mv = {"city", "order_date"}
for q in [{"city"}, {"order_date"}, {"customer_id"}]:
    print(sorted(q), "->", "MV" if q <= mv else "base table")
''', explain='customer_id is not in the MV, so Hive must read orders_tx.'),
    dict(level='medium', title='Expand SELECT *', stmt='Show the column list a SELECT * view stores.', inp='columns at creation',
         code='''cols = ["customer_id", "name", "city"]
print("SELECT " + ", ".join(f"`cust_copy`.`{c}`" for c in cols) + " FROM `tiffingo`.`cust_copy`")
''', explain='Exactly what SHOW CREATE TABLE v_cust_all returned; later columns are not included.'),
    dict(level='business', title='Dashboard cost', stmt='40 tiles each scan 2 TB daily. With one MV of 2 GB, how much is read?', inp='illustrative',
         code='''print("without MV:", 40 * 2000, "GB · with MV:", 40 * 2, "GB")
''', explain='80,000 GB vs 80 GB a day, if all tiles can be rewritten.'),
    dict(level='business', title='Freshness trade-off', stmt='With a 20-minute window, what share of the day can a dashboard be stale?', inp='loads every 15 min (illustrative)',
         code='''print("up to", 100, "% of refreshes may show data up to 20 minutes old")
''', explain='Every refresh may be served from an MV that misses the latest load; agree that this is acceptable.'),
]

SCN_INTRO = 'Views and MVs come up in both SQL rounds and design rounds.'
SCENARIOS = (
    scn('Any company · Hive', 'Fresher', '“View vs table?”',
        'Explain what a view is and when to use one.',
        'do you know views store no data?',
        '<p>A view is a stored SELECT with a name. It holds no data; Hive expands it into the query each time, so it always shows current data. Views simplify repeated joins, give one definition of a business rule, and restrict columns for security. A table stores data and must be reloaded to change.</p>', 'Saying views are faster than tables.') +
    scn('Data engineering', 'Mid-level', 'Materialized view not used',
        'You created an MV but EXPLAIN shows queries still read the base table.',
        'do you know the rewriting rules?',
        '''<ol>
          <li>Check that the sources are transactional and rewriting is enabled (SHOW MATERIALIZED VIEWS).</li>
          <li>Check “Outdated for Rewriting” in DESCRIBE FORMATTED; rebuild or set a window.</li>
          <li>Check the query can be derived from the MV’s grain and columns.</li>
        </ol>''', '“Query the MV by name in every report.”') +
    scn('Analytics', 'Mid-level', 'Dashboard numbers lag behind',
        'Finance says yesterday’s last orders are missing from a dashboard served by an MV.',
        'can you explain staleness?',
        '''<ul>
          <li>The MV was not rebuilt after the last load and the staleness window allowed it to be used.</li>
          <li>Rebuild after each load; reduce or remove the window for finance-critical reports.</li>
          <li>Document the freshness of each dashboard.</li>
        </ul>''', 'Blaming the source system first.') +
    scn('Architecture', 'Senior', 'Speed up 200 dashboards',
        'Design an acceleration layer for 200 dashboards on large transactional fact tables.',
        'can you design MVs as a layer?',
        '''<ul>
          <li>Find common grains from query logs; build a few MVs at those grains with additive measures.</li>
          <li>Rebuild in the load pipeline; set windows per business tolerance; monitor “Outdated” status.</li>
          <li>Verify rewriting with EXPLAIN CBO in CI; keep views as the semantic layer on top.</li>
        </ul>''', 'One MV per dashboard.')
)
