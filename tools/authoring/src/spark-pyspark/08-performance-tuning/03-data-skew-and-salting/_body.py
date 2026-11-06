import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
C = 'l83_skew.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)

def tbars(x, y, sizes, tone='green', label='', hot=48):
    o = t(x, y - 6, label, 7.2, 'ink2', anchor='start', bold=True) if label else ''
    for k, s in enumerate(sizes):
        o += box(x + k * 16, y + (60 - s), 12, max(s, 1), tone if s < hot else 'acc', rx=2)
    return o

# ---------------------------------------------------------------- story
sc_ = (tbars(14, 40, [8, 9, 8, 60, 9, 8, 9, 8], 'green', 'tasks: one runs forever') + arrow(150, 70, 180, 70, 'ink3', 1.1) +
       tbars(190, 40, [20, 21, 20, 21, 20, 21, 20, 21, 20, 20, 21], 'green', 'after: even') +
       box(400, 12, 232, 132, 'card') + t(516, 30, 'Measured (60% hot key)', 8.6, bold=True) +
       ''.join(t(412, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
           ('window: max task 5.5 s', 'red'), ('...reads 3.9M vs 0.28M', 'red'),
           ('groupBy: fine (partial agg)', 'green'), ('salted join: rows even', 'green'),
           ('AQE split: max 2.8→1.3 s', 'green'), ('split hot key: 17.2→10.8 s', 'green')])))
