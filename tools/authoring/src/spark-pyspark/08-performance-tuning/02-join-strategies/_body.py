import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
C = 'l82_joins.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)

def side(x, y, label, sub, tone, w=92, h=40):
    return opbox(x, y, label, sub, tone, w, h)

# ---------------------------------------------------------------- story
sc_ = (side(14, 30, 'orders', '5M rows', 'blue', 100, 40) + side(14, 96, 'customers', '4,000 rows', 'green', 100, 40) +
       arrow(116, 116, 176, 80, 'green', 1.2) + t(150, 108, 'copy', 7, 'green') + arrow(116, 50, 176, 62, 'ink3', 1.1) +
       opbox(180, 54, 'BroadcastHashJoin', 'no shuffle of orders', 'green', 190, 34) +
       box(400, 12, 232, 132, 'card') + t(516, 30, 'Measured (5M orders)', 8.6, bold=True) +
       ''.join(t(412, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
           ('broadcast   : 1.55 s,   8 tasks', 'green'), ('shuffle_hash: 4.53 s, 208 tasks', 'amber'),
           ('sort-merge  : 6.73 s, 208 tasks', 'red'), ('bucketed SMJ: 1.68 s, 0 Exchange', 'green'),
           ('plain SMJ   : 5.31 s, 2 Exchange', 'amber'), ('5M broadcast: works, risky', 'red')])))
