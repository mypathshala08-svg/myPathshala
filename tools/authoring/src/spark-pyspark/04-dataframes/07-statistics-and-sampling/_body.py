import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit2 import *
C = 'l47_stats.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('Before any model or dashboard: what does the data actually look like? Averages, spread, medians, links between columns, and a fair sample to play with.',
    'PySpark has a small statistics toolbox on every DataFrame. On 200,000 TiffinGo orders, <code>describe()</code> exposed a delivery of <b>−4 minutes</b> (bad data), <code>corr</code> showed distance explains delivery time (0.908), and <code>approxQuantile</code> with a loose error of 0.1 called the p95 order <b>₹1,414</b> while the true p95 is <b>₹419</b>. Also: <code>sample(0.01)</code> gave 1,941, 1,938 and 2,009 rows, never exactly 2,000.',
    ['Profile columns with describe() and summary().', 'Medians and percentiles with approxQuantile, and what relativeError costs.', 'corr, cov, crosstab, freqItems; sample, sampleBy and randomSplit.'])
cmap = concept_map('Concept map. Beginner: describe, summary. Intermediate: quantiles, correlation, crosstab. Advanced: approximate algorithms, stratified sampling, train/test splits.',
    [[('df', 'DataFrames', 'Lesson 4.1', B + '04-dataframes/01-sparksession-and-dataframes/'), ('nl', 'Nulls', 'Lesson 4.4', B + '04-dataframes/04-nulls-and-duplicates/')],
     [('ds', 'describe / summary', 'profile', None), ('qt', 'approxQuantile', 'percentiles', None), ('cr', 'corr / cov', 'links', None), ('ct', 'crosstab', 'counts', None)],
     [('sm', 'sample', 'fraction', None), ('sb', 'sampleBy', 'strata', None), ('rs', 'randomSplit', 'train/test', None), ('ml', 'MLlib', 'Lesson 10.1', B + '10-mllib/01-ml-pipelines/')]],
    [('df', 'ds'), ('nl', 'ds'), ('ds', 'qt'), ('ds', 'cr'), ('cr', 'ct'), ('df', 'sm'), ('sm', 'sb'), ('sm', 'rs'), ('rs', 'ml')],
    {'ds', 'qt', 'cr', 'ct', 'sm', 'sb', 'rs'},
    '<b>Builds on:</b> <a href="../04-nulls-and-duplicates/">4.4</a>. <b>Next:</b> <a href="../../05-reading-and-writing-data/01-csv-and-json/">Module 5</a>, and <a href="../../10-mllib/01-ml-pipelines/">10.1</a> for randomSplit in ML.')
whw = why_how_where(
    'Profiling first catches bad data (negative minutes), picks sensible thresholds (p95 order value) and prepares fair samples for experiments and ML.',
    'describe/summary run one aggregation job over the columns. approxQuantile uses the Greenwald–Khanna sketch: relativeError trades accuracy for memory. sample flips a coin per row (Bernoulli), so the size is only close to fraction × count; sampleBy uses a fraction per key.',
    'Data quality checks, EDA notebooks, KPI thresholds, A/B test groups, train/test splits, quick previews of huge tables.',
    'Exact percentiles on billions of rows are expensive; sample sizes are random; corr is Pearson only (linear) in DataFrame.stat; freqItems may return false positives.')

def bars(hl=-1):
    hs = [18, 40, 62, 78, 70, 52, 34, 22, 14, 9, 6, 4]
    o = ''.join(box(30 + i * 22, 112 - h, 18, h, 'blue' if i != hl else 'acc', rx=2) for i, h in enumerate(hs))
    o += box(118, 26, 2, 90, 'green', rx=1) + t(119, 20, 'median ₹200', 7.4, bold=True)
    o += box(196, 26, 2, 90, 'amber', rx=1) + t(222, 20, 'p95 ₹419', 7.4, bold=True)
    o += box(286, 26, 2, 90, 'red', rx=1) + t(300, 34, 'err 0.1: ₹1,414?', 7.0, bold=True)
    return o + t(176, 128, 'order amount (₹) →', 7.2)
scene_svg = scene('A histogram of 200,000 order amounts: median 200 rupees, true 95th percentile 419 rupees, and the wrong answer 1,414 rupees that a loose relativeError of 0.1 returned.', bars(),
                  'Same data, <tspan font-weight="700" class="s-acc">different error setting</tspan>, very different p95.')
