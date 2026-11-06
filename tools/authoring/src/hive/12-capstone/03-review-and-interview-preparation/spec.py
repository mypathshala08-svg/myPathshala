import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return re.sub(r'; Query ID[^\n]*', '', open(CAP + n).read().rstrip())
BODY = body(HERE)

META = dict(
    module='12-capstone', lesson='03-review-and-interview-preparation', n='12.3',
    module_label='Module 12 · Capstone: a TiffinGo data warehouse',
    title='Capstone part 3: review the warehouse and prepare for Hive interviews',
    desc='Review the capstone warehouse like a senior engineer, with real Hive 4.2.1 measurements: 18 KB files, ACID delta folders and a major compaction that cut delta folders from 15 to 1, seven automated PASS/FAIL data tests, and a materialized view the optimiser uses automatically until it goes stale. Then prepare for data engineering interviews: 50 Hive interview questions with short answers by topic, a 60-second STAR project pitch, resume lines and design-round patterns.',
    og_desc='A real code review of the capstone warehouse, then 50 Hive interview questions answered with numbers from your own project.',
    minutes=55, level='Intermediate → Advanced',
    lead='The last lesson of the Hive course. First Kabir’s warehouse gets a production readiness review with real measurements and fixes. Then Riya runs a mock interview: 50 questions grouped by topic, each linked to the lesson that explains it, and a project pitch built from the capstone’s numbers. <b>All lab outputs are real.</b>',
    chips=['Hive 4.2.1 · real outputs', 'Compaction · data tests · materialized views', '50 interview questions', 'Runs in your browser (Python)'],
)

