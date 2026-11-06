import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
C = 'l63_window.txt'
def sec(a, b=None, drop=()):
    s = capsec(C, a, b, drop)
    s = re.sub(r'#\d+L?', '', s)
    return '\n'.join(l if len(l) <= 140 else l[:137] + ' …' for l in s.split('\n'))

def rows(x, y, vals, hi=(), frame=None, w=120):
    """vals: list of (day, rev); hi: indexes highlighted; frame: (a, b) bracket"""
    o = ''
    for k, (d, r) in enumerate(vals):
        tone = 'green' if k in hi else 'card'
        o += box(x, y + k * 18, w, 16, tone, rx=2) + t(x + 6, y + k * 18 + 11, d, 6.8, anchor='start', mono=True) + t(x + w - 6, y + k * 18 + 11, r, 6.8, anchor='end', mono=True)
    if frame:
        a, b = frame
        o += f'<path d="M{x - 6} {y + a * 18}h-5v{(b - a + 1) * 18 - 2}h5" style="fill:none;stroke:var(--violet);stroke-width:1.6"/>'
    return o
PUNE = [('11-01', '450'), ('11-02', '380'), ('11-02', '380'), ('11-03', '520')]

# ---------------------------------------------------------------- story
sc_ = (rows(30, 30, PUNE, hi={1, 2}, frame=(0, 2)) + t(90, 112, 'Pune: running total, row 2', 7.0, 'ink2') +
       box(400, 12, 232, 132, 'card') + t(516, 30, 'Measured', 8.6, bold=True) +
       ''.join(t(412, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
           ('ties: row_number 1,2 rank 1,1', 'ink'), ('default frame: 1210 twice', 'red'),
           ('rowsBetween: 830 then 1210', 'green'), ('top-2 per city: WindowGroupLimit', 'green'),
           ('no partitionBy: 4 → 1 partition', 'red'), ('…12.0 s vs 7.1 s per city', 'amber')])))
