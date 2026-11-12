import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from svgkit import scn
BODY = body(HERE)
META = dict(module='04-dataframes', lesson='07-statistics-and-sampling', n='4.7', module_label='Module 4 · DataFrame basics',
    title='Statistics and sampling',
    desc='Descriptive statistics and sampling on PySpark DataFrames: describe vs summary, approxQuantile and relativeError, corr, cov, crosstab, freqItems, sample, sampleBy (stratified) and randomSplit. Real PySpark 4.3 lab on 200,000 TiffinGo orders.',
    og_desc='A −4 minute delivery, a wrong p95 of ₹1,414 and samples that are never exactly 1%: statistics and sampling in PySpark 4.3.',
    minutes=20, level='Beginner',
    lead='Look before you model. We profile 200,000 orders with <b>describe</b> and <b>summary</b>, find percentiles with <b>approxQuantile</b>, measure links with <b>corr</b> and <b>crosstab</b>, and take fair <b>samples</b>. <b>All outputs are real.</b>',
    chips=['describe found −4 min', 'p95: 1414 vs 419', 'corr 0.908', 'Runs in your browser (Python)'])
MAIN = '''# Median, p95 and correlation by hand (what Spark computes for you)
amounts = [120, 180, 200, 210, 150, 400, 230, 190, 260, 900]
xs = sorted(amounts)
def q(p):
    return xs[min(len(xs) - 1, int(p * len(xs)))]
print("median:", q(0.5), " p95:", q(0.95))
km   = [1, 2, 3, 4, 5]
mins = [15, 17, 20, 22, 25]
mk, mm = sum(km) / 5, sum(mins) / 5
cov = sum((a - mk) * (b - mm) for a, b in zip(km, mins)) / 4
sd = lambda v, m: (sum((x - m) ** 2 for x in v) / 4) ** 0.5
print("corr:", round(cov / (sd(km, mk) * sd(mins, mm)), 3))
'''
RUN = dict(heading='Run the code: statistics by hand', intro='<p>Percentiles and Pearson correlation in plain Python. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('    return xs[min(len(xs) - 1, int(p * len(xs)))]', 'Rank of the p-th value in sorted data.'), ('print("corr:", round(cov / (sd(km, mk) * sd(mins, mm)), 3))', 'Pearson = covariance ÷ (sd × sd).')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>.', code=None),
        dict(label='2 · Predict first: sample size', hint='<b>Predict first:</b> 1% Bernoulli of 1,000 rows.', code='import random\nrandom.seed(1)\nprint(sum(random.random() < 0.01 for _ in range(1000)))\n'),
        dict(label='3 · Stratify', hint='Different fraction per city.', code='frac = {"Mumbai": 0.01, "Pune": 0.05}\nrows = {"Mumbai": 100000, "Pune": 40000}\nprint({c: int(rows[c] * f) for c, f in frac.items()})\n'),
        dict(label='4 · Rank error', hint='err 0.1 on 200,000 rows.', code='print("rank may be off by", int(0.1 * 200000), "rows")\n'),
        dict(label='5 · Spot the error', hint='Bad data check.', expect='error', code='mins = [22, 31, -4, 18]\nif min(mins) < 0:\n    raise ValueError(f"negative delivery time {min(mins)}: quarantine before reporting")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC', intro='<p>PySpark 4.x. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Run the lab', cmd='python3 l47_stats.py', file='terminal', output='  relativeError 0.01  -> [200.0, 417.0]', note='~30 seconds.'),
           dict(title='2 · Per-group median', cmd='df.groupBy("city").agg(F.median("amount")).show()', file='python', output='', note='Exact median per group.')])
TRACE = dict(heading='One percentile step by step', intro='<p>Rank and tolerance.</p>',
    code='n, p, err = 200000, 0.95, 0.01\nrank = int(p * n)\nlow, high = rank - int(err * n), rank + int(err * n)\nprint(rank, low, high)\n', notes={2: 'Rank :: 190,000th value.', 3: 'Tolerance :: ±2,000 ranks.'})
WORKED_INTRO = 'Three profiling decisions.'
EXAMPLES = [
    dict(level='b', tag='summary', title='Find bad values', problem='<p>Is any delivery time impossible?</p>', inp='summary',
         approach=['summary("min").', 'Compare with rules.', 'Quarantine.'], code='print(-4.0 < 0)\n', notes={1: 'Bad row.'}, tryit='Step 1.'),
    dict(level='i', tag='quantile', title='Choose relativeError', problem='<p>p95 for a policy.</p>', inp='errors',
         approach=['Try 0.01.', 'Check with 0 on a sample.', 'Document.'], code='res = {0.1: 1414, 0.01: 417, 0.0: 419}\nprint(res[0.01])\n', notes={1: 'Close to exact.'}, tryit='Step 2.'),
    dict(level='a', tag='split', title='Reproducible split', problem='<p>Same train/test every run.</p>', inp='df',
         approach=['cache().', 'randomSplit with seed.', 'Check counts.'], code='print(int(200000 * 0.8), int(200000 * 0.2))\n', notes={1: 'Approximate sizes.'}, tryit='Step 5.')]
