import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
C = 'l103_tuning.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)

def cm(x, y, tn=21341, fp=3897, fn=6074, tp=8850, s=56):
    o = t(x + s, y - 8, 'predicted 0 · 1', 7, 'ink2', bold=True) + t(x - 6, y + s / 2 + 3, 'actual 0', 6.6, 'ink2', anchor='end') + t(x - 6, y + s * 1.5 + 3, 'actual 1', 6.6, 'ink2', anchor='end')
    for (r, c, v, tone, lab) in ((0, 0, tn, 'green', 'TN'), (0, 1, fp, 'amber', 'FP'), (1, 0, fn, 'red', 'FN'), (1, 1, tp, 'green', 'TP')):
        o += box(x + c * s, y + r * s, s - 4, s - 4, tone, rx=4) + t(x + c * s + (s - 4) / 2, y + r * s + 22, lab, 7.4, 'ink2', bold=True) + t(x + c * s + (s - 4) / 2, y + r * s + 38, f'{v:,}', 8, 'ink', bold=True, mono=True)
    return o

# ---------------------------------------------------------------- story
sc_ = (cm(70, 34, s=52) + t(250, 50, 'threshold', 7.4, 'ink2', bold=True) +
       ''.join(t(250, 66 + k * 16, s, 7, c, mono=True) for k, (s, c) in enumerate([('0.3 → recall 0.82', 'green'), ('0.5 → recall 0.59', 'blue'), ('0.7 → precision 0.81', 'violet')])) +
       box(400, 12, 232, 132, 'card') + t(516, 30, 'Measured (40,162 test rows)', 8.6, bold=True) +
       ''.join(t(412, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
           ('AUC 0.8105 · PR AUC 0.7174', 'green'), ('accuracy 0.75 vs 0.63 baseline', 'amber'),
           ('TVS 17.3 s · CV 36.9 s', 'blue'), ('best: regParam 0.0', 'blue'),
           ('saved model: 12.9 KB', 'green'), ('reload: 0 rows differ', 'green')])))