MAIN = '''# Review helper: flag tables whose average file is far below a block
BLOCK = 128 * 1024 * 1024
tables = {  # table: (files, bytes) measured in Step 1
    "fact_orders": (31, 565614), "fact_deliveries": (31, 298639),
    "gold_city_daily": (31, 40002), "rejected_orders": (31, 26547), "dim_customer": (1, 24830),
}
for name, (files, size) in tables.items():
    avg = size / files
    verdict = "small files" if files > 1 and avg < BLOCK / 100 else "ok"
    print(f"{name:16} {files:3} files, avg {avg / 1024:7.1f} KB -> {verdict}")
'''
RUN = dict(
    heading='Run the code: review checks and interview drills',
    intro='<p>Small programs for the review checks of Steps 1–6 and two interview drills. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('    verdict = "small files" if files > 1 and avg < BLOCK / 100 else "ok"', 'A simple rule: many files averaging under 1% of a block. Real teams tune the threshold.'),
    ],
    tasks=[
        dict(label='1 · Small-file report', hint='Press <b>Run</b>. Then work out how many files a year of daily partitions creates for these four partitioned tables.', code=None),
        dict(label='2 · Should this partition be compacted?', hint='Count delta folders per partition and flag those above a threshold, as an alert would.',
             code='''partitions = {"2026-10-05": ["base_0000022_v0000116"],
              "2026-10-28": ["delete_delta_35", "delete_delta_36", "delete_delta_37", "delta_34", "delta_35a", "delta_35b", "delta_36a", "delta_36b", "delta_37"],
              "2026-10-31": ["delta_37"]}
for p, dirs in partitions.items():
    deltas = sum(d.startswith(("delta", "delete_delta")) for d in dirs)
    print(p, deltas, "COMPACT" if deltas >= 5 else "ok")
'''),
        dict(label='3 · Predict first: does Hive use the view?', hint='<b>Predict first</b>, then run: the view is used only if no source table changed since it was built.',
             code='''mv_built_at_write_id = 37
for current_write_id in (37, 38):
    uses_mv = current_write_id == mv_built_at_write_id
    print("fact write id", current_write_id, "->", "scan mv_status_day" if uses_mv else "scan fact_orders (view is stale)")
'''),
        dict(label='4 · Interview drill: ORDER BY vs SORT BY', hint='Simulate two reducers. SORT BY sorts inside each reducer only; ORDER BY gives one total order.',
             code='''rows = [7, 3, 9, 1, 8, 2]
reducers = [[r for r in rows if r % 2 == 0], [r for r in rows if r % 2 == 1]]   # DISTRIBUTE BY r % 2
print("SORT BY  :", [sorted(r) for r in reducers])
print("ORDER BY :", sorted(rows))
'''),
        dict(label='5 · Spot the error', hint='This “bucket” function ignores the number of buckets. Fix it: Hive assigns hash(value) mod N.', expect='error',
             code='''def bucket(customer_id, n_buckets=4):
    return hash(customer_id)              # bug: no mod
b = bucket(1033)
assert 0 <= b < 4, f"bucket {b} is outside 0..3"
print(b)
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: review commands',
    intro='<p>Commands from the review you can run on your own lab. <b>Outputs are real</b> (Hive 4.2.1).</p>',
    items=[
        dict(title='1 · The CBO plan uses the materialized view', cmd="EXPLAIN CBO SELECT status, SUM(amount) AS amt FROM fact_orders\nWHERE order_date >= DATE '2026-10-15' GROUP BY status;", file='beeline',
             output=capf('l123_mv3.txt'),
             note='<code>EXPLAIN CBO</code> prints the plan after Calcite’s optimisation, including materialized view rewriting. Look for the table name in <code>HiveTableScan</code>.'),
        dict(title='2 · The answer is the same either way', cmd="SELECT status, SUM(amount) AS amt FROM fact_orders\nWHERE order_date >= DATE '2026-10-15' GROUP BY status ORDER BY status;", file='beeline',
             output=capf('l123_mv6.txt'),
             note='Rewriting changes the work, never the result. Check this once when you add a view.'),
        dict(title='3 · Totals by status, the finance check', cmd='SELECT status, COUNT(*) AS n, SUM(amount) AS amt FROM fact_orders GROUP BY status ORDER BY status;', file='beeline',
             output=capf('l123_q_before.txt'),
             note='43,531 + 3,362 + 660 = 47,553 orders. Net revenue (DELIVERED) ₹1,53,95,190 is the number finance reconciles.'),
    ],
)

TRACE = dict(
    heading='Follow a materialized view through a load',
    intro='<p>How Hive decides whether a materialized view is fresh enough to use.</p>',
    code='''mv_snapshot = {"fact_orders": 37}          # write ids when the view was built
table_now = {"fact_orders": 37}
print("fresh" if mv_snapshot == table_now else "stale")
table_now["fact_orders"] = 38               # the nightly MERGE commits
print("fresh" if mv_snapshot == table_now else "stale")
mv_snapshot = dict(table_now)               # ALTER MATERIALIZED VIEW … REBUILD
print("fresh" if mv_snapshot == table_now else "stale")
''',
    notes={1: 'Built :: The view records the source tables’ transactional state.', 4: 'Load :: A new write id: the view no longer matches.', 6: 'Rebuild :: The view catches up and can be used again.'},
)

WORKED_INTRO = 'Three interview tasks solved the way a strong candidate would, with code you can run.'
EXAMPLES = [
    dict(level='b', tag='Interview · SQL', title='Second-highest order value per city',
         problem='<p>A favourite SQL question: the second-highest order amount in each city, ties included.</p>',
         inp='orders (city, amount)',
         approach=['Rank within each city by amount, descending.', 'DENSE_RANK so ties share a rank.', 'Keep rank 2.'],
         code='''orders = [("Mumbai", 900), ("Mumbai", 1000), ("Mumbai", 900), ("Pune", 700), ("Pune", 650)]
by_city = {}
for city, amt in orders:
    by_city.setdefault(city, set()).add(amt)
for city, amts in sorted(by_city.items()):
    ranked = sorted(amts, reverse=True)
    print(city, ranked[1] if len(ranked) > 1 else None)
''', notes={4: 'Distinct values :: A set gives DENSE_RANK behaviour.', 6: 'Rank 2 :: The second-highest distinct amount.'},
         tryit='HiveQL: SELECT city, amount FROM (SELECT city, amount, DENSE_RANK() OVER (PARTITION BY city ORDER BY amount DESC) dr FROM fact_orders) x WHERE dr = 2.'),
    dict(level='i', tag='Interview · troubleshooting', title='Diagnose a slow query from symptoms',
         problem='<p>Map interview symptoms to the most likely cause and the first check.</p>',
         inp='four symptoms',
         approach=['Read the symptom.', 'Name the likely cause.', 'Name the first command to confirm.'],
         code='''playbook = {
    "one reducer runs for hours, others finish fast": ("skewed key", "GROUP BY key ORDER BY COUNT(*) DESC LIMIT 10"),
    "query reads all partitions": ("no partition filter / function on partition column", "EXPLAIN DEPENDENCY"),
    "slower every week, same data size": ("ACID deltas piling up", "SHOW COMPACTIONS"),
    "thousands of map tasks for little data": ("small files", "count files per partition"),
}
for symptom, (cause, check) in playbook.items():
    print(f"{symptom}\\n  cause: {cause}\\n  check: {check}")
''', notes={1: 'Playbook :: Each answer has a cause and a concrete check.', 7: 'Answer shape :: Symptom → cause → check is what interviewers want.'},
         tryit='Add “OutOfMemory in a map join” → small table not small → check hive.auto.convert.join.noconditionaltask.size.'),
    dict(level='a', tag='Interview · design', title='Estimate a warehouse in a design round',
         problem='<p>Estimate yearly storage and daily partition size for a ride-booking fact table.</p>',
         inp='2 million rides/day; ~60 bytes per row in ORC (assumed)',
         approach=['Daily bytes = rows × bytes per row.', 'Yearly = daily × 365.', 'Decide partition grain from daily size.'],
         code='''rides, bytes_per_row = 2_000_000, 60
daily = rides * bytes_per_row
print(f"per day: {daily / 1024**2:.0f} MB, per year: {daily * 365 / 1024**3:.0f} GB")
print("partition by day" if daily > 64 * 1024**2 else "partition by month")
''', notes={3: 'Daily size :: About 114 MB per day: close to one block, so daily partitions are healthy.', 4: 'Decision :: State the rule you used; interviewers care about the reasoning.'},
         tryit='Repeat with TiffinGo’s 1,500 orders/day and 18 KB per day from Step 1.'),
]

QUIZ = mix([
    dict(q='Beginner: What does a major compaction do?', options=['Deletes old partitions', 'Rewrites base and delta folders of an ACID partition into one new base', 'Compresses text files', 'Drops statistics'], answer=1,
         why='The cleaner then removes the old folders.'),
    dict(q='Beginner: Which Hive 4 change should every interview answer know?', options=['Hive on Spark was added', 'Hive on Spark was removed and MapReduce deprecated; Tez is the default', 'Indexes were added', 'The metastore was removed'], answer=1,
         why='From the Hive 4.0 release overview.'),
    dict(q='Beginner: In a STAR answer, what does R stand for?', options=['Requirement', 'Result', 'Review', 'Risk'], answer=1,
         why='Situation, Task, Action, Result: end with measurable results.'),
    dict(q='Intermediate: Why was the first materialized view refused?', options=['Too many rows', 'Automatic rewriting needs transactional source tables, and dim_restaurant was plain ORC', 'Joins are not allowed', 'MVs need Iceberg'], answer=1,
         why='Hive must know whether every source table changed since the build.'),
    dict(q='Intermediate: After the nightly load, the same query scanned fact_orders instead of the view. Why?', options=['The view was dropped', 'The view was stale, and Hive never uses outdated views by default', 'The CBO was off', 'A syntax error'], answer=1,
         why='After REBUILD it used the view again.'),
    dict(q='Intermediate: How did the data tests avoid the Tez counter limit?', options=['Raising the limit', 'One small INSERT per test into dq_results instead of one big UNION ALL', 'Using MapReduce', 'Disabling Tez'], answer=1,
         why='Fewer stages per query.'),
    dict(q='Advanced: Our fact files average 18 KB. Best review action at this size?', options=['Add 64 buckets', 'Partition by month or use Iceberg with compaction', 'Switch to text files', 'Nothing will ever matter'], answer=1,
         why='Fewer, larger files; buckets would make files even smaller.'),
    dict(q='Advanced: An interviewer asks “SORT BY or ORDER BY for a global top 10?”', options=['SORT BY', 'ORDER BY … LIMIT 10 (one reducer, but LIMIT keeps it cheap)', 'CLUSTER BY', 'DISTRIBUTE BY'], answer=1,
         why='SORT BY only orders within each reducer.'),
])

REVISION = [
    'Review areas: <b>correctness, reliability, files, ACID deltas, statistics, serving, observability</b>.',
    'Measure files in <b>bytes per file</b>: ours averaged 18 KB against a 128 MB block.',
    'ACID: every MERGE adds delta/delete_delta folders; <code>COMPACT \'major\' AND WAIT</code>, check <code>SHOW COMPACTIONS</code>.',
    'Data tests = queries returning PASS/FAIL; run after every load; alert on FAIL.',
    'Materialized views: transactional sources, used automatically when fresh, <code>REBUILD</code> after loads.',
    'Hive 4: Tez default, MapReduce deprecated, Hive on Spark removed, Iceberg built in; indexes gone since 3.0.',
    'Answer pattern: definition → your choice → reason → a real detail or number.',
    'Project pitch (STAR) with numbers: 48,871 → 47,553 · 112 rejects · ₹42.8 L → ₹38.4 L · re-run safe.',
]
FAQ = [
    ('I have no work experience. Can I present the capstone as a project?', 'Yes, as a personal or course project, described honestly. Interviewers value a project you can explain in depth (why each table, what went wrong, what you measured) far more than a long list of tools. Expect detailed follow-up questions.'),
    ('How many of the 50 questions should I memorise?', 'None word for word. Understand each one well enough to answer in two or three sentences and to give an example from the capstone. Practise aloud; written knowledge and spoken answers are different skills.'),
    ('What if I am asked about a Hive version my company uses, like Hive 3 on Cloudera?', 'Most concepts are the same. Mention version differences you know (Hive 4 removed Hive on Spark; Hive 3 introduced ACID by default for managed tables and removed indexes) and say you would check the platform’s documentation for specifics.'),
    ('Should I also learn Spark?', 'Yes. Most data engineering roles in 2026 expect SQL, one engine such as Spark, a table format such as Iceberg or Delta, and a scheduler such as Airflow. Hive knowledge transfers directly: the metastore, partitions, file formats and ACID ideas are the same.'),
    ('Where do I go after this course?', 'Rebuild the capstone with a different dataset (rides, bank transactions), port it to Iceberg (Lesson 11.3), and add an Airflow DAG. Then explore the Spark and data engineering courses on MyPhatshala as they are published.'),
]

PRACTICE_INTRO = 'Interview-style practice problems. Solve them in Python here, then write the HiveQL from the explanation.'
PROBLEMS = [
    dict(level='easy', title='Files per year', stmt='How many files do four daily-partitioned tables create in a year (one file per partition)?', inp='4 tables, 365 days',
         code='''print(4 * 365, "files a year")
''', explain='With monthly partitions: 4 × 12 = 48.'),
    dict(level='easy', title='Bucket number', stmt='Compute the bucket for customer ids with 4 buckets, using the classic rule where an INT hashes to itself.', inp='1033, 1380, 2311',
         code='''for cid in (1033, 1380, 2311):
    print(cid, cid % 4)
''', explain='The rule is always hash mod N (CLUSTERED BY (customer_id) INTO 4 BUCKETS). Old tables (bucketing_version 1) hash an INT to itself; tables created by Hive 3 and later use bucketing_version 2 with a Murmur3 hash, so the real bucket numbers differ from this simple calculation.'),
    dict(level='easy', title='Global top 3', stmt='Return the three largest amounts overall.', inp='a list of amounts',
         code='''amounts = [450, 1000, 300, 900, 760, 120]
print(sorted(amounts, reverse=True)[:3])
''', explain='SELECT amount FROM fact_orders ORDER BY amount DESC LIMIT 3;'),
    dict(level='medium', title='Keep the latest row', stmt='De-duplicate events, keeping the latest per id.', inp='(id, ts, value)',
         code='''events = [(1, 3, "a"), (1, 5, "b"), (2, 1, "c"), (2, 1, "c")]
latest = {}
for i, ts, v in events:
    if i not in latest or ts > latest[i][0]:
        latest[i] = (ts, v)
print(latest)
''', explain='ROW_NUMBER() OVER (PARTITION BY id ORDER BY ts DESC) = 1.'),
    dict(level='medium', title='Running total per city', stmt='Cumulative net revenue per city by date.', inp='(city, date, amount)',
         code='''rows = [("Pune", "10-01", 100), ("Pune", "10-02", 50), ("Mumbai", "10-01", 70), ("Pune", "10-03", 30)]
run = {}
for city, d, amt in sorted(rows):
    run[city] = run.get(city, 0) + amt
    print(city, d, run[city])
''', explain='SUM(net) OVER (PARTITION BY city ORDER BY order_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW).'),
    dict(level='medium', title='Customers with no orders', stmt='Find customers who never ordered.', inp='customers and orders',
         code='''customers = {1, 2, 3, 4}
ordered = {2, 4, 4}
print(sorted(customers - ordered))
''', explain='SELECT c.customer_id FROM dim_customer c LEFT JOIN fact_orders f ON f.customer_id = c.customer_id WHERE c.is_current AND f.order_id IS NULL;'),
    dict(level='business', title='Month-over-month growth', stmt='Growth of orders per city between two months.', inp='September and October counts (illustrative for September)',
         code='''sep = {"Mumbai": 10950, "Pune": 9010}
oct_ = {"Mumbai": 11822, "Pune": 9336}
for c in oct_:
    print(c, f"{100 * (oct_[c] - sep[c]) / sep[c]:+.1f}%")
''', explain='LAG(orders) OVER (PARTITION BY city ORDER BY month) gives the previous month in HiveQL.'),
    dict(level='business', title='Refund rate by city', stmt='Refunded orders as a share of delivered + refunded, per city, from gold.', inp='October gold totals',
         code='''gold = {"Mumbai": (10846, 161), "Bengaluru": (10527, 163), "Pune": (8526, 145)}
for c, (deliv, ref) in gold.items():
    print(c, f"{100 * ref / (deliv + ref):.2f}%")
''', explain='SUM(refunded) / (SUM(delivered) + SUM(refunded)) from gold_city_daily, grouped by city.'),
]

SCN_INTRO = 'Final-round questions that combine everything in the course.'
SCENARIOS = (
    scn('Any company · HR + tech', 'Fresher', '“Explain Hive to a non-technical manager.”',
        'A hiring manager from the business side asks you to explain what you built.',
        'can you communicate without jargon?',
        '<p>“Our order data arrived as thousands of messy files. Hive lets us ask questions of those files in SQL, like a spreadsheet the size of a warehouse. I built a nightly process that cleans the data, keeps history and produces a daily city report. It found that last month’s Mumbai revenue had been overstated by about 11%.”</p>', 'Starting with YARN containers and ORC stripes.') +
    scn('Service company · troubleshooting', 'Mid-level', 'A Hive job failed at 3 a.m.',
        'The nightly job failed with “Too many counters: 121 max=120”. What do you do?',
        'do you diagnose before changing settings?',
        '''<ol>
          <li>Find the failing statement in the log; it is a Tez limit on counters per DAG.</li>
          <li>Short term: re-run (the pipeline is idempotent).</li>
          <li>Proper fix: simplify the query (fewer UNION branches, STACK) or raise tez.counters.max on the cluster after agreeing with the platform team.</li>
        </ol>''', 'Disabling Tez or switching to MapReduce.') +
    scn('Product company · design', 'Mid-level', 'Design a warehouse for a new domain',
        '“Design a Hive warehouse for an online pharmacy’s orders and prescriptions.”',
        'can you reuse a proven pattern?',
        '''<ul>
          <li>KPIs and grain first; raw external all-STRING tables by load date.</li>
          <li>Silver: ACID order fact with MERGE; SCD 2 for customer and pharmacy; quarantine; audit.</li>
          <li>Gold per city and day rebuilt for touched dates; tests and compaction; Iceberg if Trino or Spark must read it.</li>
        </ul>''', 'Jumping to tools before the grain and KPIs.') +
    scn('Data platform', 'Senior', 'Hive or something else?',
        'Your new team runs everything on Hive 3. The architect asks whether to stay on Hive or move.',
        'can you weigh migration honestly?',
        '''<ul>
          <li>Keep: the metastore and SQL ETL skills; Hive 4 adds Iceberg and better ACID.</li>
          <li>Move tables to Iceberg so Spark and Trino get consistent results (Lesson 11.1 showed three different counts).</li>
          <li>Plan in waves with validation (Lesson 11.3); keep Hive where it works well (large batch SQL).</li>
        </ul>''', '“Hive is dead, rewrite everything in Spark next quarter.”')
)