scene_svg = scene('Window functions compute a value for every row from a group of related rows: ranks, previous values, running totals, shares. We ranked days, ran totals with two different frames and took the top orders per city from 5 million rows.', sc_,
                  'Every window needs a <tspan font-weight="700" class="s-acc">partition</tspan>, an <tspan font-weight="700" class="s-acc">order</tspan> and the right <tspan font-weight="700" class="s-acc">frame</tspan>.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“The running total jumped”</h2>
  <div class="story">
    <p class="narration">Riya built a running revenue chart per city with <code>sum().over(Window.partitionBy("city").orderBy("day"))</code>. On days with two identical entries the line jumped straight to the day’s total on both rows. The finance team asked why the running total was the same on two consecutive rows.</p>

{scene_svg}

R> Sir, a running total should grow row by row. Why did it skip?
A> Because with <code>orderBy</code> and no frame, Spark uses <code>RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW</code>: all rows with the <b>same day</b> are “current” together. For a row-by-row total you must say <code>rowsBetween</code>.
K> And windows are the way to get top N per group?
A> Yes, and Spark 4 optimises exactly that pattern. Today: ranking functions and ties, lag and lead, running totals and frames, moving averages and shares, top-N per city on 5 million rows, and what happens without <code>partitionBy</code>. All outputs are real (PySpark 4.3.0).
  </div>
</section>
'''

lv = '''
LEVELS> Window functions at three levels
L1> A class marks list
      <ul>
        <li>Each student keeps their own row, and you write next to it their rank within their section.</li>
        <li>“Previous test’s marks” is lag; a running total adds all earlier tests.</li>
        <li>The window is which rows you look at: same section (partition), in date order (order), and how far back (frame).</li>
      </ul>
L2> The API
      <ul>
        <li><code>w = Window.partitionBy(...).orderBy(...)</code>, optional <code>.rowsBetween(a, b)</code> or <code>.rangeBetween(a, b)</code>; then <code>F.func().over(w)</code>.</li>
        <li>Ranking: <code>row_number</code>, <code>rank</code>, <code>dense_rank</code>, <code>percent_rank</code>, <code>ntile</code>. Offset: <code>lag</code>, <code>lead</code>. Aggregates: <code>sum</code>, <code>avg</code>, <code>min</code>, <code>max</code>, <code>count</code> over a window.</li>
        <li><code>Window.unboundedPreceding</code>, <code>Window.currentRow</code>, <code>Window.unboundedFollowing</code>, or integer offsets.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>For tied revenue, <code>row_number</code> gave 1, 2; <code>rank</code> 1, 1, 3; <code>dense_rank</code> 1, 1, 2.</li>
        <li>The default frame gave 1210 on both rows of 2 November; <code>rowsBetween</code> gave 830 then 1210.</li>
        <li>Top 2 per city on 5M rows used <code>WindowGroupLimit</code>; a window with no partition moved everything to 1 partition (12.0 s vs 7.1 s).</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Window functions</h2>
''' + def_block(
    'A <b>window function</b> computes a value for each input row from a set of rows related to it, its <b>window</b>, without collapsing rows as <code>groupBy</code> does. The window is defined by a <b>partitioning</b> (rows with the same partition keys), an <b>ordering</b> within the partition, and a <b>frame</b> relative to the current row: <code>ROWS</code> frames count physical rows, <code>RANGE</code> frames include all rows whose ordering value lies in a range, so peers with equal ordering values are treated together. When an ordering is specified without a frame, the default frame is <code>RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW</code>; without ordering it is the whole partition. Spark executes windows by shuffling on the partition keys and sorting; a window without partition keys moves all data to a single partition.',
    'A window function looks at a group of rows around each row and writes a result on that row: its rank, the previous value, a running total. You choose the group (partitionBy), the order (orderBy) and how many rows to include (the frame). Rows are not merged, so you keep all details.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Window spec', 'partitionBy + orderBy + frame.'),
    ('row_number', '1, 2, 3… unique within the partition.'),
    ('rank / dense_rank', 'Ties share a rank; rank leaves gaps.'),
    ('lag / lead', 'Value from a previous / next row.'),
    ('Frame', 'Rows included around the current row.'),
    ('ROWS vs RANGE', 'Physical rows vs equal ordering values.'),
    ('Peers', 'Rows with the same ordering value.'),
    ('Top-N per group', 'row_number() ≤ N.'),
]) + '''

  <h3>Ranking functions with ties (Delhi: 610, 610, 300)</h3>
''' + table(['Function', 'Result', 'Use for'], [
    ['<code>row_number</code>', '1, 2, 3', 'exactly N rows per group; dedup (add a tiebreaker!)'],
    ['<code>rank</code>', '1, 1, 3', 'competition ranking with gaps'],
    ['<code>dense_rank</code>', '1, 1, 2', 'rank without gaps, “top 3 distinct values”'],
    ['<code>percent_rank</code> / <code>ntile(n)</code>', '0..1 / bucket number', 'percentiles, deciles'],
], minw=580) + lv + '''
EXAM> “Why does my running total repeat a value?” With orderBy and no frame Spark uses RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW, which includes all peers with the same ordering value. Use <code>.rowsBetween(Window.unboundedPreceding, Window.currentRow)</code> and a unique ordering (add a tiebreaker column) for a row-by-row running total.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Frames you will use</h2>
''' + table(['Goal', 'Frame', 'Example'], [
    ['Running total', '<code>rowsBetween(unboundedPreceding, currentRow)</code>', 'cumulative revenue'],
    ['Moving average of last 7 rows', '<code>rowsBetween(-6, 0)</code>', '7-day average (one row per day)'],
    ['Last 7 days by value', '<code>rangeBetween(-6*86400, 0)</code> on epoch seconds', 'irregular dates'],
    ['Share of group total', 'no orderBy (whole partition)', 'revenue / sum over city'],
    ['Previous/next value', 'lag/lead (frame not used)', 'day-over-day change'],
], minw=640) + '''
WARN> <code>Window.orderBy(...)</code> without <code>partitionBy</code> moves <b>all rows into one partition</b> on one executor (Spark logs “No Partition Defined for Window operation”). In our lab the 4 input partitions became 1 and the job took 12.0 s instead of 7.1 s; on a cluster with 5 billion rows it simply fails. Partition by something, or compute global ranks differently (e.g. sort + zipWithIndex, or approximate percentiles).
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Ranks, offsets, frames and top-N</h2>
  <p>All outputs are real: PySpark 4.3.0, local mode with 4 cores. Steps 1–4 use daily revenue for Pune and Delhi (with ties on purpose); Steps 5–6 use 5,000,000 orders.</p>
''' + stepper([
    ('Step 1 · Ranking and ties',
     code('python', 'l63_window.py', 'w = Window.partitionBy("city").orderBy(F.desc("revenue"))\nd.select("city", "day", "revenue", F.row_number().over(w).alias("row_number"),\n         F.rank().over(w).alias("rank"), F.dense_rank().over(w).alias("dense_rank"))', sec('== 1)', '== 2)')),
     'Each city is ranked separately. Delhi’s two 610 days got row_number 1 and 2 (in an <b>arbitrary</b> order), but rank 1 and 1; the next day got rank 3 and dense_rank 2. If you use row_number to pick one row, add a tiebreaker to the orderBy, or the chosen row can change between runs (Lesson 4.4).'),
    ('Step 2 · lag and lead',
     code('python', 'l63_window.py', 'w2 = Window.partitionBy("city").orderBy("day")\nd.select("city", "day", "revenue", F.lag("revenue").over(w2).alias("prev"),\n         (F.col("revenue") - F.lag("revenue").over(w2)).alias("change"), F.lead("day").over(w2).alias("next_day"))', sec('== 2)', '== 3)')),
     '<code>lag</code> took the previous row’s revenue in the same city, so day-over-day change is one expression, without a self-join. The first row of each partition has no previous row (null), the last no next. Partitions never leak: Delhi’s first day does not see Pune’s last.'),
    ('Step 3 · Running totals: the frame trap',
     code('python', 'l63_window.py', 'run_default = F.sum("revenue").over(Window.partitionBy("city").orderBy("day"))\nrun_rows = F.sum("revenue").over(Window.partitionBy("city").orderBy("day")\n                                .rowsBetween(Window.unboundedPreceding, Window.currentRow))', sec('== 3)', '== 4)')),
     'Riya’s bug, reproduced. The default <b>RANGE</b> frame treats both 2 November rows as “the current row”, so both show 1210. The <b>ROWS</b> frame adds one row at a time: 830, then 1210. Both end at 1730. Whenever ordering values can repeat, decide which you mean and write the frame explicitly.'),
    ('Step 4 · Moving average and share of total',
     code('python', 'l63_window.py', 'F.avg("revenue").over(Window.partitionBy("city").orderBy("day").rowsBetween(-1, 0))\nF.col("revenue") / F.sum("revenue").over(Window.partitionBy("city")) * 100', sec('== 4)', '== 5)')),
     '<code>rowsBetween(-1, 0)</code> averaged the current and previous row. A window with only <code>partitionBy</code> covers the whole partition, so each row can be divided by its city total: Pune’s 3 November was 30.1% of Pune’s revenue. Without windows this needs a groupBy and a join.'),
    ('Step 5 · Top 2 orders per city on 5M rows',
     code('python', 'l63_window.py', 'top = (o.withColumn("rn", F.row_number().over(\n          Window.partitionBy("city").orderBy(F.desc("amount"), "order_id")))\n        .where("rn <= 2").select("city", "order_id", "amount"))\ntop.explain()', sec('== 5)', '== 6)')),
     'The classic top-N-per-group pattern, with <code>order_id</code> as tiebreaker (many orders have the maximum 959). The plan shows a Spark 3.5+ optimisation: <code>WindowGroupLimit … Partial</code> <b>before</b> the shuffle keeps only the top 2 rows per city in each partition, so almost nothing is shuffled, then a final limit after it.'),
    ('Step 6 · A window without partitionBy',
     code('python', 'l63_window.py', 'r = o.withColumn("global_rank", F.row_number().over(Window.orderBy(F.desc("amount"), "order_id")))\nr.rdd.getNumPartitions()\nr.write.format("noop").mode("overwrite").save()\no.withColumn("city_rank", F.row_number().over(Window.partitionBy("city").orderBy(…))).write.format("noop")…', sec('== 6)')),
     'A global <code>row_number</code> collapsed 4 partitions into <b>1</b>: one task sorted all 5 million rows (12.0 s). Ranking within cities kept the work parallel (7.1 s). On a real cluster the difference is one core against hundreds, plus the risk of running one executor out of memory.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('Delhi 610 610 300', W), ('row_number 1 2 3', W), ('rank 1 1 3 | dense 1 1 2', G)], size=7.6),
    term([('prev  : NULL 450 380 380', W), ('change: NULL -70 0 140', G)], size=7.6),
    term([('default frame: 450 1210 1210 1730', RD), ('rowsBetween  : 450 830 1210 1730', G)], size=7.2),
    term([('avg_2: 450 415 380 450', W), ('pct_city: 26.0 22.0 22.0 30.1', G)], size=7.6),
    term([('top 2 per city: WindowGroupLimit', G), ('global window: 4 -> 1 partition', RD), ('12.0 s vs 7.1 s', Y)], size=7.4),
]
B1 = [
    t(180, 14, 'Rank inside each partition', 9.4, bold=True) + rows(30, 34, [('Delhi', '610 → 1'), ('Delhi', '610 → 1'), ('Delhi', '300 → 3')], w=130) + rows(200, 34, [('Pune', '520 → 1'), ('Pune', '450 → 2')], w=130) + cap('Ties: row_number differs from rank.', '', 'blue', y=144, h=30),
    t(180, 14, 'Look one row back', 9.4, bold=True) + rows(110, 34, PUNE, hi={1}, frame=(0, 0)) + cap('lag(): previous row, same city.', '', 'blue', y=144, h=30),
    t(180, 14, 'RANGE frame: peers together', 9.4, bold=True) + rows(40, 34, PUNE, hi={1, 2}, frame=(0, 2)) + t(50, 120, 'RANGE: row 2 sees 3 rows', 7.0, 'red', anchor='start') + rows(230, 34, PUNE, hi={1}, frame=(0, 1), w=110) + t(240, 120, 'ROWS: 2 rows', 7.0, 'green', anchor='start') + cap('Write the frame explicitly.', '', 'red', y=144, h=30),
    t(180, 14, 'Sliding and whole-partition frames', 9.4, bold=True) + rows(40, 34, PUNE, hi={2, 3}, frame=(2, 3)) + rows(220, 34, PUNE, hi={0, 1, 2, 3}, frame=(0, 3)) + cap('Moving average | share of total.', '', 'violet', y=144, h=30),
    t(180, 14, 'Partitions keep it parallel', 9.4, bold=True) + ''.join(opbox(14, 30 + k * 30, f'city {k + 1}', 'own task', 'green', 90, 24) for k in range(3)) + opbox(220, 50, 'no partitionBy', 'ONE task', 'acc', 110, 34) + cap('Global windows run on one core.', '', 'amber', y=144, h=30),
]
see_caps = ['Three rankings, different on ties.', 'Day-over-day change with lag.', 'The default frame repeated 1210.', 'Moving average and share.', 'Top-N optimised; global window slow.']
behind_caps = ['partitionBy + orderBy.', 'Offset functions ignore the frame.', 'RANGE includes peers.', 'rowsBetween and partition-wide frames.', 'Windows shuffle by partition keys.']
two = anim_two('Window functions', 'Calculations across related rows', 'Real lab outputs', 'The window', see, B1, see_caps, behind_caps)

# ---- scenario 1: running total
e1 = (t(180, 22, 'Cumulative revenue chart', 9.4, bold=True) + t(180, 56, 'sum().over(partitionBy.orderBy(day))', 8.0, 'ink', mono=True) + cap('Looks fine in tests.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Two entries on one day', 9.4, bold=True) + t(180, 56, 'both rows show the day total', 8.4, 'ink2') + cap('Chart has a flat step.', '', 'amber', y=150, h=34))
e3 = (t(180, 22, 'Default RANGE frame', 9.4, bold=True) + t(180, 56, 'peers counted together', 8.4, 'ink2') + cap('Our Step 3.', '', 'red', y=150, h=34))
e4 = (t(180, 22, 'rowsBetween + tiebreaker', 9.4, bold=True) + t(180, 56, 'orderBy("day", "order_id")', 8.4, 'ink', mono=True) + cap('Row by row, stable.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Or aggregate per day first', 9.4, 'acc', bold=True) + t(180, 56, 'one row per day, then a window', 8.4, 'ink2') + cap('Often what finance wants.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'A running total with steps',
              'Window frames. (Behaviour from our lab.)',
              'RANGE vs ROWS', 'The default frame with orderBy is RANGE and includes peers; use rowsBetween and a unique order for running totals', [e1, e2, e3, e4, e5],
              ['Chart.', 'Same value.', 'RANGE.', 'ROWS.', 'Daily first.'],
              hid='scenario-frame')

# ---- scenario 2: latest record per key
b1 = (t(180, 22, 'Latest address per customer', 9.4, bold=True) + t(180, 56, 'from 40M change records', 8.4, 'ink2') + cap('Daily job.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'groupBy + max(ts) + join back', 9.4, bold=True) + t(180, 56, 'two shuffles, ties duplicate rows', 8.4, 'ink2') + cap('Slow and wrong on ties.', '', 'amber', y=150, h=34))
b3 = (t(180, 22, 'row_number over a window', 9.4, bold=True) + t(180, 56, 'partitionBy(id).orderBy(desc(ts), seq)', 8.0, 'ink', mono=True) + cap('One shuffle, exactly one row.', '', 'green', y=150, h=34))
b4 = (t(180, 22, 'where rn = 1', 9.4, bold=True) + t(180, 56, 'WindowGroupLimit prunes early', 8.4, 'ink2') + cap('Spark 3.5+.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Same pattern: top N', 9.4, 'acc', bold=True) + t(180, 56, 'rn <= N per group', 8.4, 'ink', mono=True) + cap('Our Step 5.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'The latest record per key',
              'Top-N per group with windows. (Typical; plan from our lab.)',
              'row_number top-N', 'row_number over a partitioned, ordered window picks exactly N rows per key in one shuffle', [b1, b2, b3, b4, b5],
              ['Need latest.', 'Join back.', 'row_number.', 'Filter.', 'Top N.'],
              hid='scenario-latest')

# ---- scenario 3: global rank
u1 = (t(180, 22, 'Rank all customers by spend', 9.4, bold=True) + t(180, 56, 'Window.orderBy(desc("spend"))', 8.4, 'ink', mono=True) + cap('No partitionBy.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'One task, 300M rows', 9.4, bold=True) + t(180, 56, 'executor runs out of memory', 8.4, 'ink2') + cap('Job fails after an hour.', '', 'red', y=150, h=34))
u3 = (t(180, 22, 'What is really needed?', 9.4, bold=True) + t(180, 56, 'top 1,000, or percentile buckets', 8.4, 'ink2') + cap('Rarely an exact global rank.', '', 'amber', y=150, h=34))
u4 = (t(180, 22, 'Top 1,000', 9.4, bold=True) + t(180, 56, 'orderBy(desc).limit(1000)', 8.4, 'ink', mono=True) + cap('Top-k plan (Lesson 4.5).', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'Buckets', 9.4, 'acc', bold=True) + t(180, 56, 'percentile_approx thresholds', 8.4, 'ink2') + cap('Parallel and cheap.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'A global rank on 300 million rows',
              'Windows without partitions. (Typical; behaviour from our lab.)',
              'Global windows', 'A window without partitionBy runs in one task; use top-k or approximate percentiles instead of exact global ranks', [u1, u2, u3, u4, u5],
              ['Global rank.', 'One task.', 'Real need.', 'Top-k.', 'Percentiles.'],
              hid='scenario-global-window')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Calculations across related rows</h2>
  <p>Left: real outputs. Right: which rows each window sees.</p>
''' + two + '''
  <p>Three live scenarios follow: a running total with steps, the latest record per key, and a global rank on 300 million rows.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Windows at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'latest', 12, 'blue', bold=True) + t(60, 58, 'record', 7.4, 'ink2'),
    '1. Latest version of records',
    'Change logs are reduced to the current row per key with row_number.',
    ['Changes', '*row_number = 1', 'Current table']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'trend', 12, 'green', bold=True) + t(60, 58, 'moving avg', 7.4, 'ink2'),
    '2. Trends',
    '7-day moving averages and day-over-day changes for dashboards.',
    ['Daily KPIs', '*avg over rows', 'Smoothed line']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'top N', 12, 'violet', bold=True) + t(60, 58, 'per group', 7.4, 'ink2'),
    '3. Leaderboards per group',
    'Top restaurants per city, best-selling dishes per restaurant.',
    ['Scores', '*rank per city', 'Top 10']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'sessions', 10, 'acc', bold=True) + t(60, 58, 'clicks', 7.4, 'ink2'),
    '4. Sessionisation',
    'lag on click times finds gaps over 30 minutes; a running sum of “new session” flags numbers sessions.',
    ['Clicks', '*lag + running sum', 'Sessions']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'ML', 12, 'acc', bold=True) + t(60, 58, 'features', 7.4, 'ink2'),
    '5. Time-based features',
    'Orders in the last 30 days, days since last order and running spend per customer.',
    ['Orders', '*range frames', 'Features']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> groupBy in <a href="../01-groupby-and-pivot/">6.1</a>, deterministic dedup in <a href="../../04-dataframes/04-nulls-and-duplicates/">4.4</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