scene_svg = scene('A model is only useful once it is measured honestly, tuned and saved for scoring. We evaluated the churn model with several metrics and a confusion matrix, moved the decision threshold, tuned it with TrainValidationSplit and CrossValidator, then saved, reloaded and used it to score all customers.', sc_,
                  'Choose the threshold from the <tspan font-weight="700" class="s-acc">business cost</tspan>, not from 0.5.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“75% accurate. Is that good?”</h2>
  <div class="story">
    <p class="narration">The churn model went to TiffinGo’s retention team with one number: “75% accuracy”. The team had budget for coupons to 6,000 customers a month and asked which 6,000 to pick, how many of them would really leave, and whether the model could be run every night without the data scientist.</p>

{scene_svg}

K> Sir, 75% sounds good. Isn’t it?
A> Predicting “nobody churns” already scores 63% on this data. Accuracy hides how many churners we catch and how many coupons we waste. We need AUC, precision and recall, and a threshold matched to the budget.
R> And running it every night?
A> We tune it properly, save the fitted pipeline as files, and let a scoring job load it. Today: metrics, a confusion matrix, thresholds, two tuning methods, and save/load with a check that nothing changed. All outputs are real (PySpark 4.3.0).
  </div>
</section>
'''

lv = '''
LEVELS> Evaluation and tuning at three levels
L1> A security gate
      <ul>
        <li>A strict guard stops few innocent people but misses some intruders (high precision, low recall). A nervous guard stops everyone suspicious (high recall, more false alarms).</li>
        <li>The threshold is how nervous the guard is. Tuning is trying a few guards on practice days and keeping the best.</li>
      </ul>
L2> The API
      <ul>
        <li><code>BinaryClassificationEvaluator(metricName="areaUnderROC" | "areaUnderPR")</code>, <code>MulticlassClassificationEvaluator(metricName="accuracy" | "f1" | …)</code>.</li>
        <li><code>ParamGridBuilder().addGrid(lr.regParam, […]).build()</code>; <code>TrainValidationSplit</code> or <code>CrossValidator(numFolds=3, parallelism=2)</code>; <code>.bestModel</code>.</li>
        <li><code>model.write().overwrite().save(path)</code>, <code>PipelineModel.load(path)</code>.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>AUC 0.8105, PR AUC 0.7174; accuracy 0.7517 vs 0.6284 for always predicting “stay”.</li>
        <li>Threshold 0.7 flagged 5,643 customers with 81% precision; 0.3 caught 82% of churners.</li>
        <li>CrossValidator took 2.1x as long as TrainValidationSplit and picked the same parameters; the reloaded model gave identical predictions.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Evaluation, tuning and saving models</h2>
''' + def_block(
    '<b>Evaluators</b> compute metrics on a predictions DataFrame: for binary classification, the area under the ROC curve (threshold-independent ranking quality) and under the precision-recall curve; for class predictions, accuracy, F1, precision and recall. A <b>confusion matrix</b> counts true/false positives and negatives at a chosen <b>decision threshold</b>, which trades precision against recall. <b>Hyperparameter tuning</b> searches a <code>ParamGridBuilder</code> grid: <code>TrainValidationSplit</code> evaluates each combination once on a held-out part of the training data, while <code>CrossValidator</code> averages over <i>k</i> folds, costing about <i>k</i> times more; both refit the best combination on all training data as <code>bestModel</code>. Fitted pipelines are <b>persisted</b> with <code>MLWriter</code> (<code>model.write().save(path)</code>) as metadata and per-stage data, and restored with <code>PipelineModel.load(path)</code> for batch or streaming scoring.',
    'Measure a model with metrics that fit the problem, not just accuracy; pick the probability threshold that matches what you can act on. Try a few settings automatically and keep the best on validation data. Then save the whole fitted pipeline to storage so any job can load it and score new data exactly the same way.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('ROC AUC', 'Ranking quality, 0.5 = random.'),
    ('PR AUC', 'Precision–recall area.'),
    ('Precision', 'Of flagged, how many churn.'),
    ('Recall', 'Of churners, how many flagged.'),
    ('Threshold', 'Probability cut-off (0.5 default).'),
    ('Param grid', 'Combinations to try.'),
    ('Cross-validation', 'Average over k folds.'),
    ('PipelineModel.load', 'Restore a saved model.'),
]) + '''

  <h3>Which metric answers which question</h3>
''' + table(['Question', 'Metric', 'Lab'], [
    ['Does the model rank churners above stayers?', 'ROC AUC', '0.8105'],
    ['How good is it on the rare/positive class?', 'PR AUC', '0.7174'],
    ['How many predictions are right?', 'Accuracy (compare to baseline)', '0.7517 vs 0.6284'],
    ['Of customers we target, how many churn?', 'Precision at threshold', '0.694 at 0.5, 0.807 at 0.7'],
    ['Of churners, how many do we reach?', 'Recall at threshold', '0.593 at 0.5, 0.815 at 0.3'],
], minw=620) + lv + '''
EXAM> “CrossValidator vs TrainValidationSplit?” Both search a parameter grid with an evaluator. TrainValidationSplit splits training data once (e.g. 80/20) and evaluates each combination once: fast but noisier. CrossValidator uses k folds and averages, more reliable but about k times the cost. Both refit the best parameters on the full training data. Use <code>parallelism</code> to fit several models at once, and keep a separate test set for the final estimate.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Tuning options</h2>
''' + table(['Tool', 'Models fitted', 'Our time', 'When'], [
    ['Manual loop', 'You decide', 'n/a', 'Quick experiments'],
    ['TrainValidationSplit(0.8)', 'grid + 1 = 7', '17.3 s', 'Large data, many combinations'],
    ['CrossValidator(3 folds)', '3 × grid + 1 = 19', '36.9 s', 'Smaller data, reliable estimates'],
], minw=560) + '''
WARN> Grids grow multiplicatively: 3 regParams × 2 elasticNets × 3 folds already meant 19 fits, and adding 3 values for another parameter triples that. Keep grids small and coarse, use <code>parallelism</code>, and cache the training data. Also, a saved model is tied to its Spark version: test loading in the version your scoring job runs, and store the training metrics and data date next to the files.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>From metrics to a saved model</h2>
  <p>All outputs are real: PySpark 4.3.0, <code>local[4]</code>, the churn pipeline from Lesson 10.1 (Imputer, StringIndexer, OneHotEncoder, VectorAssembler, StandardScaler, LogisticRegression) on the same 80/20 split.</p>
''' + stepper([
    ('Step 1 · Metrics',
     code('python', 'l103_tuning.py', 'BinaryClassificationEvaluator(labelCol="churned", metricName="areaUnderROC").evaluate(pred)\nMulticlassClassificationEvaluator(labelCol="churned", metricName="f1").evaluate(pred)\n1 - test.agg(F.avg("churned")).first()[0]          # always predict 0', sec('== 1)', '== 2)')),
     'ROC AUC <b>0.81</b>: pick a random churner and a random stayer, and 81% of the time the model gives the churner a higher score. Accuracy 0.75 looks good until you see the baseline: predicting “no churn” for everyone scores <b>0.63</b>. Always report a baseline next to accuracy.'),
    ('Step 2 · Confusion matrix',
     code('python', 'l103_tuning.py', 'pred.groupBy("churned", "prediction").count().orderBy("churned", "prediction").show()', sec('== 2)', '== 3)')),
     'At the default threshold 0.5: 8,850 churners caught (TP), <b>6,074 missed</b> (FN), 3,897 loyal customers wrongly flagged (FP). Precision 8,850 / 12,747 = 0.69, recall 8,850 / 14,924 = 0.59.'),
    ('Step 3 · Choosing the threshold',
     code('python', 'l103_tuning.py', 'p1 = pred.withColumn("p", vector_to_array("probability")[1])\nfor th in (0.3, 0.5, 0.7):\n    # count TP, FP, FN where p >= th', sec('== 3)', '== 4)')),
     'Same model, three policies. With a budget of about 6,000 coupons, threshold <b>0.7</b> flags 5,643 customers and 81% of them would really churn. If missing a churner is very costly, 0.3 reaches 82% of churners at the price of many more coupons. Choose with the business, then set <code>lr.setThreshold()</code> or filter on the probability.'),
    ('Step 4 · Tuning: TrainValidationSplit vs CrossValidator',
     code('python', 'l103_tuning.py', 'grid = ParamGridBuilder().addGrid(lr.regParam, [0.0, 0.01, 0.1]).addGrid(lr.elasticNetParam, [0.0, 0.5]).build()\nTrainValidationSplit(estimator=pipe, estimatorParamMaps=grid, evaluator=ev, trainRatio=0.8, parallelism=2)\nCrossValidator(estimator=pipe, estimatorParamMaps=grid, evaluator=ev, numFolds=3, parallelism=2)', sec('== 4)', '== 5)')),
     'Six combinations. TrainValidationSplit fitted each once (17.3 s); CrossValidator three times (36.9 s, 2.1x). Both picked <b>no regularization</b> and reached the same test AUC: with 160,000 rows and 15 features there is little to over-fit, and strong regularization (0.1 with L1) hurt (0.79). Tuning confirmed the default was right, which is a valid result.'),
    ('Step 5 · Save and reload',
     code('python', 'l103_tuning.py', 'model.write().overwrite().save("churn_model_v1")\nloaded = PipelineModel.load("churn_model_v1")\n# compare probabilities of model vs loaded on the test set', sec('== 5)', '== 6)')),
     'The saved model is a folder: <code>metadata</code> plus one subfolder per stage, including the imputer medians, the indexer labels, the scaler statistics and the coefficients. Only <b>12.9 KB</b>. After loading, <b>0 rows</b> had a different probability: training and scoring use exactly the same logic.'),
    ('Step 6 · Batch scoring',
     code('python', 'l103_tuning.py', 'loaded.transform(df).filter(vector_to_array("probability")[1] >= 0.7).count()', sec('== 6)')),
     'The nightly job is three lines: read customers, <code>PipelineModel.load</code>, <code>transform</code>. 200,000 customers scored in <b>0.7 s</b>; 28,038 have churn probability ≥ 0.7. The same loaded model can also transform a streaming DataFrame (Module 9).'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('areaUnderROC : 0.8105', G), ('areaUnderPR  : 0.7174', G), ('accuracy     : 0.7517', W), ("baseline     : 0.6284", Y)], size=7.4),
    term([('0 0.0 21341   0 1.0 3897', W), ('1 0.0  6074   1 1.0 8850', W), ('0.3: recall 0.815', G), ('0.7: precision 0.807', G)], size=7.2),
    term([('TVS: 17.3 s, ~7 fits', G), ('CV : 36.9 s, ~19 fits', Y), ('best regParam 0.0, AUC 0.8105', G)], size=7.2),
    term([("saved: ['metadata', 'stages']", W), ('size 12.9 KB', G), ('rows different after reload: 0', G), ('200,000 scored in 0.7 s', G)], size=7.0),
]
B1 = [
    t(180, 14, 'AUC ranks; accuracy counts', 9.4, bold=True) + opbox(20, 46, 'AUC 0.81', 'churner > stayer?', 'green', 150, 34) + opbox(190, 46, 'accuracy 0.75', 'baseline 0.63', 'amber', 150, 34) + cap('Compare to a baseline.', '', 'amber', y=144, h=30),
    t(180, 14, 'The threshold moves errors', 9.4, bold=True) + cm(110, 42, s=46) + cap('Budget decides the cut-off.', '', 'blue', y=144, h=30),
    t(180, 14, 'Grid × folds = fits', 9.4, bold=True) + flow([('6 combos', 'grid', 'violet'), ('× 3 folds', 'CV', 'blue'), ('+1 refit', 'best', 'green')], y=50, w=96, gap=16) + cap('TVS: one split; CV: k splits.', '', 'blue', y=144, h=30),
    t(180, 14, 'Save once, load anywhere', 9.4, bold=True) + flow([('fit', 'notebook', 'blue'), ('save', '12.9 KB', 'violet'), ('load', 'nightly job', 'green')], y=50, w=96, gap=16) + cap('Identical predictions.', '', 'green', y=144, h=30),
]
see_caps = ['Metrics.', 'Confusion matrix and thresholds.', 'Tuning.', 'Save, load, score.']
behind_caps = ['Ranking vs counting.', 'Precision vs recall.', 'Search cost.', 'Model persistence.']
two = anim_two('Evaluate, tune, save', 'From a score to a decision', 'Real lab outputs', 'What it means', see, B1, see_caps, behind_caps)

e1 = (t(180, 22, 'Budget: 6,000 coupons', 9.4, bold=True) + t(180, 56, '₹100 each per month', 8.4, 'ink2') + cap('Who gets them?', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Threshold 0.5', 9.4, bold=True) + t(180, 56, '12,747 flagged, 69% precision', 8.4, 'ink2') + cap('Over budget.', '', 'amber', y=150, h=34))
e3 = (t(180, 22, 'Threshold 0.7', 9.4, bold=True) + t(180, 56, '5,643 flagged, 81% precision', 8.4, 'ink2') + cap('Fits the budget.', '', 'green', y=150, h=34))
e4 = (t(180, 22, 'Or rank and take top 6,000', 9.4, bold=True) + t(180, 56, 'order by probability desc', 8.4, 'ink2') + cap('Budget-driven.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Measure the uplift', 9.4, 'acc', bold=True) + t(180, 56, 'A/B test coupon vs no coupon', 8.4, 'ink2') + cap('Model + action.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Spending the coupon budget',
              'Choosing a decision threshold. (Typical; numbers from our lab.)',
              'Threshold', 'Pick the threshold or top-N from the business budget and the precision it gives', [e1, e2, e3, e4, e5],
              ['Budget.', '0.5.', '0.7.', 'Top-N.', 'Uplift.'],
              hid='scenario-threshold')
b1 = (t(180, 22, 'Grid of 5 × 4 × 3 params', 9.4, bold=True) + t(180, 56, 'CrossValidator, 5 folds', 8.4, 'ink2') + cap('301 fits.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'Job runs 9 hours', 9.4, bold=True) + t(180, 56, 'on 2 TB of training data', 8.4, 'ink2') + cap('Blocks the cluster.', '', 'red', y=150, h=34))
b3 = (t(180, 22, 'Coarse grid first', 9.4, bold=True) + t(180, 56, '6 combos, TrainValidationSplit', 8.4, 'ink2') + cap('2.1x faster than CV (lab).', '', 'green', y=150, h=34))
b4 = (t(180, 22, 'Sample for search', 9.4, bold=True) + t(180, 56, 'tune on 10%, refit on all', 8.4, 'ink2') + cap('Cheap search.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'parallelism + cache', 9.4, 'acc', bold=True) + t(180, 56, 'fit models concurrently', 8.4, 'ink2') + cap('Use the cluster well.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'The nine-hour tuning job',
              'Keeping hyperparameter search affordable. (Typical; timings from our lab.)',
              'Tuning cost', 'Grids multiply fits; use coarse grids, TrainValidationSplit, sampling and parallelism', [b1, b2, b3, b4, b5],
              ['Big grid.', '9 hours.', 'Coarse.', 'Sample.', 'Parallel.'],
              hid='scenario-tuning')
u1 = (t(180, 22, 'Model in a notebook', 9.4, bold=True) + t(180, 56, 'scientist on leave', 8.4, 'ink2') + cap('No nightly scores.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'Save to object storage', 9.4, bold=True) + t(180, 56, 'models/churn/v1 + metrics', 8.4, 'ink2') + cap('Versioned.', '', 'green', y=150, h=34))
u3 = (t(180, 22, 'Nightly job loads it', 9.4, bold=True) + t(180, 56, 'PipelineModel.load(path)', 8.4, 'ink', mono=True) + cap('0.7 s for 200K (lab).', '', 'green', y=150, h=34))
u4 = (t(180, 22, 'Monitor drift', 9.4, bold=True) + t(180, 56, 'AUC on last month’s outcomes', 8.4, 'ink2') + cap('Retrain when it drops.', '', 'amber', y=150, h=34))
u5 = (t(180, 22, 'v2 next to v1', 9.4, 'acc', bold=True) + t(180, 56, 'switch path after comparison', 8.4, 'ink2') + cap('Safe rollouts.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'From notebook to nightly job',
              'Saving, versioning and monitoring models. (Typical.)',
              'Model lifecycle', 'Saved, versioned PipelineModels let jobs score reliably and be replaced safely', [u1, u2, u3, u4, u5],
              ['Notebook.', 'Save.', 'Load.', 'Drift.', 'v2.'],
              hid='scenario-lifecycle')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>From a score to a decision</h2>
  <p>Left: real outputs. Right: what the numbers mean.</p>
''' + two + '''
  <p>Three live scenarios follow: spending a coupon budget, an expensive tuning job, and putting a model into production.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Model evaluation and deployment at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'budget', 11, 'blue', bold=True) + t(60, 58, 'targeting', 7.4, 'ink2'),
    '1. Budgeted campaigns',
    'Retention, credit and fraud teams choose thresholds from the cost of each error.',
    ['Scores', '*threshold', 'Campaign list']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'tune', 12, 'green', bold=True) + t(60, 58, 'monthly', 7.4, 'ink2'),
    '2. Scheduled retraining',
    'Monthly jobs retrain with TrainValidationSplit and save a new version.',
    ['New data', '*tune + fit', 'models/v(n+1)']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'batch', 12, 'violet', bold=True) + t(60, 58, 'scoring', 7.4, 'ink2'),
    '3. Nightly batch scoring',
    'A small job loads the PipelineModel and writes scores to a table.',
    ['Customers', '*load + transform', 'Scores table']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'MLflow', 10, 'acc', bold=True) + t(60, 58, 'registry', 7.4, 'ink2'),
    '4. Model registries',
    'MLflow logs Spark models, parameters and metrics, and promotes versions.',
    ['Run', '*log model', 'Registry']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'drift', 12, 'acc', bold=True) + t(60, 58, 'monitor', 7.4, 'ink2'),
    '5. Drift monitoring',
    'AUC on recent outcomes is tracked; a drop triggers retraining.',
    ['Outcomes', '*evaluate', 'Retrain alert']) + '''
  <p class="muted">Examples are simplified; the customer data is synthetic.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> pipelines in <a href="../01-ml-pipelines/">10.1</a> and classifiers in <a href="../02-feature-engineering-and-classification/">10.2</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
