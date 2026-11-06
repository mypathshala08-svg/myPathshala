import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
BODY = body(HERE)

META = dict(
    module='10-mllib', lesson='03-evaluation-tuning-and-saving-models', n='10.3',
    module_label='Module 10 · MLlib',
    title='Evaluation, tuning and saving models',
    desc='Evaluating, tuning and saving Spark ML models with PySpark 4.3.0: ROC AUC 0.8105 and PR AUC 0.7174, accuracy 0.75 vs a 0.63 baseline, a confusion matrix, precision and recall at thresholds 0.3/0.5/0.7, TrainValidationSplit (17.3 s) vs CrossValidator (36.9 s) on a 6-point grid, and saving a 12.9 KB PipelineModel that reloads with identical predictions and scores 200,000 customers in 0.7 s.',
    og_desc='Is 75% accuracy good? Metrics, thresholds, CrossValidator vs TrainValidationSplit, and saving a Spark PipelineModel for nightly scoring.',
    minutes=30, level='Intermediate → Advanced',
    lead='A model is useful only when measured honestly, tuned and deployable. This lesson evaluates the churn model with the right metrics, picks a <b>decision threshold</b> from a budget, compares <b>TrainValidationSplit</b> and <b>CrossValidator</b>, and <b>saves and reloads</b> the PipelineModel for batch scoring. <b>All outputs are real</b> (PySpark 4.3.0).',
    chips=['PySpark 4.3.0', 'Thresholds compared', 'CV vs TVS timed', 'Runs in your browser (Python)'],
)