dialogue = '''K> Sir, finance wants “typical order value” and “top 5% orders”. Should I collect() to pandas?
A> 200,000 rows today, 200 million next year. Spark has <b>describe</b>, <b>summary</b> and <b>approxQuantile</b> built in.
R> Approx? Finance wants exact numbers.
A> Then set the error to 0 and pay for it, or 0.01 and be very close. With 0.1 we will see something funny. Let’s look.'''
lv = '''
LEVELS> Statistics and sampling at three levels
L1> Tasting the dal
      <ul>
        <li>You do not drink the whole pot to check salt: you taste a spoon (sample). describe() is the label on the pot: count, average, spread, smallest, biggest.</li>
      </ul>
L2> The API
      <ul>
        <li><code>df.describe(*cols)</code>: count, mean, stddev, min, max. <code>df.summary("count", "25%", "50%", "75%", …)</code> adds percentiles.</li>
        <li><code>df.approxQuantile(col, [0.5, 0.95], relativeError)</code>; <code>df.stat.corr(a, b)</code>, <code>cov</code>, <code>crosstab</code>, <code>freqItems(cols, support)</code>.</li>
        <li><code>df.sample(fraction, seed)</code>, <code>withReplacement=True</code>; <code>df.sampleBy(col, {key: fraction}, seed)</code>; <code>df.randomSplit([0.8, 0.2], seed)</code>.</li>
      </ul>
L3> Practical details
      <ul>
        <li>relativeError 0 is exact but can be expensive on huge data; 0.01 is a common compromise; SQL has <code>percentile_approx</code> and <code>percentile</code>.</li>
        <li><code>summary()</code> percentiles are approximate too. Use <code>F.median</code>, <code>F.percentile</code> inside groupBy for per-group values.</li>
        <li>Cache before randomSplit: without it, each split re-reads and re-randomises the source; with the same seed and cached data, splits are reproducible.</li>
      </ul>
/LEVELS
'''
DIS = figure('Dissection of approxQuantile: column amount, probabilities 0.5 and 0.95, relativeError 0.01, result a list of two values.',
    t(16, 22, 'One approxQuantile call (real)', 8.6, 'ink', anchor='start', bold=True) +
    fields(16, 34, [('"amount"', 'blue', 1), ('[0.5, 0.95]', 'green', 2), ('0.01', 'amber', 3), ('→ [200, 417]', 'violet', 4)]) +
    legend(16, 84, [(1, 'Column', 'numeric column'), (2, 'Probabilities', 'median and p95'), (3, 'relativeError', '0 = exact, larger = cheaper'),
                    (4, 'Result', 'Python list, one value each')], size=8, gap=15, w=90),
    h=156, caption='It returns plain Python numbers to the driver, not a DataFrame.')
extra = '''

  <h3>Dissect approxQuantile</h3>
''' + DIS
types_html = table(['Method', 'Answers', 'Exact?', 'Returns'], [
    ['describe / summary', 'count, mean, spread, min/max, percentiles', 'percentiles approx', 'DataFrame'],
    ['approxQuantile', 'median, p95…', 'set by relativeError', 'Python list'],
    ['stat.corr / cov', 'do two columns move together?', 'yes (Pearson)', 'float'],
    ['stat.crosstab', 'counts for pairs of values', 'yes', 'DataFrame'],
    ['stat.freqItems', 'frequent values', 'no (false positives)', 'DataFrame'],
    ['sample / sampleBy / randomSplit', 'a random subset', 'size is random', 'DataFrame(s)']], minw=600)