scene_svg = scene('Data skew means one key holds far more rows than the others, so one task does most of the work. We gave one restaurant 60% of 6 million orders and measured a window, a groupBy and a join, then fixed them with salting, AQE and splitting the hot key.', sc_,
                  'A stage is only as fast as its <tspan font-weight="700" class="s-acc">slowest task</tspan>.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“199 tasks done, 1 task running”</h2>
  <div class="story">
    <p class="narration">TiffinGo signed a cloud-kitchen chain that now takes 60% of all orders. Overnight, the restaurant ranking job went from minutes to hours. The Spark UI showed 199 finished tasks and one task still running.</p>

{scene_svg}

K> Sir, Spark has 200 cores. Why is only one working?
A> Because all rows with the same key must go to the same partition after a shuffle. If one restaurant has 60% of the rows, one task gets 60% of the work. That is <b>data skew</b>.
R> Can we just add more machines?
A> No: one task runs on one core, however big the cluster. We have to spread the hot key. Today we measure skew in task metrics, see why groupBy survives it, and fix joins and windows with <b>salting</b>, AQE and splitting the hot key. All outputs are real (PySpark 4.3.0).
  </div>
</section>
'''

lv = '''
LEVELS> Skew at three levels
L1> One busy billing counter
      <ul>
        <li>A supermarket opens 8 counters, but everyone with a loyalty card must use counter 4. Seven cashiers wait while one queue never ends.</li>
        <li>Salting: give loyalty customers a random counter number 1–8 and let every counter handle them.</li>
      </ul>
L2> The tools
      <ul>
        <li>Detect: Spark UI task summary (max vs median duration and shuffle read), <code>groupBy(key).count()</code>.</li>
        <li>Fix joins: AQE skew join (<code>spark.sql.adaptive.skewJoin.*</code>), broadcast the other side, or salt: <code>(F.rand() * S).cast("int")</code> on the big side, <code>F.explode(F.sequence(0, S-1))</code> on the small side.</li>
        <li>Fix aggregations: partial aggregation (automatic), or two-stage salted aggregation. Fix windows: handle the hot key separately.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>Window by restaurant: one task read 3.9M rows vs 0.28M, 5.5 s vs 0.7 s.</li>
        <li>groupBy on the same key: max task 73 ms, because map-side partial aggregation shrank the shuffle to ~800 rows per task.</li>
        <li>Salting evened rows per task (min/max 819K/864K); AQE split the hot join partition (max 2.8 s → 1.3 s).</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Data skew and salting</h2>
''' + def_block(
    '<b>Data skew</b> is an uneven distribution of rows across partitions, usually because a few join or grouping keys are far more frequent than the rest. Since a hash shuffle sends all rows of a key to one partition, a hot key creates a <b>straggler task</b> that dominates the stage’s runtime and may spill or run out of memory. Skew is diagnosed from the task summary metrics of a stage (max vs median duration, shuffle read size and records). <b>Salting</b> adds a random or derived component to the key so a hot key is spread over several partitions: for joins the other side is replicated once per salt value, and for aggregations results are combined in a second stage. Adaptive Query Execution can split skewed sort-merge join partitions automatically.',
    'Skew is when one key has many more rows than others, so one task does most of the work and the whole stage waits for it. Salting adds a random number to the hot key so its rows are spread across many tasks, and then the results are combined.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Hot key', 'A key with a huge share of rows.'),
    ('Straggler', 'A task much slower than the rest.'),
    ('Task summary', 'Min/median/max metrics per stage.'),
    ('Partial aggregation', 'Combining rows before the shuffle.'),
    ('Salt', 'Random number added to a key.'),
    ('Explode', 'Copy small side once per salt.'),
    ('Skew join (AQE)', 'Split big partition automatically.'),
    ('Isolate hot key', 'Process hot keys separately.'),
]) + '''

  <h3>Which operation suffers, which fix</h3>
''' + table(['Operation', 'Skew hurts?', 'Lab', 'Fix'], [
    ['groupBy + sum/count', 'Rarely', 'max task 73 ms', 'Automatic partial aggregation'],
    ['groupBy + collect_list / distinct', 'Yes', 'Lesson 8.4', 'Two-stage salted aggregation'],
    ['Join, small other side', 'No if broadcast', 'Lesson 8.2', 'Broadcast the small side'],
    ['Join, both sides big', 'Yes', 'max 2.8 s vs median 1.0 s', 'AQE skew join, or salting'],
    ['Window partitionBy hot key', 'Yes, badly', '3.9M rows in one task', 'Split the hot key out'],
], minw=640) + lv + '''
EXAM> “How do you handle data skew in Spark?” First confirm it in the Spark UI task summary (max far above median). For joins, broadcast the small side if possible, rely on AQE skew-join splitting, or salt: add a random salt 0..S-1 to the skewed side and explode the other side over all salts, then join on (key, salt). For aggregations, aggregate on (key, salt) then on key. For hot keys like nulls or defaults, filter or handle them separately.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Salting patterns</h2>
''' + table(['Pattern', 'Big side', 'Other side', 'Cost'], [
    ['Salted join', '<code>salt = (rand() * S).cast("int")</code>', '<code>explode(sequence(0, S-1))</code>', 'Other side × S rows'],
    ['Salt only hot keys', 'salt if key in hot list, else 0', 'explode only hot keys', 'Small replication'],
    ['Two-stage aggregation', '<code>groupBy(key, salt)</code> then <code>groupBy(key)</code>', 'n/a', 'One extra aggregation'],
    ['Isolate hot key', '<code>filter(key = hot)</code> processed separately', 'broadcast its match', 'Two code paths'],
], minw=640) + '''
WARN> Salting multiplies the other side by <b>S</b>. In our lab the menu side became 16x larger, so the salted join read about 850K records per task and was not faster on our 2-CPU machine (5.66 s vs 5.16 s), even though tasks were perfectly even. Salting pays off on a real cluster where idle cores can take the extra tasks. Choose S from the skew ratio (hot partition ÷ median), salt only the hot keys if you can, and try AQE or a broadcast first.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Measuring and fixing skew</h2>
  <p>All outputs are real: PySpark 4.3.0, <code>local[4]</code> (2 physical CPUs), AQE off unless stated, 8 shuffle partitions. 6,000,000 orders where restaurant 1 has 60%. Task durations and shuffle records come from the REST API task list of the reduce stage.</p>
''' + stepper([
    ('Step 1 · A skewed window',
     code('python', 'l83_skew.py', 'o = spark.range(N).select(F.col("id").alias("order_id"),\n      F.when(F.col("id") % 10 < 6, F.lit(1)).otherwise((F.col("id") % 4000) + 2).alias("rest_id"), …)\nw = Window.partitionBy("rest_id").orderBy("amount")\nrun("window by rest_id", sink(heavy(o).withColumn("rk", F.row_number().over(w)))); tasks(st)', sec('top keys:', '== 2)')),
     'Restaurant 1 has <b>3.6 million</b> orders; the next has 1,500. In the window stage one task read <b>3,897,000</b> records while the smallest read 279,000, and ran <b>5.5 s</b> vs 0.74 s. The median task was done in 2.7 s and then waited. On a 200-core cluster this is 199 idle cores.'),
    ('Step 2 · Why the groupBy did not suffer',
     code('python', 'l83_skew.py', 'run("groupBy rest_id sum", sink(o.groupBy("rest_id").agg(F.sum("amount")))); tasks(st)', sec('== 2)', '== 3)')),
     'Same hot key, but each reduce task read only about <b>800 records</b>: every map task first summed its own rows per restaurant (<b>partial aggregation</b>), so restaurant 1 arrived as one row per map task, not 3.6 million. Sums and counts are naturally skew-resistant. <code>collect_list</code>, <code>countDistinct</code> and windows are not.'),
    ('Step 3 · A skewed join',
     code('python', 'l83_skew.py', 'spark.conf.set("spark.sql.autoBroadcastJoinThreshold", -1)\nmenu = spark.range(400000).select(F.when(F.col("id") < 200, F.lit(1))\n          .otherwise(F.col("id") % 4000 + 2).alias("rest_id"), F.col("id").alias("item"))\nj = o.sample(0.05, 7).join(menu, "rest_id")', sec('== 3)', '== 4)')),
     'Restaurant 1 is hot on both sides (200 menu items), so its partition produces 36 million output rows. The hot task read 244K records vs a minimum of 62K and ran <b>2.8 s vs median 1.0 s</b>.'),
    ('Step 4 · Salting the join',
     code('python', 'l83_skew.py', 'S = 16\nos_ = o_s.withColumn("salt", (F.rand(1) * S).cast("int"))\nms  = menu.withColumn("salt", F.explode(F.sequence(F.lit(0), F.lit(S - 1))))\njs  = os_.join(ms, ["rest_id", "salt"]).drop("salt")\nprint(j.count() == js.count())', sec('== 4)', '== 5)')),
     'Each order picks a random salt 0–15; each menu row is copied 16 times, once per salt. Every order still meets every matching menu item exactly once (<b>same row count: True</b>), but restaurant 1 is now spread over 16 keys. Records per task became nearly equal: <b>819K to 864K</b>. The price: the menu side is 16x bigger, so on our 2 CPUs the total time did not improve. With idle cores on a cluster, even tasks finish together.'),
    ('Step 5 · Let AQE split it',
     code('python', 'l83_skew.py', 'spark.conf.set("spark.sql.adaptive.enabled", "true")\nspark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes", "1m")   # small lab\nspark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionFactor", "2")\nrun("AQE skew join", sink(o_s.join(menu, "rest_id")))', sec('== 5)', '== 6)')),
     'No code change: AQE saw the hot partition after the shuffle and split it, so the stage ran <b>11 tasks</b> instead of 8, max records per task fell from 244K to 98K, and the slowest task from 2.8 s to <b>1.3 s</b>. Total 2.91 s, the best of all join runs. Defaults (5x median and 256 MB) are much higher than our lab values.'),
    ('Step 6 · Handle the hot key separately',
     code('python', 'l83_skew.py', 'hot, cold = o.filter("rest_id = 1"), o.filter("rest_id <> 1")\n# hot key: sort in parallel by amount using range partitioning\nrun("hot key alone", sink(heavy(hot).repartitionByRange(8, "amount").sortWithinPartitions("amount")))\nrun("cold keys window", sink(heavy(cold).withColumn("rk", F.row_number().over(w))))', sec('== 6)')),
     'Windows cannot be salted directly, because a rank needs all rows of the key. But a single hot key can be ordered with <b>range partitioning</b> on the order column: each of 8 tasks sorts one range (420K–504K records, max 0.48 s), and the rank is the range offset plus the position inside it. The remaining keys are balanced. Together <b>10.8 s vs 17.2 s</b>, and no task above 0.8 s.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('rest_id 1: 3600000 rows', RD), ('window max task 5504 ms', RD), ('records 279000 .. 3897000', Y)], size=7.4),
    term([('groupBy sum: max task 73 ms', G), ('records 744 .. 852', G)], size=7.6),
    term([('join  : 556 .. 2830 ms', Y), ('salted: rows 819245 .. 864318', G), ('AQE   : max 1293 ms, 11 tasks', G)], size=7.4),
    term([('hot alone : max 483 ms', G), ('cold keys : max 797 ms', G), ('17.22 s -> 7.00 + 3.77 s', G)], size=7.4),
]
B1 = [
    t(180, 14, 'Hash sends a key to one task', 9.4, bold=True) + tbars(40, 50, [8, 9, 8, 60, 9, 8, 9, 8], 'green', '8 reduce tasks') + t(270, 90, 'rest 1 → task 4', 7.4, 'red') + cap('Stage waits for the straggler.', '', 'amber', y=144, h=30),
    t(180, 14, 'Partial aggregation', 9.4, bold=True) + flow([('3.6M rows', 'map side', 'acc'), ('sum per task', '1 row each', 'green'), ('shuffle', '~800 rows', 'green')], y=50, w=96, gap=16) + cap('Sums shrink before the shuffle.', '', 'green', y=144, h=30),
    t(180, 14, 'Salt: key → (key, 0..15)', 9.4, bold=True) + opbox(20, 40, 'orders', 'rest 1 + rand salt', 'blue', 120, 32) + opbox(220, 40, 'menu × 16', 'one copy per salt', 'violet', 120, 32) + tbars(110, 80, [20, 21, 20, 21, 20, 21, 20, 21], 'green', '') + cap('Even tasks, bigger other side.', '', 'green', y=144, h=30),
    t(180, 14, 'Split the hot key out', 9.4, bold=True) + opbox(20, 40, 'hot key', 'range-partition', 'acc', 140, 32) + opbox(200, 40, 'other keys', 'normal window', 'green', 140, 32) + t(180, 100, 'union the results', 7.6, 'ink2') + cap('No single giant task.', '', 'green', y=144, h=30),
]
see_caps = ['A skewed window.', 'groupBy survives.', 'Join: salting and AQE.', 'Hot key split out.']
behind_caps = ['Hash partitioning a hot key.', 'Map-side combine.', 'Salting a join.', 'Isolating hot keys.']
two = anim_two('Data skew', 'One key, one task', 'Real lab outputs', 'What Spark does', see, B1, see_caps, behind_caps)

e1 = (t(180, 22, 'Join stuck at 199/200', 9.4, bold=True) + t(180, 56, 'Spark UI: max 40 min, median 30 s', 8.4, 'ink2') + cap('Classic skew signature.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Find the key', 9.4, bold=True) + t(180, 56, 'groupBy(key).count().orderBy(desc)', 8.2, 'ink', mono=True) + cap('One chain: 60% of rows.', '', 'amber', y=150, h=34))
e3 = (t(180, 22, 'Is AQE splitting it?', 9.4, bold=True) + t(180, 56, 'look for skew=true in the plan', 8.4, 'ink2') + cap('Tune thresholds if not.', '', 'green', y=150, h=34))
e4 = (t(180, 22, 'Still slow: salt hot keys', 9.4, bold=True) + t(180, 56, 'S = hot size ÷ median size', 8.4, 'ink2') + cap('Replicate only hot rows.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Max task 40 → 3 min', 9.4, 'acc', bold=True) + t(180, 56, 'stage time follows', 8.4, 'ink2') + cap('Cores used evenly.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'The 199-of-200 join',
              'Diagnosing and fixing a skewed join. (Typical; pattern from our lab.)',
              'Skewed join', 'Find the hot key, check AQE skew handling, then salt only the hot keys', [e1, e2, e3, e4, e5],
              ['Stuck.', 'Hot key.', 'AQE.', 'Salt.', 'Fixed.'],
              hid='scenario-join')
b1 = (t(180, 22, 'Join on customer_id', 9.4, bold=True) + t(180, 56, '40% of rows have NULL id', 8.4, 'ink2') + cap('Guest checkouts.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'All NULLs in one task?', 9.4, bold=True) + t(180, 56, 'inner join never matches them', 8.4, 'ink2') + cap('Wasted work and skew.', '', 'amber', y=150, h=34))
b3 = (t(180, 22, 'Filter NULLs before the join', 9.4, bold=True) + t(180, 56, 'or union them back after', 8.4, 'ink2') + cap('For left joins.', '', 'green', y=150, h=34))
b4 = (t(180, 22, 'Same for defaults', 9.4, bold=True) + t(180, 56, '“unknown”, 0, -1, “NA”', 8.4, 'ink', mono=True) + cap('Fake hot keys.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Check key distributions', 9.4, 'acc', bold=True) + t(180, 56, 'in data quality checks', 8.4, 'ink2') + cap('Catch it before Spark does.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'The NULL hot key',
              'Skew from NULLs and default values. (Typical.)',
              'NULL skew', 'NULL or default keys often cause skew; filter them out before the join', [b1, b2, b3, b4, b5],
              ['NULLs.', 'One task.', 'Filter.', 'Defaults.', 'Checks.'],
              hid='scenario-null')
u1 = (t(180, 22, 'Top-10 dishes per restaurant', 9.4, bold=True) + t(180, 56, 'window partitionBy rest_id', 8.4, 'ink2') + cap('Chain has 60% of rows.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'One task: 3.9M rows', 9.4, bold=True) + t(180, 56, 'spills, then OOM at scale', 8.4, 'ink2') + cap('Salting breaks ranks.', '', 'red', y=150, h=34))
u3 = (t(180, 22, 'Hot key separately', 9.4, bold=True) + t(180, 56, 'range-partition by the order column', 8.2, 'ink2') + cap('8 tasks of ~0.5M rows.', '', 'green', y=150, h=34))
u4 = (t(180, 22, 'Or reduce first', 9.4, bold=True) + t(180, 56, 'top-10 per (rest, salt), then top-10', 8.2, 'ink2') + cap('Two-stage top-N.', '', 'green', y=150, h=34))
u5 = (t(180, 22, '17.2 s → 10.8 s', 9.4, 'acc', bold=True) + t(180, 56, 'max task 5.5 s → 0.8 s', 8.4, 'ink2') + cap('Our lab.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Ranking inside a hot key',
              'Skewed windows. (Typical; timings from our lab.)',
              'Skewed window', 'Windows over a hot key need the hot key handled separately or a two-stage top-N', [u1, u2, u3, u4, u5],
              ['Window.', 'Huge task.', 'Split.', 'Two-stage.', 'Result.'],
              hid='scenario-window')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>One key, one task</h2>
  <p>Left: real outputs. Right: why skew happens and how each fix spreads it.</p>
''' + two + '''
  <p>Three live scenarios follow: a stuck join, NULL keys, and ranking inside a hot key.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Skew at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'sellers', 11, 'blue', bold=True) + t(60, 58, 'marketplace', 7.4, 'ink2'),
    '1. Marketplaces',
    'A few big sellers or restaurants dominate orders; joins on seller_id need AQE or salting.',
    ['Big seller', '*salt / AQE', 'Even tasks']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'NULL', 12, 'green', bold=True) + t(60, 58, 'keys', 7.4, 'ink2'),
    '2. Guest users',
    'Events without a user_id share one NULL key; filtering them before joins removes the skew.',
    ['NULL keys', '*filter', 'Balanced join']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'bots', 12, 'violet', bold=True) + t(60, 58, 'clicks', 7.4, 'ink2'),
    '3. Clickstreams',
    'A bot generating millions of clicks becomes a hot session; handle it separately or drop it.',
    ['Bot session', '*isolate', 'Normal sessions']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'geo', 12, 'acc', bold=True) + t(60, 58, 'cities', 7.4, 'ink2'),
    '4. City-level reports',
    'Metro cities dominate; aggregations stay fast thanks to partial aggregation.',
    ['City key', '*partial agg', 'Fast groupBy']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'UI', 12, 'acc', bold=True) + t(60, 58, 'max/median', 7.4, 'ink2'),
    '5. Monitoring',
    'Alerts fire when a stage’s max task time exceeds 5x its median.',
    ['Task metrics', '*ratio > 5', 'Alert']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> partitions in <a href="../01-partitions-and-shuffle-partitions/">8.1</a>, join strategies in <a href="../02-join-strategies/">8.2</a>, windows in <a href="../../06-transformations/03-window-functions/">6.3</a>, AQE in <a href="../../07-spark-sql/04-adaptive-query-execution/">7.4</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
