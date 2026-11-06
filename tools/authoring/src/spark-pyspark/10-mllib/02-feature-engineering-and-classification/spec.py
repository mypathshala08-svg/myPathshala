import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
BODY = body(HERE)

META = dict(
    module='10-mllib', lesson='02-feature-engineering-and-classification', n='10.2',
    module_label='Module 10 · MLlib',
    title='Feature engineering and classification',
    desc='Feature engineering and classifiers in Spark MLlib with PySpark 4.3.0: a median Imputer (4,797 nulls filled), StandardScaler z-scores, Bucketizer tenure bands (47.7% churn in the first 6 months), and logistic regression, decision tree, random forest and gradient-boosted trees on the same features (AUC 0.8105, 0.7447, 0.7867, 0.8069; fit 4.9 to 22.3 s), with coefficients, feature importances and the effect of scaling on regularized models.',
    og_desc='Logistic regression vs decision tree vs random forest vs GBT on the same Spark features: AUC, training time and what each learned.',
    minutes=30, level='Intermediate',
    lead='Good features matter more than fancy algorithms. This lesson imputes, scales and bucketizes churn features, then trains <b>four classifiers</b> on the same data and compares AUC, training time and what each model learned. <b>All outputs are real</b> (PySpark 4.3.0).',
    chips=['PySpark 4.3.0', '4 classifiers compared', 'Importances shown', 'Runs in your browser (Python)'],
)

