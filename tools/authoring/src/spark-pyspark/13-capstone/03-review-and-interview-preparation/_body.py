import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
RV = 'l133_review.txt'
def sec(a, b=None, drop=()):
    return capsec(RV, a, b, drop)

def bars(x, y, vals, labels, tones):
    o = ''
    mx = max(vals)
    for k, (v, l, tn) in enumerate(zip(vals, labels, tones)):
        w = 220 * v / mx
        o += t(x, y + k * 30 + 12, l, 7.4, 'ink', anchor='start') + box(x + 92, y + k * 30, w, 18, tn, rx=3) + t(x + 98 + w, y + k * 30 + 12, f'{v:.2f} s', 7.4, 'ink', anchor='start', mono=True)
    return o

sc_ = (box(14, 12, 300, 132, 'card') + t(164, 30, 'Review checklist', 8.6, bold=True) +
       ''.join(t(26, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
           ('files   : 56 → 14', 'green'), ('join    : BroadcastHashJoin', 'green'),
           ('pruning : PartitionFilters', 'green'), ('skew    : 5.30 s → 0.59 s', 'amber'),
           ('gate    : 5.34% → STOP', 'red'), ('story   : problem → impact', 'violet')])) +
       box(330, 12, 300, 132, 'card') + t(480, 30, 'Interview', 8.6, bold=True) +
       ''.join(t(342, 52 + k * 16, s, 7.2, 'ink2', anchor='start') for k, s in enumerate([
           '“Walk me through your project.”', '“Why broadcast?”', '“What if data doubles?”',
           '“How do you know it is correct?”', '“What would you change?”', '“Explain a shuffle.”'])))
