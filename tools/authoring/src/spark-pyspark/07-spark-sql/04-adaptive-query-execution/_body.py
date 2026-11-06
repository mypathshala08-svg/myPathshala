import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
C = 'l74_aqe.txt'
def sec(a, b=None, drop=()):
    s = capsec(C, a, b, drop)
    s = re.sub(r'#\d+L?', '', s)
    return '\n'.join(l if len(l) <= 140 else l[:137] + ' …' for l in s.split('\n'))

def bars(x, y, sizes, tone='card', label=''):
    o = t(x, y - 6, label, 7.2, 'ink2', anchor='start', bold=True) if label else ''
    for k, s in enumerate(sizes):
        o += box(x + k * 16, y + (60 - s), 12, s, tone if s < 45 else 'acc', rx=2)
    return o

# ---------------------------------------------------------------- story
sc_ = (bars(14, 40, [4, 3, 5, 2, 4, 3, 2, 5, 3, 4], 'card', '200 tiny partitions') + arrow(180, 70, 210, 70, 'ink3', 1.1) + bars(220, 40, [30, 28, 32, 26, 30], 'green', 'AQE: 5') +
       box(400, 12, 232, 132, 'card') + t(516, 30, 'Measured', 8.6, bold=True) +
       ''.join(t(412, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
           ('groupBy: 204 tasks → 5 tasks', 'green'), ('…1.74 s → 0.62 s', 'green'),
           ('SMJ → broadcast at run time', 'green'), ('…0.89 s → 0.05 s', 'green'),
           ('60% skewed key: 3.67 s (off)', 'red'), ('skew join split: 1.92 s', 'green')])))