MAIN = '''# Precision and recall from the lab confusion matrix, and a budget threshold
tn, fp, fn, tp = 21341, 3897, 6074, 8850
precision = tp / (tp + fp)
recall = tp / (tp + fn)
f1 = 2 * precision * recall / (precision + recall)
print(f"precision {precision:.3f} | recall {recall:.3f} | f1(churn) {f1:.3f}")

lab = {0.3: (21280, 0.571, 0.815), 0.5: (12747, 0.694, 0.593), 0.7: (5643, 0.807, 0.305)}
budget = 6000
ok = [th for th, (flagged, p, r) in lab.items() if flagged <= budget]
best = min(ok)                                   # lowest threshold that fits the budget
print("threshold for a budget of", budget, "->", best, lab[best])
'''
RUN = dict(
    heading='Run the code: precision, recall and a budget',
    intro='<p>From the lab’s confusion matrix to a business threshold. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('precision = tp / (tp + fp)', 'Of the customers we flag, how many really churn.'),
        ('best = min(ok)                                   # lowest threshold that fits the budget', 'Lower threshold = more churners reached; the budget sets the limit.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Then set the budget to 25,000.', code=None),
        dict(label='2 · Predict first: baseline', hint='<b>Predict first:</b> accuracy of always predicting “stay” with 37.2% churn.',
             code='''churn_rate = 0.3716
print(round(1 - churn_rate, 4))
'''),
        dict(label='3 · Fits in tuning', hint='Models fitted by CrossValidator.',
             code='''grid, folds = 6, 3
print("CV:", grid * folds + 1, "| TVS:", grid + 1)
'''),
        dict(label='4 · AUC meaning', hint='Share of churner/stayer pairs ranked correctly.',
             code='''churn_scores = [0.8, 0.6, 0.4]
stay_scores = [0.5, 0.2, 0.3]
pairs = [(c, s) for c in churn_scores for s in stay_scores]
print(round(sum(c > s for c, s in pairs) / len(pairs), 3))
'''),
        dict(label='5 · Spot the error', hint='Reporting accuracy without a baseline.', expect='error',
             code='''accuracy, baseline = 0.7517, 0.6284
assert accuracy - baseline > 0.3, "75% sounds good, but 'nobody churns' already gives 63%: report AUC, precision, recall"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: evaluate and save',
    intro='<p>In the <code>pyspark</code> shell after fitting the lab pipeline. <b>Outputs are real</b> (PySpark 4.3.0).</p>',
    items=[
        dict(title='1 · PR AUC', cmd='BinaryClassificationEvaluator(labelCol="churned", metricName="areaUnderPR").evaluate(pred)', file='pyspark',
             output='0.7174…', note='Focus on the positive class.'),
        dict(title='2 · Save', cmd='model.write().overwrite().save("churn_model_v1")\nimport os; sorted(os.listdir("churn_model_v1"))', file='pyspark',
             output="['metadata', 'stages']", note='One folder per stage.'),
        dict(title='3 · Load and score', cmd='loaded = PipelineModel.load("churn_model_v1")\nloaded.transform(df).filter(vector_to_array("probability")[1] >= 0.7).count()', file='pyspark',
             output='28038', note='0.7 s for 200,000.'),
    ],
)

TRACE = dict(
    heading='k-fold cross-validation',
    intro='<p>Each fold is the validation set once.</p>',
    code='''rows = list(range(6))
k = 3
scores = []
for f in range(k):
    val = [r for r in rows if r % k == f]
    train = [r for r in rows if r % k != f]
    scores.append(len(train))
print(scores, sum(scores) / k)
''',
    notes={5: 'Validation :: One fold held out.', 6: 'Train :: The other k−1 folds.', 8: 'Average :: The metric is averaged.'},
)

WORKED_INTRO = 'Three evaluation decisions at TiffinGo.'
EXAMPLES = [
    dict(level='b', tag='Evaluation · basics', title='Is 75% good?',
         problem='<p>Accuracy 0.7517 with 37% churners.</p>',
         inp='accuracy and class balance',
         approach=['Compute the majority-class baseline.', 'Compare.', 'Report AUC too.'],
         code='''print("baseline", 1 - 0.3716, "| model", 0.7517)
''', notes={1: 'Baseline :: Predict the majority class.'},
         tryit='Step 1.'),
    dict(level='i', tag='Evaluation · threshold', title='Threshold for a budget',
         problem='<p>Budget: 6,000 coupons/month.</p>',
         inp='flagged per threshold',
         approach=['List flagged counts.', 'Pick the lowest threshold within budget.', 'Check its precision.'],
         code='''flagged = {0.3: 21280, 0.5: 12747, 0.7: 5643}
print(min(t for t, n in flagged.items() if n <= 6000))
''', notes={1: 'Or top-N :: Sort by probability and take 6,000.'},
         tryit='Step 3.'),
    dict(level='a', tag='Tuning · cost', title='Plan a tuning job',
         problem='<p>Grid 4 × 3 × 3, CV 5 folds, 2 min per fit.</p>',
         inp='grid and folds',
         approach=['Fits = grid × folds + 1.', 'Divide by parallelism.', 'Consider TVS or a smaller grid.'],
         code='''grid, folds, mins, par = 4 * 3 * 3, 5, 2, 4
print((grid * folds + 1) * mins / par, "minutes")
''', notes={1: 'Cost :: 181 fits.'},
         tryit='Step 4.'),
]

QUIZ = mix([
    dict(q='Beginner: ROC AUC 0.5 means…', options=['Perfect', 'Random ranking', 'Always wrong', '50% accuracy'], answer=1,
         why='0.81 in our lab.'),
    dict(q='Beginner: Recall is…', options=['TP / (TP + FP)', 'TP / (TP + FN)', 'TN / all', 'Accuracy'], answer=1,
         why='Share of churners caught.'),
    dict(q='Beginner: Save a fitted pipeline with…', options=['pickle', 'model.write().save(path)', 'df.write', 'spark.save'], answer=1,
         why='Load with PipelineModel.load.'),
    dict(q='Intermediate: Raising the threshold from 0.5 to 0.7…', options=['Raises recall', 'Raises precision, lowers recall', 'No effect', 'Changes AUC'], answer=1,
         why='0.694 → 0.807 precision.'),
    dict(q='Intermediate: Majority baseline in our data?', options=['0.37', '0.63', '0.75', '0.81'], answer=1,
         why='Always predict “stay”.'),
    dict(q='Intermediate: CrossValidator with 6 combos, 3 folds fits about…', options=['7', '19 models', '6', '3'], answer=1,
         why='Plus the final refit.'),
    dict(q='Advanced: CV vs TVS in our lab?', options=['Different winners', 'Same best params; CV 2.1x slower', 'TVS failed', 'CV faster'], answer=1,
         why='17.3 vs 36.9 s.'),
    dict(q='Advanced: Reloaded model predictions…', options=['Slightly differ', 'Identical (0 rows differ)', 'Need refit', 'Lose preprocessing'], answer=1,
         why='Whole pipeline saved.'),
])

REVISION = [
    'ROC AUC 0.8105, PR AUC 0.7174; accuracy 0.75 vs 0.63 baseline.',
    'Confusion matrix: TP 8,850, FN 6,074, FP 3,897 at 0.5.',
    'Threshold trades precision vs recall (0.7: 5,643 flagged, 81% precision).',
    'ParamGridBuilder + TrainValidationSplit (fast) or CrossValidator (k× cost).',
    'Lab: TVS 17.3 s vs CV 36.9 s, same best params.',
    '<code>model.write().save()</code> / <code>PipelineModel.load()</code>: 12.9 KB, identical predictions.',
    'Batch scoring: 200,000 customers in 0.7 s.',
]
FAQ = [
    ('Should I tune on the test set?', 'No. Tuning uses validation splits inside the training data; the test set gives the final, untouched estimate.'),
    ('How do I change the threshold of a saved model?', 'Set it on the model stage (lr_model.setThreshold(0.7)) or filter on the probability column in the scoring job.'),
    ('Can I load the model in Scala or Java?', 'Yes, the saved format is shared across Spark’s language APIs.'),
    ('Do saved models work across Spark versions?', 'Usually within a major version; test loading before upgrading and retrain if needed.'),
    ('How do I track experiments?', 'Use MLflow’s Spark flavor to log parameters, metrics and the model with each run.'),
]

PRACTICE_INTRO = 'Programs about metrics, tuning and thresholds.'
PROBLEMS = [
    dict(level='easy', title='Precision', stmt='Precision from TP 8,850 and FP 3,897.', inp='8850, 3897',
         code='''print(round(8850 / (8850 + 3897), 3))
''', explain='0.694.'),
    dict(level='easy', title='Recall', stmt='Recall from TP 8,850 and FN 6,074.', inp='8850, 6074',
         code='''print(round(8850 / (8850 + 6074), 3))
''', explain='0.593.'),
    dict(level='easy', title='Slowdown', stmt='CV vs TVS time.', inp='36.9, 17.3',
         code='''print(round(36.9 / 17.3, 1))
''', explain='2.1x.'),
    dict(level='medium', title='F1', stmt='F1 for the churn class.', inp='p 0.694, r 0.593',
         code='''p, r = 0.694, 0.593
print(round(2 * p * r / (p + r), 3))
''', explain='Harmonic mean.'),
    dict(level='medium', title='Grid size', stmt='Combinations of 3 × 2 × 4.', inp='lists',
         code='''import itertools
print(len(list(itertools.product([0, 0.01, 0.1], [0, 0.5], [10, 20, 50, 100]))))
''', explain='24.'),
    dict(level='medium', title='Top-N', stmt='Top 3 customers by probability.', inp='dict',
         code='''p = {"c1": 0.91, "c2": 0.42, "c3": 0.77, "c4": 0.88}
print(sorted(p, key=p.get, reverse=True)[:3])
''', explain='Budget-driven targeting.'),
    dict(level='business', title='Coupon value', stmt='Expected churners reached at 0.7.', inp='5,643 × 0.807',
         code='''print(round(5643 * 0.807))
''', explain='About 4,554 real churners.'),
    dict(level='business', title='Wasted coupons', stmt='Coupons to non-churners at 0.5 and ₹100.', inp='3,897',
         code='''print("₹", 3897 * 100)
''', explain='Precision has a price.'),
]

SCN_INTRO = 'Evaluation and deployment questions show production ML experience.'
SCENARIOS = (
    scn('Any company · Spark', 'Fresher', '“Precision vs recall”',
        'Explain with an example.',
        'trade-off?',
        '<p>Precision: of flagged customers, how many churn. Recall: of churners, how many we flagged. Raising the threshold raises precision and lowers recall; in my lab 0.5 → 0.7 moved precision 0.69 → 0.81 and recall 0.59 → 0.31.</p>', 'Using accuracy alone.') +
    scn('Data science', 'Mid-level', 'Tuning in Spark',
        'How do you tune hyperparameters in MLlib?',
        'tools?',
        '''<ul>
          <li>ParamGridBuilder + evaluator.</li>
          <li>TrainValidationSplit for speed, CrossValidator for reliability.</li>
          <li>parallelism, cached data, small grids; final check on a test set.</li>
        </ul>''', 'Tuning on the test set.') +
    scn('ML engineering', 'Mid-level', 'Deploying a model',
        'Move a notebook model to nightly scoring.',
        'steps?',
        '''<ol>
          <li>Save the fitted PipelineModel to versioned storage.</li>
          <li>Scoring job: load, transform, write scores.</li>
          <li>Verify reload gives identical predictions; log metrics.</li>
        </ol>''', 'Pickling only the classifier.') +
    scn('ML platform', 'Senior', 'Model lifecycle',
        'Design retraining and monitoring for churn models.',
        'design?',
        '''<ul>
          <li>Monthly retrain with tuning; new version path + registry.</li>
          <li>Champion/challenger comparison on recent data.</li>
          <li>Drift monitoring on AUC and feature distributions.</li>
        </ul>''', 'Training once and never checking again.')
)