QUIZ = mix([
    dict(q='Beginner: describe() shows…', options=['Percentiles only', 'count, mean, stddev, min, max', 'Schema', 'Plans'], answer=1, why='Step 1.'),
    dict(q='Beginner: The median is…', options=['The mean', 'The 50% quantile', 'The mode', 'The max'], answer=1, why='50%.'),
    dict(q='Beginner: sample(0.01) returns…', options=['Exactly 1%', 'About 1%', 'First 1%', '0 rows'], answer=1, why='Bernoulli.'),
    dict(q='Intermediate: relativeError 0 means…', options=['Fast and rough', 'Exact', 'Error', 'Sampled'], answer=1, why='Exact, costlier.'),
    dict(q='Intermediate: corr(km, mins) in our lab was…', options=['0.0', '0.908', '−0.5', '1.414'], answer=1, why='Step 3.'),
    dict(q='Intermediate: sampleBy is…', options=['Ordered sampling', 'Stratified sampling', 'Random split', 'Dedup'], answer=1, why='Fraction per key.'),
    dict(q='Advanced: p95 with error 0.1 was…', options=['419', '1414', '200', '417'], answer=1, why='Badly off.'),
    dict(q='Advanced: Before randomSplit you should…', options=['sort', 'cache the input', 'collect', 'repartition(1)'], answer=1, why='Stable splits.')])
REVISION = ['describe: count, mean, stddev, min, max; summary adds percentiles.', 'approxQuantile(col, probs, err): 0 exact, 0.01 close, 0.1 wrong p95 (1414 vs 419).',
    'stat.corr / cov / crosstab / freqItems (approx).', 'sample: approximate size; sampleBy: per-key fractions; randomSplit with seed, cache first.', 'Profiling found −4 minute deliveries.']
FAQ = [('Is summary() exact?', 'count/mean/min/max yes; percentiles are approximate.'),
    ('Spearman correlation?', 'DataFrame.stat.corr supports only Pearson; use pyspark.ml.stat.Correlation with method="spearman".'),
    ('Exact N random rows?', 'orderBy(F.rand(seed)).limit(N): exact but needs a sort.'),
    ('Why do split sizes change?', 'Without cache, the source is re-evaluated; cache and fix the seed.')]
PRACTICE_INTRO = 'Statistics programs.'
PROBLEMS = [
    dict(level='easy', title='Mean', stmt='Average.', inp='list', code='v = [100, 200, 300]\nprint(sum(v) / len(v))\n', explain='200.'),
    dict(level='easy', title='Median', stmt='Middle value.', inp='list', code='v = sorted([5, 1, 9, 3, 7])\nprint(v[len(v) // 2])\n', explain='5.'),
    dict(level='easy', title='Range', stmt='max − min.', inp='list', code='v = [25, 1414, 200]\nprint(max(v) - min(v))\n', explain='1389.'),
    dict(level='medium', title='Stddev', stmt='Sample stddev.', inp='list', code='v = [2, 4, 4, 4, 5, 5, 7, 9]\nm = sum(v) / 8\nprint(round((sum((x - m) ** 2 for x in v) / 7) ** 0.5, 2))\n', explain='2.14.'),
    dict(level='medium', title='Crosstab', stmt='Pair counts.', inp='pairs', code='from collections import Counter\nprint(Counter([("Pune", "UPI"), ("Pune", "UPI"), ("Delhi", "Card")]))\n', explain='Counts.'),
    dict(level='medium', title='Split', stmt='80/20.', inp='list', code='import random\nrandom.seed(42)\nr = [random.random() < 0.8 for _ in range(1000)]\nprint(sum(r), 1000 - sum(r))\n', explain='About 800/200.'),
    dict(level='business', title='Free delivery', stmt='Orders above p95.', inp='ints', code='print(int(200000 * 0.05), "orders above ₹419")\n', explain='10,000.'),
    dict(level='business', title='Bad rows', stmt='Share of bad rows.', inp='ints', code='print(round(37 / 200000 * 100, 3), "%")\n', explain='Tiny but harmful.')]
SCN_INTRO = 'Statistics interview questions.'
SCENARIOS = (scn('Any company · data', 'Fresher', '“How do you find the median in PySpark?”', 'Explain.', 'answer?', '<p>approxQuantile("col", [0.5], 0.01) or summary("50%"), or F.median / percentile_approx in SQL; relativeError 0 for exact.</p>', '“collect() and sort in Python.”') +
    scn('Fintech', 'Mid-level', 'Threshold', 'p95 looks wrong.', 'fix?', '<ul><li>Lower relativeError; cross-check with exact on a sample.</li></ul>', 'Trust it.') +
    scn('Data', 'Mid-level', 'Exact sample', 'Need exactly 1,000 rows.', 'answer?', '<ul><li>orderBy(rand(seed)).limit(1000).</li></ul>', 'sample(0.001).') +
    scn('ML team', 'Senior', 'Unstable splits', 'Metrics change run to run.', 'answer?', '<ul><li>cache, fixed seed, deterministic source order.</li></ul>', 'More epochs.'))