warn = 'Do not trust approxQuantile with a large relativeError for tail percentiles: in our lab, 0.1 returned the maximum (₹1,414) as p95 instead of ₹419. And never expect sample(0.01) to return exactly 1% of rows: use limit() or take() after ordering if you need an exact count.'
steps = [
    ('Step 1 · Profile with describe and summary',
     code('python', 'l47_stats.py', 'df.select("km", "mins", "amount").describe().show()\ndf.select("amount").summary("count", "min", "25%", "50%", "75%", "max").show()', sec('== 1)', '== 2)')),
     'min of mins = −4.0: impossible delivery time; profiling found a data bug before any report used it.'),
    ('Step 2 · Percentiles and relativeError',
     code('python', 'l47_stats.py', 'for err in [0.1, 0.01, 0.0]:\n    df.approxQuantile("amount", [0.5, 0.95], err)', sec('== 2)', '== 3)')),
     'At 200,000 rows all three are fast; the difference is accuracy. 0.01 is within ₹2 of exact; 0.1 is badly wrong in the tail.'),
    ('Step 3 · Correlation and covariance',
     code('python', 'l47_stats.py', 'df.stat.corr("km", "mins"); df.stat.corr("km", "amount"); df.stat.cov("km", "mins")', sec('== 3)', '== 4)')),
     'Distance and delivery time: 0.908 (strong). Distance and amount: 0.0 (no link). Lesson 10.5 turns this into a model.'),
    ('Step 4 · crosstab and freqItems',
     code('python', 'l47_stats.py', 'df.stat.crosstab("city", "pay").show()\ndf.stat.freqItems(["pay"], 0.25)', sec('== 4)', '== 6)')),
     'UPI dominates in every city. freqItems is approximate: it may list Cash even though Cash is only 10%.'),
    ('Step 5 · sample, sampleBy, randomSplit',
     code('python', 'l47_stats.py', 'df.sample(fraction=0.01, seed=s).count()\ndf.sampleBy("city", {"Mumbai": 0.01, "Pune": 0.05, "Delhi": 0.0}, seed=1)\ndf.randomSplit([0.8, 0.2], seed=42)', sec('== 6)')),
     'Sizes are close to the fraction, not exact. sampleBy gives each city its own fraction (Delhi 0 → none).'),
]
see = [term([('mins min -4.0', RD), ('amount 50% 200', G)], size=7.0), term([('0.1  -> p95 1414', RD), ('0.01 -> p95 417', G), ('0.0  -> p95 419', G)], size=6.8),
       term([('corr km,mins 0.908', G), ('corr km,amt 0.0', W)], size=7.0), term([('Mumbai UPI 60069', G), ('freqItems: 3 items', W)], size=6.8), term([('seed1 1941 seed2 1938', W), ('train 160000/40000', G)], size=6.8)]
B1 = [bars(4), bars(10), bars(-1), bars(-1), bars(-1)]
B1 = [b + cap(c, '', tn, y=140, h=26) for b, c, tn in zip(B1, ['Bad data found', 'Error matters', 'Strong link', 'Pairs counted', 'Fair samples'], ['red', 'amber', 'green', 'blue', 'violet'])]
two = anim_two('Statistics and sampling', 'Look before you model', 'Real outputs (local[2])', 'Profile the data', see, B1, ['Profile.', 'Quantiles.', 'Corr.', 'Crosstab.', 'Sample.'], ['−4!', '0.01.', '0.908.', 'UPI.', 'Random.'])
pe = peel('approxQuantile, layer by layer', 'How Spark finds a median without sorting everything. (Simplified.)',
    [('Partitions', ''), ('Sketch', ''), ('Merge', ''), ('Query', ''), ('Error', ''), ('Answer', '')],
    [['Partitions', 'each task sees', 'its rows', ''], ['Sketch', 'keeps a compact', 'summary per task', 'GK'], ['Merge', 'driver merges', 'sketches', ''],
     ['Query', 'rank 0.95 × n', 'looked up', ''], ['Error', 'rank may be off', 'by err × n', ''], ['Answer', 'one value', 'per probability', '']],
    ['Split.', 'Summarise.', 'Combine.', 'Look up.', 'Tolerance.', 'Result.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'Data quality gate', 'Negative delivery times in reports. (Typical.)', ('summary()', 'Profile every load'), [
    ('Daily load lands', '200k orders', 'Input.', 'blue'), ('summary() on key columns', 'min/max/percentiles', 'Profile.', 'green'),
    ('min mins < 0', 'rule fails', 'Detect.', 'red'), ('Quarantine bad rows', 'filter mins >= 0', 'Fix.', 'amber'),
    ('Alert owner', 'source bug', 'Operate.', 'blue')], ['Load.', 'Profile.', 'Detect.', 'Quarantine.', 'Alert.'], 'scenario-dq') + \
       five('Real-time scenario 2', 'Free delivery threshold', 'Finance needs a p95. (Typical.)', ('approxQuantile', 'relativeError 0.01'), [
    ('Question: top 5% orders', 'threshold?', 'Ask.', 'blue'), ('approxQuantile(…, 0.1)', 'p95 = 1414?', 'Wrong.', 'red'),
    ('Rerun with 0.01', 'p95 = 417', 'Fix.', 'green'), ('Cross-check exact 0.0', '419', 'Verify.', 'green'),
    ('Publish ₹420', 'documented', 'Decide.', 'amber')], ['Ask.', 'Loose.', 'Tight.', 'Verify.', 'Publish.'], 'scenario-p95') + \
       five('Real-time scenario 3 · advanced', 'Fair A/B groups', 'Stratified experiment. (Typical.)', ('sampleBy + randomSplit', 'Strata and seeds'), [
    ('Cities differ in size', 'Mumbai 50%', 'Data.', 'blue'), ('sampleBy city fractions', 'balanced pilot', 'Stratify.', 'green'),
    ('cache()', 'stable input', 'Stabilise.', 'amber'), ('randomSplit([0.5,0.5], seed)', 'A and B', 'Split.', 'green'),
    ('Check crosstab', 'groups similar', 'Verify.', 'violet')], ['Sizes.', 'Strata.', 'Cache.', 'Split.', 'Check.'], 'scenario-ab')