scene_svg = scene('Spark joins two tables using one of several physical strategies. We forced each strategy with hints on 5 million orders joined to 4,000 customers and timed them, then compared a bucketed join with a normal one.', sc_,
                  'The fastest join is the one that <tspan font-weight="700" class="s-acc">does not shuffle</tspan> the big table.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Same join, four times faster”</h2>
  <div class="story">
    <p class="narration">TiffinGo’s loyalty job joins every order with the customer tier table. After someone set <code>spark.sql.autoBroadcastJoinThreshold=-1</code> to “fix” an out-of-memory error elsewhere, the job silently became 4x slower.</p>

{scene_svg}

K> Sir, a join is a join. How can the same join be 4x slower?
A> Spark has several <b>physical join strategies</b>. If one side is small, it copies it to every executor and never moves the big table. Otherwise it shuffles both sides by the key, and then either sorts them or builds hash tables.
R> And we can choose?
A> Spark chooses using size estimates and thresholds, and you can override it with <b>hints</b>. Today we force each strategy, time it, read the plans, and see how <b>bucketing</b> removes the shuffle for repeated joins. All outputs are real (PySpark 4.3.0).
  </div>
</section>
'''

lv = '''
LEVELS> Join strategies at three levels
L1> Matching guests to tables
      <ul>
        <li>Broadcast: give every waiter a copy of the short guest list. Nobody moves.</li>
        <li>Sort-merge: both long lists are sorted by name and walked together.</li>
        <li>Shuffle hash: split both lists by first letter, then use a lookup table per letter.</li>
      </ul>
L2> The API
      <ul>
        <li><code>F.broadcast(df)</code> or <code>df.hint("broadcast")</code>, <code>"merge"</code>, <code>"shuffle_hash"</code>, <code>"shuffle_replicate_nl"</code>; SQL <code>/*+ BROADCAST(c) */</code>.</li>
        <li><code>spark.sql.autoBroadcastJoinThreshold</code> (10 MB), <code>spark.sql.join.preferSortMergeJoin</code> (true).</li>
        <li><code>df.write.bucketBy(n, "key").sortBy("key").saveAsTable(...)</code>.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>Broadcast 1.55 s (8 tasks), shuffled hash 4.53 s, sort-merge 6.73 s (208 tasks each).</li>
        <li>The broadcast plan had 0 hash Exchanges; sort-merge had 2.</li>
        <li>Bucketed tables: sort-merge with 0 Exchanges, 1.68 s vs 5.31 s.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Physical join strategies</h2>
''' + def_block(
    'Spark SQL implements equi-joins with three main physical operators. A <b>broadcast hash join</b> (BHJ) sends the smaller relation to every executor and builds a hash table there, so the larger side is not shuffled; it is chosen when a side’s estimated size is below <code>spark.sql.autoBroadcastJoinThreshold</code> (10 MB) or a broadcast hint is given. A <b>sort-merge join</b> (SMJ) shuffles both sides by the join key, sorts each partition and merges them; it is the default for large inputs. A <b>shuffled hash join</b> (SHJ) shuffles both sides and builds a hash table from the smaller side per partition, avoiding the sort. Non-equi joins use a <b>broadcast nested loop join</b> or a <b>cartesian product</b>. Hints (<code>BROADCAST</code>, <code>MERGE</code>, <code>SHUFFLE_HASH</code>, <code>SHUFFLE_REPLICATE_NL</code>) override the choice; bucketed tables can skip the shuffle.',
    'Spark can join by copying a small table to every machine (broadcast), or by moving both tables so matching keys meet and then sorting (sort-merge) or hashing (shuffled hash). Broadcast avoids moving the big table and is usually fastest; the others work for any size. Hints let you choose.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('BHJ', 'Broadcast hash join: small side copied.'),
    ('SMJ', 'Sort-merge join: shuffle + sort both.'),
    ('SHJ', 'Shuffled hash join: shuffle + hash.'),
    ('BNLJ', 'Broadcast nested loop: non-equi joins.'),
    ('Join hint', 'Tells Spark which strategy to use.'),
    ('autoBroadcastJoinThreshold', '10 MB default; -1 disables.'),
    ('BroadcastExchange', 'Plan node that ships the small side.'),
    ('Bucketing', 'Pre-shuffled, pre-sorted table files.'),
]) + '''

  <h3>The strategies side by side</h3>
''' + table(['Strategy', 'Shuffles', 'Best when', 'Lab (5M × 4,000)'], [
    ['Broadcast hash', 'Neither side (small side copied)', 'One side small (≤ ~10–100 MB)', '1.55 s, 8 tasks'],
    ['Shuffled hash', 'Both', 'One side much smaller, fits in memory per partition', '4.53 s, 208 tasks'],
    ['Sort-merge', 'Both (+ sort)', 'Both sides large', '6.73 s, 208 tasks'],
    ['Cartesian / BNLJ', 'Varies', 'Non-equi conditions only', 'hint gave CartesianProduct'],
    ['Bucketed SMJ', 'None (pre-bucketed)', 'Same big join repeated', '1.68 s vs 5.31 s'],
], minw=660) + lv + '''
EXAM> “Explain Spark join strategies.” Broadcast hash join copies the small side to all executors and avoids shuffling the big side; it is chosen below <code>autoBroadcastJoinThreshold</code> (10 MB) or with a hint. Sort-merge join shuffles and sorts both sides and is the default for large tables. Shuffled hash join shuffles both and hashes the smaller side per partition. Non-equi joins use broadcast nested loop or cartesian joins. Bucketing on the join key lets sort-merge skip the shuffle.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Hints in DataFrame and SQL</h2>
''' + table(['Hint', 'DataFrame', 'SQL', 'Plan in our lab'], [
    ['Broadcast', '<code>F.broadcast(c)</code> / <code>c.hint("broadcast")</code>', '<code>/*+ BROADCAST(c) */</code>', 'BroadcastHashJoin'],
    ['Merge', '<code>c.hint("merge")</code>', '<code>/*+ MERGE(c) */</code>', 'SortMergeJoin'],
    ['Shuffle hash', '<code>c.hint("shuffle_hash")</code>', '<code>/*+ SHUFFLE_HASH(c) */</code>', 'ShuffledHashJoin'],
    ['Replicate NL', '<code>c.hint("shuffle_replicate_nl")</code>', '<code>/*+ SHUFFLE_REPLICATE_NL(c) */</code>', 'CartesianProduct'],
], minw=640) + '''
WARN> A broadcast hint is an order, not a suggestion: Spark will try to collect the side on the driver and send it to every executor, even a huge one. Our forced broadcast of 5 million rows worked on a 3 GB driver (5.32 s), but on a cluster a mis-estimated side causes driver OOM or a broadcast timeout. Setting the threshold to <code>-1</code> everywhere is the opposite mistake: every small dimension join becomes a shuffle.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Forcing each strategy</h2>
  <p>All outputs are real: PySpark 4.3.0, <code>local[4]</code>, AQE off (so the plan does not change at run time), 5,000,000 orders joined on <code>customer_id</code> to 4,000 customers. Strategies are read from the executed plan; timings are warm runs.</p>
''' + stepper([
    ('Step 1 · Spark’s automatic choice',
     code('python', 'l82_joins.py', 'cust = spark.range(1, 4001).select(F.col("id").cast("int").alias("customer_id"), (F.col("id") % 5).alias("tier"))\nprint(strat(o.join(cust, "customer_id")))\nspark.conf.set("spark.sql.autoBroadcastJoinThreshold", -1)\nprint(strat(o.join(cust, "customer_id")))', sec('default', '== 2)')),
     'The customer side is tiny, far below 10 MB, so Spark picked a <b>broadcast hash join</b> by itself. Disabling the threshold with <code>-1</code> forced it back to <b>sort-merge</b>, the default for “big” joins.'),
    ('Step 2 · Hints and timings',
     code('python', 'l82_joins.py', 'for h in ("broadcast", "merge", "shuffle_hash", "shuffle_replicate_nl"):\n    print(h, strat(o.join(cust.hint(h), "customer_id")))\nfor h in ("broadcast", "merge", "shuffle_hash"):\n    run(f"join with {h}", sink(o.join(cust.hint(h), "customer_id")))', sec('== 2)', '== 3)')),
     'Each hint produced exactly the requested operator. Broadcast: <b>1.55 s</b> with 8 tasks (just scanning orders). Shuffled hash: <b>4.53 s</b>. Sort-merge: <b>6.73 s</b>, 4.3x slower, with 208 tasks because both sides were shuffled into 200 partitions and sorted. <code>shuffle_replicate_nl</code> on an equi-join gave a <b>CartesianProduct</b>: never use it for normal keys.'),
    ('Step 3 · Read the plan, count Exchanges',
     code('python', 'l82_joins.py', 'for h in ("broadcast", "merge"):\n    p = o.join(cust.hint(h), "customer_id")._jdf.queryExecution().executedPlan().toString()\n    print(h, p.count("Exchange hashpartitioning"), p.count("BroadcastExchange"))', sec('== 3)', '== 4)')),
     'The quickest way to understand a join’s cost: count <code>Exchange hashpartitioning</code> nodes. Each is a full shuffle of one side. Broadcast had <b>0</b> (plus one cheap BroadcastExchange of 4,000 rows); sort-merge had <b>2</b>, moving all 5 million orders across the network.'),
    ('Step 4 · Forcing a broadcast of a big side',
     code('python', 'l82_joins.py', 'o2 = o.select("order_id", "amount")          # 5,000,000 rows\nrun("broadcast 5M-row side", sink(o.join(F.broadcast(o2), "order_id")))\nrun("sort-merge same join",  sink(o.join(o2, "order_id")))', sec('== 4)', '== 5)')),
     'It worked here and was even faster (5.32 s vs 7.62 s), because we run in one process with a 3 GB driver. On a cluster the driver collects the side, builds the hash table and ships it to every executor: a few hundred MB per executor, times every concurrent job. Spark refuses broadcasts above 8 GB and fails on driver memory or <code>spark.sql.broadcastTimeout</code> (300 s) long before that.'),
    ('Step 5 · Bucketing removes the shuffle',
     code('python', 'l82_joins.py', 'o.write.bucketBy(16, "customer_id").sortBy("customer_id").saveAsTable("ob")\ncust.write.bucketBy(16, "customer_id").sortBy("customer_id").saveAsTable("cb")\nb = spark.table("ob").join(spark.table("cb"), "customer_id")   # threshold -1', sec('== 5)')),
     'Both tables were written in 16 buckets hashed by <code>customer_id</code>. The join is still a sort-merge join, but with <b>0 Exchanges</b>: bucket 3 of orders only needs bucket 3 of customers. <b>1.68 s vs 5.31 s</b>. The shuffle was paid once at write time, so bucketing pays off when the same big join runs many times. Both sides need the same bucket column and compatible bucket counts.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('small dim -> BroadcastHashJoin', G), ('threshold -1 -> SortMergeJoin', Y)], size=7.6),
    term([('broadcast   : 1.55 s,   8 tasks', G), ('shuffle_hash: 4.53 s, 208 tasks', Y), ('merge       : 6.73 s, 208 tasks', RD)], size=7.4),
    term([('broadcast: Exchange 0, Broadcast 1', G), ('merge    : Exchange 2, Broadcast 0', RD)], size=7.4),
    term([('bucketed SMJ: Exchange 0, 1.68 s', G), ('plain SMJ   : Exchange 2, 5.31 s', Y)], size=7.4),
]
def ex(n, x0=30, y=46):
    return ''.join(box(x0 + k * 28, y, 22, 22, 'blue', rx=3) for k in range(n))
B1 = [
    t(180, 14, 'Size decides', 9.4, bold=True) + opbox(20, 40, 'customers', '≈ 60 KB', 'green', 110, 32) + arrow(132, 56, 226, 56, 'green', 1.1) + t(180, 50, '≤ 10 MB ?', 8, 'ink2') + opbox(230, 40, 'broadcast', 'yes', 'green', 110, 32) + cap('Else: sort-merge by default.', '', 'blue', y=144, h=30),
    t(180, 14, 'Broadcast: big side stays put', 9.4, bold=True) + t(80, 38, 'orders partitions (stay)', 7, 'blue') + ex(4) + ''.join(box(36 + k * 28, 80, 10, 10, 'green', rx=2) for k in range(4)) + t(260, 62, 'copy of dim', 7.2, 'green') + t(260, 92, 'per executor', 7.2, 'green') + cap('8 tasks, no shuffle.', '', 'green', y=144, h=30),
    t(180, 14, 'Sort-merge: both move', 9.4, bold=True) + flow([('orders', 'shuffle', 'acc'), ('customers', 'shuffle', 'acc'), ('sort', 'both', 'violet'), ('merge', 'walk', 'blue')], y=50, w=72, gap=14) + cap('2 Exchanges, 208 tasks.', '', 'amber', y=144, h=30),
    t(180, 14, 'Bucketed: pre-shuffled', 9.4, bold=True) + ''.join(opbox(20 + k * 84, 46, f'bucket {k}', 'o ⋈ c', 'green', 74, 30) for k in range(4)) + cap('Matching buckets join locally.', '', 'green', y=144, h=30),
]
see_caps = ['Automatic choice.', 'Forced by hints.', 'Exchanges in the plan.', 'Bucketing.']
behind_caps = ['Threshold check.', 'Broadcast hash join.', 'Sort-merge join.', 'Bucketed join.']
two = anim_two('Join strategies', 'Who moves, and how much', 'Real lab outputs', 'What Spark does', see, B1, see_caps, behind_caps)

e1 = (t(180, 22, 'Threshold set to -1', 9.4, bold=True) + t(180, 56, 'to stop one OOM elsewhere', 8.4, 'ink2') + cap('Global setting.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Every dim join shuffles', 9.4, bold=True) + t(180, 56, '1.55 s → 6.73 s in our lab', 8.4, 'ink2') + cap('4x slower, silently.', '', 'red', y=150, h=34))
e3 = (t(180, 22, 'Restore the default', 9.4, bold=True) + t(180, 56, '10 MB (or a bit higher)', 8.4, 'ink2') + cap('Small sides broadcast again.', '', 'green', y=150, h=34))
e4 = (t(180, 22, 'Fix the real OOM locally', 9.4, bold=True) + t(180, 56, 'hint("merge") on that one join', 8.4, 'ink', mono=True) + cap('Targeted, not global.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Check plans in CI', 9.4, 'acc', bold=True) + t(180, 56, 'expect BroadcastHashJoin', 8.4, 'ink2') + cap('Catch regressions.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'The global -1',
              'Broadcast threshold regressions. (Typical; timings from our lab.)',
              'Broadcast threshold', 'A global broadcast threshold of -1 made every dimension join a sort-merge join', [e1, e2, e3, e4, e5],
              ['-1.', 'Slow.', 'Default.', 'Local fix.', 'CI check.'],
              hid='scenario-threshold')
b1 = (t(180, 22, 'Dim filtered at run time', 9.4, bold=True) + t(180, 56, 'estimate 2 GB, real 3 MB', 8.4, 'ink2') + cap('Optimizer guesses wrong.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'Plan: sort-merge', 9.4, bold=True) + t(180, 56, 'big fact table shuffled', 8.4, 'ink2') + cap('Slow.', '', 'amber', y=150, h=34))
b3 = (t(180, 22, 'Option 1: AQE', 9.4, bold=True) + t(180, 56, 'switches at run time (7.4)', 8.4, 'ink2') + cap('Automatic.', '', 'green', y=150, h=34))
b4 = (t(180, 22, 'Option 2: hint', 9.4, bold=True) + t(180, 56, 'F.broadcast(dim_filtered)', 8.4, 'ink', mono=True) + cap('You know it is small.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Verify in the SQL tab', 9.4, 'acc', bold=True) + t(180, 56, 'BroadcastHashJoin in final plan', 8.4, 'ink2') + cap('Measure.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'When the optimizer guesses wrong',
              'Broadcast hints. (Typical; behaviour from our lab.)',
              'Broadcast hint', 'Use AQE or a broadcast hint when a side is small after filtering', [b1, b2, b3, b4, b5],
              ['Wrong estimate.', 'SMJ.', 'AQE.', 'Hint.', 'Verify.'],
              hid='scenario-hint')
u1 = (t(180, 22, 'Orders ⋈ deliveries, hourly', 9.4, bold=True) + t(180, 56, 'both 500 GB, same key', 8.4, 'ink2') + cap('Two full shuffles every hour.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'Bucket both by order_id', 9.4, bold=True) + t(180, 56, 'bucketBy(512, "order_id")', 8.4, 'ink', mono=True) + cap('Shuffle paid once at write.', '', 'green', y=150, h=34))
u3 = (t(180, 22, 'Join plan: no Exchange', 9.4, bold=True) + t(180, 56, '1.68 s vs 5.31 s in our lab', 8.4, 'ink2') + cap('Each hour saves the shuffle.', '', 'green', y=150, h=34))
u4 = (t(180, 22, 'Catch: bucket rules', 9.4, bold=True) + t(180, 56, 'same key; table must be read as a table', 8.2, 'ink2') + cap('Not just a parquet path.', '', 'amber', y=150, h=34))
u5 = (t(180, 22, 'Modern alternative', 9.4, 'acc', bold=True) + t(180, 56, 'Iceberg/Delta clustering + SPJ', 8.4, 'ink2') + cap('Storage-partitioned joins.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'The hourly big-to-big join',
              'Bucketing to avoid repeated shuffles. (Typical; timings from our lab.)',
              'Bucketing', 'Bucket both tables on the join key so repeated sort-merge joins skip the shuffle', [u1, u2, u3, u4, u5],
              ['Big × big.', 'Bucket.', 'No shuffle.', 'Rules.', 'Alternatives.'],
              hid='scenario-bucket')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Who moves, and how much</h2>
  <p>Left: real outputs. Right: how each strategy moves data.</p>
''' + two + '''
  <p>Three live scenarios follow: a global threshold mistake, a wrong size estimate, and a repeated big-to-big join.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Join strategies at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'star', 12, 'blue', bold=True) + t(60, 58, 'schema', 7.4, 'ink2'),
    '1. Fact-to-dimension joins',
    'Orders joined to cities, restaurants and plans: every dimension under the threshold is broadcast.',
    ['Fact', '*broadcast dims', 'No shuffle']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'big×big', 10, 'green', bold=True) + t(60, 58, 'SMJ', 7.4, 'ink2'),
    '2. Large-to-large joins',
    'Sessions joined to clickstream use sort-merge; tuning focuses on partitions and skew.',
    ['Big', '*sort-merge', 'Big']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'bucket', 11, 'violet', bold=True) + t(60, 58, 'tables', 7.4, 'ink2'),
    '3. Repeated joins',
    'Tables joined many times a day on the same key are bucketed or clustered once.',
    ['Write once', '*bucketBy', 'Join many']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'range', 11, 'acc', bold=True) + t(60, 58, 'joins', 7.4, 'ink2'),
    '4. Range joins',
    'Matching GPS pings to time windows uses non-equi conditions; keep one side small to get a broadcast nested loop join.',
    ['ts BETWEEN', '*BNLJ (small side)', 'Matches']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'hint', 12, 'acc', bold=True) + t(60, 58, 'review', 7.4, 'ink2'),
    '5. Code reviews',
    'Teams require a comment on every broadcast hint explaining why the side is small.',
    ['Hint', '*size proof', 'Safe merge']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> join types in <a href="../../06-transformations/02-joins/">6.2</a>, plans in <a href="../../07-spark-sql/03-catalyst-and-explain/">7.3</a>, AQE in <a href="../../07-spark-sql/04-adaptive-query-execution/">7.4</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