scene_svg = scene('Adaptive Query Execution re-optimises a query while it runs, using real sizes measured after each shuffle. We ran the same queries with AQE off and on: shuffle partitions were merged, a join became a broadcast, and a skewed partition was split.', sc_,
                  'AQE fixes plans with <tspan font-weight="700" class="s-acc">real numbers</tspan>, not estimates.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“We tuned shuffle partitions for every job”</h2>
  <div class="story">
    <p class="narration">Before Spark 3, TiffinGo’s platform team kept a spreadsheet of <code>spark.sql.shuffle.partitions</code> values per job: 200 was too many for small days and too few for festival days. One restaurant chain with most of the orders made a join run for an hour on a single task.</p>

{scene_svg}

K> Sir, why can’t Spark choose the right number of partitions itself?
A> Before running, it can only estimate. <b>Adaptive Query Execution</b> waits until each shuffle has finished, looks at the real sizes, and re-plans the rest: it merges small partitions, switches joins to broadcast when a side turns out small, and splits skewed partitions.
R> Is it on by default?
A> Since Spark 3.2. Today we switch it off and on and measure all three features, and learn to read the final plan. All outputs are real (PySpark 4.3.0).
  </div>
</section>
'''

lv = '''
LEVELS> AQE at three levels
L1> Packing parcels
      <ul>
        <li>You booked 200 trucks before knowing the parcels. When they turn out to be few, you send 5 full trucks instead (coalescing).</li>
        <li>A parcel you expected to be heavy is light: hand-carry it instead of booking a truck (switch to broadcast).</li>
        <li>One giant parcel: split it across several trucks (skew join).</li>
      </ul>
L2> The API
      <ul>
        <li><code>spark.sql.adaptive.enabled</code> (true), <code>…coalescePartitions.enabled</code>, <code>…advisoryPartitionSizeInBytes</code> (64 MB).</li>
        <li><code>spark.sql.adaptive.autoBroadcastJoinThreshold</code> (defaults to the normal threshold), <code>…skewJoin.enabled</code>, <code>…skewedPartitionFactor</code> (5), <code>…skewedPartitionThresholdInBytes</code> (256 MB).</li>
        <li>Plans show <code>AdaptiveSparkPlan isFinalPlan=…</code>, <code>AQEShuffleRead coalesced</code>, <code>SortMergeJoin(skew=true)</code>.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>groupBy city: AQE off ran 204 tasks, on ran 5; 1.74 s → 0.62 s.</li>
        <li>With static broadcast disabled, AQE still turned the join into a broadcast at run time: 0.89 s → 0.05 s.</li>
        <li>A key with 60% of rows: 3.67 s without AQE, 2.57 s with coalescing only, 1.92 s with skew-join splitting.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Adaptive Query Execution</h2>
''' + def_block(
    '<b>Adaptive Query Execution (AQE)</b> re-optimises a query at run time using statistics collected from completed <b>query stages</b>, which are delimited by shuffles and broadcasts. After each stage materialises, Spark re-plans the remaining query with the actual output sizes. Its main optimisations are <b>coalescing post-shuffle partitions</b> into fewer partitions close to an advisory size, <b>switching join strategies</b> (sort-merge to broadcast hash join, or to shuffled hash join) when a side is found to be small, and <b>optimising skew joins</b> by splitting oversized partitions and replicating the matching partition of the other side. AQE is enabled by default since Spark 3.2 (<code>spark.sql.adaptive.enabled</code>).',
    'AQE lets Spark change its plan while the query runs. After each shuffle it knows the real data sizes, so it can merge tiny partitions, use a broadcast join when a table turns out small, and split a partition that is much bigger than the rest.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Query stage', 'Part of a plan between shuffles/broadcasts.'),
    ('Runtime statistics', 'Real sizes of shuffle outputs.'),
    ('Coalescing', 'Merging small shuffle partitions.'),
    ('Advisory partition size', 'Target size after coalescing (64 MB).'),
    ('Join switching', 'SMJ → broadcast at run time.'),
    ('Skew join', 'Split big partitions, replicate the other side.'),
    ('AQEShuffleRead', 'Plan node reading coalesced/split partitions.'),
    ('isFinalPlan', 'true once the query has run.'),
]) + '''

  <h3>The three main optimisations</h3>
''' + table(['Feature', 'Problem it fixes', 'Lab (AQE off → on)'], [
    ['Coalesce partitions', '200 tiny tasks after a shuffle', '204 → 5 tasks, 1.74 → 0.62 s'],
    ['Switch to broadcast', 'Wrong size estimate before running', 'SMJ → BHJ, 0.89 → 0.05 s'],
    ['Skew join', 'One huge partition holds a hot key', '3.67 → 1.92 s, plan SortMergeJoin(skew=true)'],
], minw=620) + lv + '''
EXAM> “What does AQE do?” It re-optimises queries at run time using statistics from completed shuffle stages: it coalesces small shuffle partitions, converts sort-merge joins to broadcast joins when a side is small, and splits skewed partitions in joins. It is on by default since Spark 3.2; it reduces the need to hand-tune shuffle partitions but cannot fix every skew or bad data layout.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Settings worth knowing</h2>
''' + table(['Setting', 'Default', 'Effect'], [
    ['<code>spark.sql.adaptive.enabled</code>', 'true', 'Master switch'],
    ['<code>…coalescePartitions.enabled</code>', 'true', 'Merge small partitions'],
    ['<code>…advisoryPartitionSizeInBytes</code>', '64 MB', 'Target size for coalescing and skew splits'],
    ['<code>…autoBroadcastJoinThreshold</code>', 'same as static', 'Runtime broadcast limit (can differ from the static one)'],
    ['<code>…skewJoin.skewedPartitionFactor</code>', '5', 'Skewed if > factor × median …'],
    ['<code>…skewJoin.skewedPartitionThresholdInBytes</code>', '256 MB', '… and larger than this'],
    ['<code>spark.sql.shuffle.partitions</code>', '200', 'Starting point before coalescing; set high enough'],
], minw=640) + '''
WARN> AQE’s skew handling only kicks in when a partition is both <b>5× the median</b> and over <b>256 MB</b> by default, and only for joins (sort-merge and shuffled hash), not for aggregations. Our small lab had to lower the thresholds to see it. On real clusters check the final plan for <code>skew=true</code>; if a hot key still dominates, salt it (Lesson 8.3).
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>AQE off and on</h2>
  <p>All outputs are real: PySpark 4.3.0, local mode with 4 cores, 5,000,000 orders, default 200 shuffle partitions. Tasks and stages are counted from the Spark REST API; each timing is a warm run.</p>
''' + stepper([
    ('Step 1 · Coalescing shuffle partitions',
     code('python', 'l74_aqe.py', 'for aqe in ("false", "true"):\n    spark.conf.set("spark.sql.adaptive.enabled", aqe)\n    o.groupBy("city").agg(F.sum("amount")).collect()\n# then the final plan after running', sec('== 1)', '== 2)')),
     'Without AQE the reduce stage ran all <b>200</b> tasks (plus 4 map tasks) for just 8 cities, most of them empty. With AQE, after the map stage Spark saw a few kilobytes of shuffle data and read it with <b>one</b> task: 5 tasks in total, about 3x faster. The final plan shows <code>isFinalPlan=true</code> and <code>AQEShuffleRead coalesced</code>.'),
    ('Step 2 · A join switched at run time',
     code('python', 'l74_aqe.py', 'spark.conf.set("spark.sql.autoBroadcastJoinThreshold", -1)             # static planner: no broadcast\nspark.conf.set("spark.sql.adaptive.autoBroadcastJoinThreshold", "10485760")\nj = o.join(c.where("plan = \'Gold\' AND state = \'KA\'"), "customer_id").groupBy("plan").count()', sec('== 2)', '== 3)')),
     'The static planner was not allowed to broadcast, so both runs <b>started</b> as a sort-merge join. Without AQE it stayed that way: 0.89 s. With AQE, once the filtered customer side had been materialised and turned out tiny, Spark replaced the join with a <b>broadcast hash join</b> (the final plan contains both: initial and final): 0.05 s.'),
    ('Step 3 · A skewed join',
     code('python', 'l74_aqe.py', 'skew = o.withColumn("rest_id", F.when(F.rand(7) < 0.6, F.lit(1))\n                     .otherwise((F.rand(8) * 2000).cast("int") + 2).cast("long"))\nrests = spark.range(1, 2002).withColumnRenamed("id", "rest_id")…\n# small lab: thresholds lowered to 8 MB, factor 3; broadcast disabled\nskew.join(rests, "rest_id").agg(F.sum("amount")).collect()', sec('== 3)')),
     'Restaurant 1 got <b>60%</b> of all orders, so one join partition held 3 million rows. Without AQE: 3.67 s. AQE with coalescing alone already helped (2.57 s), but the hot partition remained one task. With skew-join handling the final plan shows <code>SortMergeJoin(skew=true)</code> and <code>AQEShuffleRead coalesced and skewed</code>: the big partition was split into several tasks, each joined with a copy of restaurant 1: <b>1.92 s</b>.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('AQE false: 204 tasks, 1.74 s', Y), ('AQE true : 5 tasks, 0.62 s', G), ('AQEShuffleRead coalesced', G)], size=7.4),
    term([('AQE false: SortMergeJoin, 0.89 s', Y), ('AQE true : BroadcastHashJoin, 0.05 s', G)], size=7.4),
    term([('top key share: 0.60', RD), ('off 3.67 s | coalesce 2.57 s', Y), ('skew join 1.92 s, skew=true', G)], size=7.4),
    term([('AdaptiveSparkPlan isFinalPlan=true', G), ('== Final Plan ==', W)], size=7.6),
]
B1 = [
    t(180, 14, 'Merge tiny partitions', 9.4, bold=True) + bars(14, 50, [4, 3, 5, 2, 4, 3, 2, 5, 3, 4], 'card', '200 planned') + arrow(180, 80, 210, 80, 'ink3', 1.1) + bars(240, 50, [40], 'green', 'read as 1') + cap('After the map stage, sizes are known.', '', 'green', y=144, h=30),
    t(180, 14, 'Switch the join', 9.4, bold=True) + opbox(20, 40, 'SortMergeJoin', 'planned', 'acc', 120, 30) + arrow(140, 55, 210, 55, 'ink3', 1.1) + opbox(214, 40, 'BroadcastHashJoin', 'at run time', 'green', 130, 30) + t(180, 100, 'filtered side measured: tiny', 7.4, 'ink2') + cap('Estimates replaced by real sizes.', '', 'green', y=144, h=30),
    t(180, 14, 'Split the hot partition', 9.4, bold=True) + bars(14, 50, [4, 60, 5, 4, 3, 5], 'card', 'before') + arrow(120, 80, 160, 80, 'ink3', 1.1) + bars(170, 50, [4, 15, 15, 15, 15, 5, 4, 3, 5], 'green', 'after: 1 → 4 tasks') + cap('Other side replicated per split.', '', 'green', y=144, h=30),
    t(180, 14, 'Stages, then re-plan', 9.4, bold=True) + flow([('stage 1', 'run', 'blue'), ('stats', 'real sizes', 'violet'), ('re-plan', 'rest', 'green'), ('stage 2', 'run', 'blue')], y=50, w=72, gap=14) + cap('Read the final plan after running.', '', 'blue', y=144, h=30),
]
see_caps = ['204 tasks became 5.', 'Sort-merge became broadcast.', 'Skewed partition split.', 'The final plan.']
behind_caps = ['Coalescing to an advisory size.', 'Runtime join switching.', 'Skew-join optimization.', 'Query stages and re-optimization.']
two = anim_two('Adaptive Query Execution', 'Re-planning with real sizes', 'Real lab outputs', 'What AQE changes', see, B1, see_caps, behind_caps)

e1 = (t(180, 22, 'Spreadsheet of partition counts', 9.4, bold=True) + t(180, 56, 'one value per job and season', 8.4, 'ink2') + cap('Always out of date.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Small day: 200 empty tasks', 9.4, bold=True) + t(180, 56, 'festival day: huge tasks', 8.4, 'ink2') + cap('No single right number.', '', 'amber', y=150, h=34))
e3 = (t(180, 22, 'AQE coalescing', 9.4, bold=True) + t(180, 56, 'set partitions generously, let AQE merge', 8.2, 'ink2') + cap('204 → 5 tasks in our lab.', '', 'green', y=150, h=34))
e4 = (t(180, 22, 'Tune the advisory size', 9.4, bold=True) + t(180, 56, 'advisoryPartitionSizeInBytes', 8.4, 'ink', mono=True) + cap('One knob per platform.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Delete the spreadsheet', 9.4, 'acc', bold=True) + t(180, 56, 'check final plans in the UI', 8.4, 'ink2') + cap('Less manual tuning.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Retiring the partition spreadsheet',
              'Partition coalescing. (Typical; numbers from our lab.)',
              'Coalescing', 'Set shuffle partitions generously and let AQE coalesce them to an advisory size', [e1, e2, e3, e4, e5],
              ['Manual.', 'Wrong both ways.', 'Coalesce.', 'One knob.', 'Done.'],
              hid='scenario-coalesce')
b1 = (t(180, 22, 'Join with a filtered dimension', 9.4, bold=True) + t(180, 56, 'dim 5 GB, filter keeps 0.1%', 8.4, 'ink2') + cap('Estimate says big.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'Static plan: sort-merge', 9.4, bold=True) + t(180, 56, 'both sides shuffled', 8.4, 'ink2') + cap('Slow.', '', 'amber', y=150, h=34))
b3 = (t(180, 22, 'AQE measures the filtered side', 9.4, bold=True) + t(180, 56, '5 MB after the filter', 8.4, 'ink2') + cap('Below the threshold.', '', 'green', y=150, h=34))
b4 = (t(180, 22, 'Switch to broadcast', 9.4, bold=True) + t(180, 56, 'big side no longer shuffled', 8.4, 'ink2') + cap('0.89 → 0.05 s in our lab.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Check the final plan', 9.4, 'acc', bold=True) + t(180, 56, 'Spark UI SQL tab', 8.4, 'ink2') + cap('Not the initial explain().', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'An estimate that was 1,000x too big',
              'Runtime join switching. (Typical; timings from our lab.)',
              'Join switching', 'AQE replaces sort-merge joins with broadcast joins when a side is measured small at run time', [b1, b2, b3, b4, b5],
              ['Filtered dim.', 'SMJ.', 'Measured.', 'Broadcast.', 'Final plan.'],
              hid='scenario-switch')
u1 = (t(180, 22, 'One chain has 60% of orders', 9.4, bold=True) + t(180, 56, 'join on restaurant_id', 8.4, 'ink2') + cap('One task runs for an hour.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'AQE skew join', 9.4, bold=True) + t(180, 56, 'splits the big partition', 8.4, 'ink2') + cap('If > 5x median and > 256 MB.', '', 'green', y=150, h=34))
u3 = (t(180, 22, 'Final plan: skew=true', 9.4, bold=True) + t(180, 56, 'AQEShuffleRead … skewed', 8.4, 'ink', mono=True) + cap('Our Step 3.', '', 'green', y=150, h=34))
u4 = (t(180, 22, 'Not for aggregations', 9.4, bold=True) + t(180, 56, 'groupBy on the hot key still skewed', 8.4, 'ink2') + cap('Partial agg helps sums.', '', 'amber', y=150, h=34))
u5 = (t(180, 22, 'Salting as a fallback', 9.4, 'acc', bold=True) + t(180, 56, 'Lesson 8.3', 8.4, 'ink2') + cap('When AQE is not enough.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'One restaurant chain, one slow task',
              'Skew joins with AQE. (Typical; behaviour from our lab.)',
              'Skew join', 'AQE splits skewed join partitions above its thresholds; check skew=true and fall back to salting', [u1, u2, u3, u4, u5],
              ['Hot key.', 'Split.', 'Verify.', 'Limits.', 'Salting.'],
              hid='scenario-skew')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Re-planning with real sizes</h2>
  <p>Left: real outputs. Right: what AQE changes.</p>
''' + two + '''
  <p>Three live scenarios follow: retiring manual partition tuning, an estimate 1,000x too big, and a hot key.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>AQE at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'varied', 11, 'blue', bold=True) + t(60, 58, 'volumes', 7.4, 'ink2'),
    '1. Jobs with changing volumes',
    'Daily jobs whose input varies 10x between normal and festival days run well without per-day tuning.',
    ['Any day', '*AQE coalesce', 'Right task count']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'BI', 12, 'green', bold=True) + t(60, 58, 'ad hoc', 7.4, 'ink2'),
    '2. Ad-hoc SQL',
    'Analyst queries with unpredictable filters get broadcast joins chosen from real sizes.',
    ['Ad-hoc query', '*runtime switch', 'Fast join']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'skew', 12, 'violet', bold=True) + t(60, 58, 'joins', 7.4, 'ink2'),
    '3. Marketplace data',
    'Big sellers or restaurants create hot keys; AQE splits their join partitions.',
    ['Hot key', '*skew join', 'Balanced tasks']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'files', 12, 'acc', bold=True) + t(60, 58, 'fewer', 7.4, 'ink2'),
    '4. Fewer output files',
    'Coalesced shuffle partitions also mean fewer, larger output files.',
    ['Shuffle', '*coalesce', 'Fewer files']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'UI', 12, 'acc', bold=True) + t(60, 58, 'final plan', 7.4, 'ink2'),
    '5. Performance reviews',
    'Engineers read final plans in the Spark UI to see which AQE rules fired.',
    ['Spark UI', '*final plan', 'Insight']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> shuffles in <a href="../../02-rdds/04-narrow-vs-wide-and-the-shuffle/">2.4</a>, join strategies in <a href="../../06-transformations/02-joins/">6.2</a>, plans in <a href="../03-catalyst-and-explain/">7.3</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