scene_svg = scene('Capstone review: prove the pipeline is efficient and correct using the physical plan, file counts and timings, then turn the project into interview answers covering the whole course.', sc_,
                  'Evidence, then <tspan font-weight="700" class="s-acc">the story</tspan>.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Convince me it is good”</h2>
  <div class="story">
    <p class="narration">The pipeline from Lesson 13.2 runs green every night. Before it goes to the leadership dashboard, the platform lead reviews it, and next month Kiran will describe it in job interviews.</p>

{scene_svg}

K> Sir, it works. Isn’t that enough?
A> Working is the minimum. A reviewer asks: how many files does it write, which join did Spark choose, does a date filter skip the other days, what happens with skew, and what stops a bad day? You answer with <b>evidence</b>: plans, counts, timings.
R> And the interview?
A> Same evidence, told as a story: problem, data, design, the hard parts, the numbers, and what you would change. Then we revise the whole course with the questions interviewers actually ask. All outputs are real (PySpark 4.3.0).
  </div>
</section>
'''

lv = '''
LEVELS> The review at three levels
L1> A building inspection
      <ul>
        <li>The house stands, but the inspector checks wiring, plumbing and the fire exit. Your pipeline’s wiring is its plan; its fire exit is the quality gate.</li>
      </ul>
L2> What to verify
      <ul>
        <li>Output layout: one file per partition, sensible sizes (Lesson 5.3).</li>
        <li>Physical plan: the intended join strategy and partition pruning (Lessons 7.3, 8.2).</li>
        <li>Behaviour under stress: skew, bad data, re-runs.</li>
      </ul>
L3> Turning it into answers
      <ul>
        <li>STAR-style: Situation (TiffinGo, 842k messy orders), Task (revenue + churn features), Action (profile, medallion, tests, gates, broadcast), Result (0.59% quarantined, 25 s, identical on cluster).</li>
        <li>Expect follow-ups that go one level deeper into each choice; every number above is your proof.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>A pipeline review</h2>
''' + def_block(
    'A <b>pipeline review</b> verifies a data job against its non-functional requirements using observable evidence: the <b>physical plan</b> (<code>explain</code>, Spark UI) confirms join strategies, partition pruning and adaptive execution; <b>output inspection</b> confirms file counts and layout; <b>controlled experiments</b> compare alternatives (e.g. broadcast vs sort-merge under skew); and <b>failure tests</b> confirm that data-quality gates stop bad runs. A <b>project narrative</b> for interviews presents the same evidence as situation, task, actions with trade-offs, and measurable results.',
    'Check with real evidence that the pipeline is fast, writes tidy files, uses the right join and stops on bad data. Then explain the project as a short story with numbers, ready for interview follow-ups.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Physical plan', 'What Spark actually executes.'),
    ('Partition pruning', 'Skipping folders by filter.'),
    ('isFinalPlan', 'AQE’s re-optimised plan.'),
    ('Small files', 'Many tiny output files.'),
    ('STAR', 'Situation, Task, Action, Result.'),
    ('Trade-off', 'What you gave up for a choice.'),
    ('Follow-up', 'The “why?” after your answer.'),
    ('Evidence', 'Plans, counts, timings.'),
]) + '''

  <h3>The review checklist</h3>
''' + table(['Question', 'Evidence', 'Result (lab)'], [
    ['Tidy output?', 'count files per partition', '14 files (56 without repartition)'],
    ['Right join?', '<code>explain()</code> of the gold join', 'BroadcastHashJoin, AQE final plan'],
    ['Pruning works?', 'filter on order_date in plan', '<code>PartitionFilters</code> present'],
    ['Skew handled?', 'timed alternatives', 'broadcast 0.59 s vs 5.30 s'],
    ['Bad day stopped?', 'inject bad rows, run gate', '5.34% → STOP'],
], minw=620) + lv + '''
EXAM> “How do you verify a Spark job is efficient?” Read the physical plan (join types, exchanges, PartitionFilters, AQE final plan), check the Spark UI for stage times, shuffle sizes and skewed tasks, inspect the output layout for small files, and compare alternatives with measurements, not guesses.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Course revision map: what interviewers ask</h2>
''' + table(['Topic (modules)', 'Must-know answer', 'Your capstone proof'], [
    ['Architecture (1–2)', 'Driver, executors, jobs → stages → tasks; lazy evaluation', 'Steps split at shuffles'],
    ['RDD vs DataFrame (3–4)', 'DataFrames get Catalyst + Tungsten; RDDs only for low-level control', 'All DataFrame code'],
    ['Formats (5)', 'Parquet columnar + pruning; avoid small files', '14 partitioned files'],
    ['Transformations (6)', 'Narrow vs wide; joins; window functions', 'row_number for latest customer'],
    ['SQL (7)', 'Catalyst phases; explain()', 'Plan inspection'],
    ['Performance (8)', 'Broadcast, AQE, skew, caching, partitions', 'Broadcast vs sort-merge timings'],
    ['Streaming (9)', 'Micro-batches, watermarks, checkpoints, exactly-once', 'Next step: stream orders'],
    ['MLlib (10)', 'Pipelines, no leakage, evaluation', 'customer_features for churn'],
    ['Production (11)', 'spark-submit, YARN/K8s, tests, Delta/Iceberg', '--py-files, 5 tests'],
    ['Industry (12)', 'When not to use Spark; Spark 4 ANSI', 'try_cast everywhere'],
], minw=640) + '''
WARN> In interviews, never claim numbers you cannot explain. “Our pipeline processes 842,587 rows in 25 seconds on 4 cores” invites “why 25 and not 5?”. Know where time goes (silver is 12.5 s because it reads and shuffles everything once) and what you would try next.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Reviewing the pipeline with evidence</h2>
  <p>All outputs are real: PySpark 4.3.0, <code>local[4]</code>, on the capstone data from Lessons 13.1–13.2 (lab script <code>jobs/m13/review.py</code>).</p>
''' + stepper([
    ('Step 1 · Output files',
     code('python', 'review.py', 'valid.write.partitionBy("order_date").parquet(tmp1)                              # no repartition\nvalid.repartition("order_date").write.partitionBy("order_date").parquet(tmp2)  # pipeline\ncount_files(tmp1), count_files(tmp2)', sec('== 1)', '== 2)')),
     'Without <code>repartition</code>, each of the 4 tasks writes a file for every day it touches: 56 small files. Repartitioning by the partition column first puts each day in one task: 14 files. At a year of history that is 1,460 vs 365 files.'),
    ('Step 2 · The gold join plan and pruning',
     code('python', 'review.py', 'plan = daily_city_revenue(so, rest)._jdf.queryExecution().executedPlan().toString()\n"BroadcastHashJoin" in plan, "SortMergeJoin" in plan\nso.filter("order_date = \'2026-11-01\'").explain()', sec('== 2)', '== 3)')),
     'The plan confirms the broadcast join and AQE’s final plan. Filtering on the partition column shows <code>PartitionFilters</code>: Spark reads one day’s folder, not fourteen (Lesson 5.3).'),
    ('Step 3 · What if we had not broadcast?',
     code('python', 'review.py', 'spark.conf.set("spark.sql.autoBroadcastJoinThreshold", -1)\nfor aqe in ("false", "true"):\n    spark.conf.set("spark.sql.adaptive.enabled", aqe)\n    timed(lambda: orders.join(rest, "rest_id").groupBy("city").sum("amount").collect())', sec('== 3)', '== 4)')),
     'Restaurant 1 has 30% of orders. A sort-merge join with AQE off took 5.30 s; AQE (coalescing and skew handling) brought it to 1.12 s; the broadcast in the pipeline needs no shuffle of orders at all: 0.59 s, about 9× faster than the naive plan.'),
    ('Step 4 · The gate on a bad day',
     code('python', 'review.py', 'bad = raw.limit(3000).withColumn("amount", F.lit("N/A"))   # partner sends a broken export\nday = raw_day.unionByName(bad)\n_, q = clean_orders(day); pct = q.count() / day.count() * 100\nprint(pct, "STOP" if pct >= 2 else "ok")', sec('== 4)')),
     'Injecting 3,000 “N/A” amounts into a day pushes the quarantine share to 5.34%, above the 2% gate. The job stops before gold, the dashboard keeps yesterday’s numbers, and on-call gets an alert.'),
]) + '''

  <h3>Your 60-second project story</h3>
  <div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Situation:</b> a food-delivery company needed daily city revenue and churn features from messy CSV/JSON exports. <b>Task:</b> build a reliable nightly PySpark pipeline. <b>Action:</b> profiled 842,587 orders and found duplicates, bad and negative amounts, orphans and a 30% skewed restaurant; designed landing/silver/gold with a quarantine; wrote pure transforms with 5 pytest tests; used try_cast for Spark 4 ANSI, a broadcast join for the skew, partitioned Parquet and quality gates. <b>Result:</b> 0.59% of rows quarantined with reasons, 25 s locally and identical results on a cluster, and a gate that stops bad days.</p></div>
</section>
'''

see = [
    term([('without repartition: 56 files', Y), ('pipeline (repartition first): 14 files', G), ('for 14 days', W)], size=7.2),
    term([('BroadcastHashJoin: True', G), ('SortMergeJoin: False', G), ('PartitionFilters: (order_date = ...)', G)], size=7.0),
    term([('sort-merge, AQE off : 5.30 s', RD), ('sort-merge, AQE on  : 1.12 s', Y), ('broadcast           : 0.59 s', G)], size=7.2),
    term([('quarantine_pct: 5.34', RD), ('STOP: too many bad rows', RD), ('(gate < 2%)', W)], size=7.4),
]
B1 = [
    t(180, 14, 'One task per day', 9.4, bold=True) + ''.join(box(20 + (k % 14) * 23, 40 + (k // 14) * 14, 18, 10, 'amber', rx=2) for k in range(56)) + ''.join(box(20 + k * 23, 112, 18, 14, 'green', rx=2) for k in range(14)) + cap('56 → 14 files.', '', 'green', y=144, h=30),
    t(180, 14, 'Small side is broadcast', 9.4, bold=True) + opbox(20, 50, 'orders', '835,067 rows', 'card', 110, 34) + opbox(230, 50, 'restaurants', '800 rows', 'green', 110, 34) + arrow(230, 67, 130, 67, 'green', 1.4) + t(180, 100, 'copied to every executor', 7.6, 'ink2') + cap('No shuffle of orders.', '', 'green', y=144, h=30),
    t(180, 14, 'Skew experiment', 9.4, bold=True) + bars(10, 40, [5.30, 1.12, 0.59], ['SMJ, AQE off', 'SMJ, AQE on', 'broadcast'], ['red', 'amber', 'green']) + cap('Measure, don’t guess.', '', 'blue', y=144, h=30),
    t(180, 14, 'Gate on a bad day', 9.4, bold=True) + box(30, 60, 300, 16, 'card', rx=3) + box(30, 60, 300 * 5.34 / 10, 16, 'red', rx=3) + arrow(90, 50, 90, 84, 'acc', 1.4) + t(90, 96, 'gate 2%', 7.4, 'acc', bold=True) + t(215, 72, '5.34%', 7.6, 'ink', bold=True) + cap('Stop before gold.', '', 'red', y=144, h=30),
]
two = anim_two('Capstone: the review', 'Prove it with evidence', 'Real review outputs', 'What each check proves', see, B1,
               ['Files.', 'Plan.', 'Skew.', 'Bad day.'], ['Layout.', 'Join + pruning.', 'Timings.', 'Gate.'])

def five(kind, title, sub, cons, lines, caps, hid):
    fr = [t(180, 22, a, 9.4, 'acc' if i == 4 else 'ink', bold=True) + t(180, 56, b, 8.4, 'ink2') + cap(c, '', tone, y=150, h=34) for i, (a, b, c, tone) in enumerate(lines)]
    return anim_one(kind, title, sub, cons[0], cons[1], fr, caps, hid=hid)

s1 = five('Real-time scenario 1', '“Walk me through your project”', 'The opening interview question. (Typical.)',
          ('Project story', 'Tell the project as situation, task, actions with trade-offs and measured results'), [
    ('Situation', 'food delivery, messy daily files', '15 seconds.', 'blue'),
    ('Task', 'revenue + churn features nightly', 'Who uses it.', 'blue'),
    ('Actions', 'profile, medallion, tests, gates', 'With reasons.', 'green'),
    ('Hard part', '30% skew → broadcast', 'Show a trade-off.', 'green'),
    ('Result', '0.59% quarantined, 25 s', 'Numbers.', 'blue')],
    ['Situation.', 'Task.', 'Actions.', 'Hard part.', 'Result.'], 'scenario-story')
s2 = five('Real-time scenario 2', '“What if the data grows 100×?”', 'Scaling follow-up. (Typical.)',
          ('Scaling', 'Reason about scale from where time and data go, then name concrete changes'), [
    ('84 million orders a day', 'silver step dominates', 'Reads + shuffles all.', 'blue'),
    ('Incremental loads', 'process only new partitions', 'Not full rebuilds.', 'green'),
    ('Table format', 'Delta/Iceberg MERGE', 'Lesson 11.5.', 'green'),
    ('Cluster sizing', 'partitions ≈ 128 MB, AQE on', 'Lesson 8.1.', 'green'),
    ('Maybe streaming', 'Structured Streaming', 'Module 9.', 'blue')],
    ['Growth.', 'Incremental.', 'Format.', 'Sizing.', 'Streaming.'], 'scenario-scale')
s3 = five('Real-time scenario 3 · advanced', '“What would you change?”', 'The senior-level reflection question. (Typical.)',
          ('Reflection', 'Show judgement by naming limitations of your own design and how you would fix them'), [
    ('Full rebuild each night', 'wasteful at scale', 'Go incremental.', 'red'),
    ('Asserts as gates', 'no history of checks', 'DQ framework.', 'amber'),
    ('Plain Parquet', 'no ACID or time travel', 'Delta / Iceberg.', 'amber'),
    ('Batch only', 'revenue is a day late', 'Stream later.', 'amber'),
    ('Honest trade-offs', 'simple first, on purpose', 'Seniors respect this.', 'green')],
    ['Rebuild.', 'Gates.', 'Format.', 'Latency.', 'Judgement.'], 'scenario-reflect')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Prove it with evidence</h2>
  <p>Left: real review outputs. Right: what each check proves.</p>
''' + two + '''
  <p>Three interview scenarios follow: the project story, the scaling follow-up and the reflection question.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

def uc_(word, sub, tone, title, desc, flow_):
    return usecase(f'<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-{tone}" style="stroke:var(--{tone if tone != "acc" else "track"})"/>' + t(60, 42, word, 11, tone, bold=True) + t(60, 58, sub, 7.4, 'ink2'), title, desc, flow_)
uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Where these reviews happen</h2>
''' + '\n'.join([
    uc_('PR', 'review', 'blue', '1. Code review', 'Reviewers ask for the explain() output and test results with every pipeline change.', ['Pull request', '*plan + tests', 'Merge']),
    uc_('prod', 'launch', 'green', '2. Production readiness', 'Platform teams check file layout, gates, alerts and runbooks before go-live.', ['Checklist', '*evidence', 'Go-live']),
    uc_('cost', 'review', 'violet', '3. Cost reviews', 'Slow, shuffle-heavy jobs are found from the UI and fixed with broadcast or pruning.', ['Spark UI', '*experiments', 'Lower bill']),
    uc_('hire', 'interview', 'acc', '4. Hiring loops', 'Data-engineering interviews pair a project deep-dive with Spark fundamentals.', ['Story', '*follow-ups', 'Offer']),
    uc_('post', 'mortem', 'blue', '5. Incident reviews', 'After a bad-data incident, teams add a gate and a test so it cannot recur.', ['Incident', '*gate + test', 'Prevented']),
]) + '''
  <p class="muted">Scenarios are typical; timings and counts are from the lab.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> finish <a href="../02-build-the-pipeline/">13.2</a>. The review uses explain plans (<a href="../../07-spark-sql/03-catalyst-and-explain/">7.3</a>), joins and broadcast (<a href="../../08-performance-tuning/02-join-strategies/">8.2</a>) and skew (<a href="../../08-performance-tuning/03-data-skew-and-salting/">8.3</a>).</p></div>
'''
EXTRA = ''
_x = os.path.join(HERE, '_extra.py')
if os.path.exists(_x): exec(open(_x).read())
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + EXTRA + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