assemble(HERE, h2_story='Know your data before you use it', hook_html=hk,
    narration='TiffinGo finance wants a typical order value and a “top 5%” threshold for free delivery; the ML team wants a fair train/test split. All from a 200,000-row DataFrame.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Statistics and sampling on DataFrames',
    formal='PySpark DataFrames expose descriptive statistics (<code>describe</code>, <code>summary</code>), approximate quantiles via the Greenwald–Khanna algorithm (<code>approxQuantile</code> with a relative error bound), pairwise statistics in <code>DataFrame.stat</code> (Pearson correlation, sample covariance, contingency tables, frequent items) and random sampling (Bernoulli <code>sample</code>, stratified <code>sampleBy</code>, weighted <code>randomSplit</code>).',
    simple='Quick numbers about your columns (average, spread, middle value, top 5%), whether two columns move together, and ways to take a fair random piece of the data.',
    term_rows=[('describe', 'count, mean, stddev, min, max.'), ('summary', 'Adds percentiles.'), ('Quantile', 'Value below which p% fall.'), ('relativeError', 'Allowed rank error.'), ('corr', 'Pearson −1..1.'), ('crosstab', 'Pair counts.'), ('sampleBy', 'Fraction per key.'), ('randomSplit', 'Weighted splits.')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('Approximate means slightly off.', 'With err 0.1 the p95 can be wildly off.', 'Step 2.'),
               ('sample(0.01) gives exactly 1%.', '1,941 / 1,938 / 2,009 rows.', 'Step 5.'),
               ('corr 0 means unrelated.', 'Only no linear link.', 'Step 3.')],
    exam='“How do you get a median in PySpark?” approxQuantile(col, [0.5], relativeError) or summary("50%"), F.median/percentile_approx in SQL; describe vs summary; corr is Pearson; sample is Bernoulli (approximate size); sampleBy = stratified; randomSplit with seed (cache first).',
    types_h2='The statistics toolbox', types_html=types_html, warn=warn,
    steps_h2='Profiling 200,000 orders', steps_intro='All outputs are real: PySpark 4.3.0, local[2], synthetic TiffinGo orders with a fixed seed.',
    steps=steps, two=two, peel_intro='Now peel approxQuantile.', peel_html=pe,
    scen_intro='Three live scenarios: quality gate, a p95 threshold, and A/B groups.', scen=scen,
    uc_h2='Statistics at work', ucs=[uc_('dq', 'quality', 'red', '1. Data quality', 'summary() rules on each load.', ['Load', '*summary', 'Alert']),
        uc_('kpi', 'kpi', 'blue', '2. KPI thresholds', 'p95 via approxQuantile.', ['Orders', '*Quantile', 'Policy']),
        uc_('ab', 'ab', 'green', '3. Experiments', 'sampleBy + randomSplit.', ['Users', '*Split', 'A/B']),
        uc_('eda', 'eda', 'violet', '4. EDA before ML', 'corr and crosstab.', ['Table', '*stat', 'Features'])],
    uc_note='Examples are simplified descriptions of common practice.',
    pre='<b>Before you start:</b> <a href="../03-working-with-columns/">4.3 Working with columns</a>.')