MAIN = '''# Logistic regression scoring by hand (scaled features, lab coefficients)
import math
coef = {"days_since_last": 1.03, "orders_30d": -0.61, "complaints": 0.44,
        "late_pct": 0.42, "tenure_months": -0.41}
intercept = -0.55          # illustrative

def churn_prob(z):
    s = intercept + sum(coef[k] * z[k] for k in coef)
    return 1 / (1 + math.exp(-s))

loyal = {"days_since_last": -1.2, "orders_30d": 1.5, "complaints": -0.6, "late_pct": -0.5, "tenure_months": 1.4}
risky = {"days_since_last": 1.6, "orders_30d": -1.0, "complaints": 2.2, "late_pct": 1.1, "tenure_months": -1.3}
print("loyal:", round(churn_prob(loyal), 3))
print("risky:", round(churn_prob(risky), 3))
'''
RUN = dict(
    heading='Run the code: a logistic regression score',
    intro='<p>How logistic regression turns scaled features into a probability. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('coef = {"days_since_last": 1.03, "orders_30d": -0.61, "complaints": 0.44,', 'The lab’s scaled coefficients: positive raises churn risk, negative lowers it.'),
        ('    return 1 / (1 + math.exp(-s))', 'The logistic (sigmoid) function maps any score to a probability between 0 and 1.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Then give the loyal customer 3 complaints (z = 5.5).', code=None),
        dict(label='2 · Predict first: z-score', hint='<b>Predict first:</b> 9 orders, mean 6.07, std 2.4.',
             code='''x, mean, std = 9, 6.07, 2.4
print(round((x - mean) / std, 2))
'''),
        dict(label='3 · Bucketize', hint='Tenure bands with splits [0, 6, 12, 24, 48].',
             code='''import bisect
splits = [0, 6, 12, 24, 48]
for m in (3, 6, 18, 40):
    print(m, "-> band", bisect.bisect_right(splits, m) - 1)
'''),
        dict(label='4 · A tiny tree', hint='The lab tree’s first question.',
             code='''def tree(days_since_last, orders_30d):
    if days_since_last <= 33.5:
        return "stay" if orders_30d > 3 else "churn"
    return "churn"
print(tree(10, 8), tree(45, 8), tree(20, 1))
'''),
        dict(label='5 · Spot the error', hint='A feature that only exists after the customer left.', expect='error',
             code='''features = ["orders_30d", "days_since_last", "cancellation_reason"]
assert "cancellation_reason" not in features, "leakage: this column is known only after churn"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: features and models',
    intro='<p>In the <code>pyspark</code> shell with the lab data. <b>Outputs are real</b> (PySpark 4.3.0).</p>',
    items=[
        dict(title='1 · Medians', cmd='Imputer(inputCols=["avg_amount", "late_pct"], outputCols=["avg_amount", "late_pct"], strategy="median").fit(train).surrogateDF.show()', file='pyspark',
             output='+----------+--------+\n|avg_amount|late_pct|\n+----------+--------+\n|     293.9|    18.0|\n+----------+--------+', note='Learned on train.'),
        dict(title='2 · Importances', cmd='sorted([(n, round(float(v), 3)) for n, v in zip(names, rf.featureImportances.toArray())], key=lambda x: -x[1])[:3]', file='pyspark',
             output="[('days_since_last', 0.636), ('orders_30d', 0.15), ('complaints', 0.083)]", note='names = feature names in vector order.'),
        dict(title='3 · Tree root', cmd='dt.toDebugString.split("\\n")[1].strip()', file='pyspark',
             output='If (feature 2 <= 33.5)', note='Feature 2 = days_since_last.'),
    ],
)

TRACE = dict(
    heading='Standard scaling',
    intro='<p>Compute z-scores for a column.</p>',
    code='''import statistics
x = [9, 5, 6, 4, 6]
m = statistics.mean(x)
s = statistics.stdev(x)
z = [round((v - m) / s, 2) for v in x]
print(m, round(s, 2), z)
''',
    notes={3: 'Mean :: Learned in fit().', 4: 'Std :: Sample standard deviation.', 5: 'z :: Applied in transform().'},
)

WORKED_INTRO = 'Three feature and model decisions at TiffinGo.'
EXAMPLES = [
    dict(level='b', tag='Features · nulls', title='Mean or median?',
         problem='<p>Order amounts are skewed by a few corporate orders.</p>',
         inp='amounts',
         approach=['Skewed data: mean is pulled up.', 'Median is robust.', 'strategy="median".'],
         code='''import statistics
a = [120, 150, 180, 200, 5000]
print("mean", statistics.mean(a), "| median", statistics.median(a))
''', notes={2: 'Robust :: One huge order barely moves the median.'},
         tryit='Step 1.'),
    dict(level='i', tag='Models · compare', title='Fair comparison',
         problem='<p>Compare LR, RF and GBT for churn.</p>',
         inp='same prep',
         approach=['Same feature stages.', 'Same split and seed.', 'Same metric on test.'],
         code='''res = {"LR": (0.8105, 4.9), "RF": (0.7867, 10.4), "GBT": (0.8069, 22.3)}
print(max(res, key=lambda k: res[k][0]))
''', notes={1: 'Also time :: GBT 4.5x slower here.'},
         tryit='Step 4.'),
    dict(level='a', tag='Features · explain', title='Explain a prediction',
         problem='<p>Support asks why a customer is “high risk”.</p>',
         inp='scaled coefficients',
         approach=['Contribution = coefficient × z-score.', 'Sort by size.', 'Report the top 3.'],
         code='''coef = {"days_since_last": 1.03, "complaints": 0.44, "orders_30d": -0.61}
z = {"days_since_last": 1.6, "complaints": 2.2, "orders_30d": -1.0}
print(sorted(((k, round(coef[k] * z[k], 2)) for k in coef), key=lambda x: -x[1]))
''', notes={1: 'Linear :: Contributions add up to the score.'},
         tryit='Step 5.'),
]

QUIZ = mix([
    dict(q='Beginner: Imputer with strategy="median" uses…', options=['Test median', 'Training median', 'Zero', 'Mean'], answer=1,
         why='293.9 for amounts.'),
    dict(q='Beginner: StandardScaler with mean and std gives…', options=['0–1 range', 'z-scores', 'Ranks', 'Logs'], answer=1,
         why='Std deviations from mean.'),
    dict(q='Beginner: Random forest is…', options=['One deep tree', 'Many trees averaged', 'A linear model', 'Boosting'], answer=1,
         why='Bagging + random features.'),
    dict(q='Intermediate: Best AUC in our lab?', options=['Decision tree', 'Logistic regression 0.8105', 'Random forest', 'All equal'], answer=1,
         why='GBT 0.8069 close.'),
    dict(q='Intermediate: Do tree models need scaling?', options=['Yes', 'No', 'Only GBT', 'Only forests'], answer=1,
         why='Splits use thresholds.'),
    dict(q='Intermediate: Strongest churn signal found?', options=['city', 'days_since_last', 'plan', 'avg_amount'], answer=1,
         why='Both LR and RF agreed.'),
    dict(q='Advanced: Unscaled features + regularization in our lab…', options=['Improved AUC', 'Lowered AUC to 0.8028', 'Failed', 'No effect'], answer=1,
         why='Penalty unfair across scales.'),
    dict(q='Advanced: A feature known only after churn is…', options=['Great', 'Leakage', 'A label', 'Noise'], answer=1,
         why='Inflates offline metrics.'),
])

REVISION = [
    'Impute (median), encode, scale, bucket, assemble.',
    'Scaling matters for linear models and regularization (0.8028 vs 0.8104).',
    'Bucketizer: tenure 0–6 months churn 47.7% vs 31.2% for 2+ years.',
    'LR 0.8105 (4.9 s), tree 0.7447, forest 0.7867, GBT 0.8069 (22.3 s).',
    'Compare on the same features, split and metric.',
    'Coefficients and importances agree: days since last order dominates.',
    'Watch for leakage features.',
]
FAQ = [
    ('Why did GBT not beat logistic regression?', 'Our synthetic churn signal was mostly linear; ensembles shine when interactions and non-linear effects matter.'),
    ('Does MLlib have XGBoost?', 'Not built in; GBTClassifier is MLlib’s boosting. XGBoost and LightGBM offer Spark integrations as separate libraries.'),
    ('How do I handle class imbalance?', 'Use weightCol with higher weights for the rare class, resample, and evaluate with PR AUC or F1 rather than accuracy.'),
    ('What about multiclass labels?', 'LogisticRegression (multinomial), trees and forests support multiple classes; OneVsRest wraps binary models.'),
    ('Are feature importances reliable?', 'They are a guide; correlated features share importance and high-cardinality features can be favoured.'),
]

PRACTICE_INTRO = 'Programs about features and classifiers.'
PROBLEMS = [
    dict(level='easy', title='z-score', stmt='z for ₹216.4 (mean 318, std 157.6).', inp='216.4',
         code='''print(round((216.4 - 318) / 157.6, 2))
''', explain='About −0.65.'),
    dict(level='easy', title='Speed ratio', stmt='GBT vs LR training time.', inp='22.3, 4.9',
         code='''print(round(22.3 / 4.9, 1))
''', explain='4.5x.'),
    dict(level='easy', title='Band', stmt='Band of 18 months (splits 0,6,12,24,48).', inp='18',
         code='''print(2)
''', explain='12–24.'),
    dict(level='medium', title='Median fill', stmt='Fill nulls with the median.', inp='list',
         code='''import statistics
v = [10, None, 30, 20]
m = statistics.median(x for x in v if x is not None)
print([x if x is not None else m for x in v])
''', explain='Imputer.'),
    dict(level='medium', title='Sigmoid', stmt='Probability for score 1.2.', inp='1.2',
         code='''import math
print(round(1 / (1 + math.exp(-1.2)), 3))
''', explain='0.769.'),
    dict(level='medium', title='Rank features', stmt='Sort importances.', inp='dict',
         code='''imp = {"orders_30d": 0.15, "days_since_last": 0.636, "complaints": 0.083}
print(sorted(imp, key=imp.get, reverse=True))
''', explain='Days since last first.'),
    dict(level='business', title='Training cost', stmt='Daily retrain minutes saved using LR vs GBT at 100x data.', inp='4.9 vs 22.3 s',
         code='''print(round((22.3 - 4.9) * 100 / 60), "minutes")
''', explain='Same AUC, less compute.'),
    dict(level='business', title='Onboarding focus', stmt='Churners in the first 6 months.', inp='17,161 × 47.7%',
         code='''print(round(17161 * 0.477))
''', explain='A clear target group.'),
]

SCN_INTRO = 'Feature engineering and model choice are core ML interview topics.'
SCENARIOS = (
    scn('Any company · Spark', 'Fresher', '“Why scale features?”',
        'Explain feature scaling.',
        'which models?',
        '<p>Scaling puts features on comparable ranges. Linear models and regularization depend on it (in my lab unscaled + regularization dropped AUC from 0.8104 to 0.8028); tree models do not need it because they split on thresholds.</p>', 'Scaling before splitting (leakage).') +
    scn('Data science', 'Mid-level', 'Choosing a classifier',
        'Pick a model for churn in Spark.',
        'process?',
        '''<ul>
          <li>Baseline logistic regression on good features.</li>
          <li>Try RF/GBT on the same split; compare AUC and time.</li>
          <li>In my test LR 0.8105 vs GBT 0.8069 at 4.5x time.</li>
        </ul>''', 'Picking GBT by default.') +
    scn('Data science', 'Mid-level', 'Suspicious accuracy',
        'A new model has AUC 0.99.',
        'what to check?',
        '''<ol>
          <li>Top features: anything known only after the label?</li>
          <li>Preprocessing fitted on all data?</li>
          <li>Duplicate customers across train and test?</li>
        </ol>''', 'Shipping it.') +
    scn('ML platform', 'Senior', 'Explainability',
        'Business wants reasons for each high-risk customer.',
        'approach?',
        '''<ul>
          <li>Linear model: coefficient × scaled value per feature.</li>
          <li>Trees: importances globally; SHAP-style tools per row (outside MLlib).</li>
          <li>Report top 3 reasons with each score.</li>
        </ul>''', 'Only giving a probability.')
)
