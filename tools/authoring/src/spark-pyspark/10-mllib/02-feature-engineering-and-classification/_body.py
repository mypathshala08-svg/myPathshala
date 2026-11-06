import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
C = 'l102_features.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)

RES = [('LogReg', 4.9, 0.8105), ('Tree d5', 2.7, 0.7447), ('Forest 50', 10.4, 0.7867), ('GBT 50', 22.3, 0.8069)]
def aucbars(x, y, w=300):
    o = ''
    for k, (n, ft, auc) in enumerate(RES):
        yy = y + k * 22
        bw = (auc - 0.7) / 0.12 * w
        o += t(x, yy + 11, n, 7.2, 'ink', anchor='start', bold=True) + box(x + 62, yy, bw, 15, 'green' if auc > 0.8 else 'amber', rx=3) + t(x + 66 + bw, yy + 11, f'{auc:.3f} · {ft} s', 6.8, 'ink2', anchor='start', mono=True)
    return o

# ---------------------------------------------------------------- story
sc_ = (t(14, 24, 'test AUC (bar from 0.70) · fit time', 7.4, 'ink2', anchor='start', bold=True) + aucbars(14, 34, 220) +
       box(400, 12, 232, 132, 'card') + t(516, 30, 'Measured (same features)', 8.6, bold=True) +
       ''.join(t(412, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
           ('Imputer: 4797 nulls → 0', 'green'), ('tenure 0–6 m: 47.7% churn', 'amber'),
           ('LR AUC 0.8105 (4.9 s)', 'green'), ('GBT 0.8069 (22.3 s)', 'blue'),
           ('top signal: days_since_last', 'violet'), ('LR unscaled reg: 0.8028', 'red')])))
scene_svg = scene('Feature engineering turns raw columns into model inputs, and the classifier learns from them. We imputed, scaled and bucketed the churn features, then trained logistic regression, a decision tree, a random forest and gradient-boosted trees on the same features and compared AUC, fit time and what each model learned.', sc_,
                  'The fanciest model is <tspan font-weight="700" class="s-acc">not always the best</tspan> one.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Use XGBoost, it always wins”</h2>
  <div class="story">
    <p class="narration">The TiffinGo data team argued for a week: one engineer wanted gradient-boosted trees “because they win every Kaggle competition”, another wanted logistic regression “because the business can understand it”. Nobody had compared them on the same features.</p>

{scene_svg}

K> Sir, aren’t tree ensembles always more accurate?
A> Often, when the data has complex interactions. But if the signal is mostly simple, a linear model can match them, train faster and explain itself. The only honest answer is to measure on the same features and the same test set.
R> And the features?
A> They matter more than the algorithm. Today we fill missing values, scale numbers, create tenure bands, train four classifiers, and read what each one learned. All outputs are real (PySpark 4.3.0).
  </div>
</section>
'''

lv = '''
LEVELS> Features and classifiers at three levels
L1> Judging a cooking contest
      <ul>
        <li>Feature engineering is preparing the score sheet: same units, no blanks, useful groupings.</li>
        <li>Classifiers are different judges: one uses a simple weighted checklist (logistic regression), one asks yes/no questions (a tree), one is a panel of many tree judges (forest), one is a chain of judges each fixing the last one’s mistakes (boosting).</li>
      </ul>
L2> The API
      <ul>
        <li>Features: <code>Imputer</code>, <code>StandardScaler(withMean, withStd)</code>, <code>Bucketizer(splits=…)</code>, <code>QuantileDiscretizer</code>, <code>OneHotEncoder</code>, <code>VectorAssembler</code>.</li>
        <li>Classifiers: <code>LogisticRegression</code>, <code>DecisionTreeClassifier</code>, <code>RandomForestClassifier</code>, <code>GBTClassifier</code> (also LinearSVC, NaiveBayes, MultilayerPerceptron).</li>
        <li>Inspect: <code>coefficients</code>, <code>featureImportances</code>, <code>toDebugString</code>.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>Logistic regression had the best AUC (0.8105) and GBT came close (0.8069) at 4.5x the training time.</li>
        <li>Both models agreed: days since last order, orders in 30 days and complaints drive churn.</li>
        <li>With regularization, unscaled features lost AUC (0.8028 vs 0.8104).</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Feature engineering and classification</h2>
''' + def_block(
    '<b>Feature engineering</b> transforms raw attributes into numeric features suitable for a learning algorithm: imputing missing values, encoding categories, scaling numeric ranges (<code>StandardScaler</code> to zero mean and unit variance), discretising continuous values into buckets, and assembling everything into a feature vector. A <b>classifier</b> learns a function from features to a discrete label. MLlib provides <b>logistic regression</b> (a linear model producing class probabilities through the logistic function, with optional L1/L2 regularization), <b>decision trees</b> (recursive binary splits), and tree ensembles: <b>random forests</b> (many trees on bootstrapped samples and random feature subsets, averaged) and <b>gradient-boosted trees</b> (trees trained sequentially on the errors of the previous ones). All are Estimators that train in a distributed way and output <code>rawPrediction</code>, <code>probability</code> and <code>prediction</code>.',
    'Features are the numbers a model learns from; good features are complete, comparable and meaningful. A classifier learns to predict a category such as churn yes/no. Logistic regression weighs each feature, trees ask questions, forests average many trees, and boosting adds trees that fix earlier mistakes.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Imputation', 'Filling missing values.'),
    ('Scaling', 'Same range for all numbers.'),
    ('Bucketizing', 'Number → band.'),
    ('Logistic regression', 'Weighted sum → probability.'),
    ('Decision tree', 'Yes/no splits.'),
    ('Random forest', 'Average of many trees.'),
    ('Gradient boosting', 'Trees fixing earlier errors.'),
    ('Feature importance', 'How much a feature was used.'),
]) + '''

  <h3>Four classifiers on the same features</h3>
''' + table(['Model', 'Fit time', 'Test AUC', 'Accuracy', 'Explainability'], [
    ['Logistic regression', '4.9 s', '0.8105', '0.7517', 'Coefficients per feature'],
    ['Decision tree (depth 5)', '2.7 s', '0.7447', '0.7244', 'Readable rules'],
    ['Random forest (50 trees)', '10.4 s', '0.7867', '0.7336', 'Feature importances'],
    ['GBT (50 iterations)', '22.3 s', '0.8069', '0.7475', 'Feature importances'],
], minw=620) + lv + '''
EXAM> “Which classifier would you use in Spark MLlib?” Start with a simple, fast baseline such as logistic regression on well-engineered, scaled features; then try tree ensembles (random forest, GBT) when relationships are non-linear or interactions matter. Compare on the same held-out data with AUC/F1, and weigh training time and explainability. In our data the linear model matched GBT because the true signal was mostly linear.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Which features for which model</h2>
''' + table(['Preparation', 'Linear models', 'Tree models'], [
    ['Impute nulls', 'Required', 'Required in MLlib'],
    ['Scale numbers', 'Important (regularization, convergence)', 'Not needed'],
    ['One-hot categories', 'Required', 'Optional (indexed is fine)'],
    ['Buckets / interactions', 'Help capture non-linear effects', 'Learned automatically'],
    ['Many sparse features (text)', 'Works well', 'Slower'],
], minw=600) + '''
WARN> A model’s weights and importances describe <b>what it used</b>, not cause and effect. Logistic regression coefficients are comparable only when features are on the same scale; tree importances favour features with many possible split points. And watch for <b>leakage features</b>: a column like “cancellation_reason” would give near-perfect churn accuracy because it only exists after the customer churned.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Features, then four classifiers</h2>
  <p>All outputs are real: PySpark 4.3.0, <code>local[4]</code>, the 200,000-customer churn data from Lesson 10.1 with the same 80/20 split (cached). AUC is computed on the test split from the <code>probability</code> column.</p>
''' + stepper([
    ('Step 1 · Imputing missing values',
     code('python', 'l102_features.py', 'im = Imputer(inputCols=["avg_amount", "late_pct"], outputCols=["avg_amount", "late_pct"], strategy="median").fit(train)\nim.surrogateDF.first()     # the learned medians', sec('== 1)', '== 2)')),
     'The Imputer learned the training <b>medians</b> (₹293.9 and 18.0%) and filled all 4,797 missing amounts. Median is safer than mean for skewed values like order amounts. The same medians are reused at scoring time, because they are stored in the fitted model.'),
    ('Step 2 · Scaling',
     code('python', 'l102_features.py', 'va = VectorAssembler(inputCols=["orders_30d", "avg_amount", "days_since_last"], outputCol="raw")\nStandardScaler(inputCol="raw", outputCol="scaled", withMean=True, withStd=True)', sec('== 2)', '== 3)')),
     'Raw features live on very different scales: orders around 6 (std 2.4), amounts around 300 (std 157.6). After scaling each is “standard deviations from the mean”: 9 orders is +1.22, ₹216 is −0.65. Now a weight of 1.0 means the same thing for every feature.'),
    ('Step 3 · Bucketizing tenure',
     code('python', 'l102_features.py', 'Bucketizer(splits=[0, 6, 12, 24, 48], inputCol="tenure_months", outputCol="tenure_band")', sec('== 3)', '== 4)')),
     'Bands make a pattern visible and give linear models a way to treat ranges differently: customers in their first 6 months churn at <b>47.7%</b>, those over 2 years at 31.2%. Use <code>QuantileDiscretizer</code> when you want equal-sized bands instead of fixed cut points.'),
    ('Step 4 · Four classifiers',
     code('python', 'l102_features.py', 'models = {"LogisticRegression": [scaled, LogisticRegression(featuresCol="sfeatures", labelCol="churned")],\n          "DecisionTree(depth 5)": [DecisionTreeClassifier(labelCol="churned", maxDepth=5)],\n          "RandomForest(50 trees)": [RandomForestClassifier(labelCol="churned", numTrees=50, maxDepth=6)],\n          "GBT(50 iters)": [GBTClassifier(labelCol="churned", maxIter=50, maxDepth=4)]}\nfor name, tail in models.items():\n    m = Pipeline(stages=prep + [feat] + tail).fit(train)', sec('== 4)', '== 5)')),
     'Same features, same test set. Logistic regression was best (<b>AUC 0.8105</b>) and GBT a close second (0.8069) at 4.5x the training time; a single tree was weakest. Our churn signal was generated mostly linearly, so a linear model fits it well; on data with strong interactions the ensembles usually win. Measure; do not assume.'),
    ('Step 5 · What the models learned',
     code('python', 'l102_features.py', 'lr = fitted["LogisticRegression"].stages[-1]; lr.coefficients\nrf = fitted["RandomForest(50 trees)"].stages[-1]; rf.featureImportances\ndt.toDebugString', sec('== 5)', '== 6)')),
     'Both agreed: <b>days since last order</b> is the strongest churn signal, then orders in 30 days, complaints, late deliveries and tenure. The signs of the scaled coefficients are readable: more recent orders lower churn (−0.61), complaints raise it (+0.44). The tree’s first question was also about feature 2, days since last order.'),
    ('Step 6 · Scaling matters with regularization',
     code('python', 'l102_features.py', 'LogisticRegression(labelCol="churned", regParam=0.1, standardization=False)      # raw features\nLogisticRegression(featuresCol="sfeatures", labelCol="churned", regParam=0.1)   # scaled', sec('== 6)')),
     'Regularization penalises large weights. On raw features, a variable measured in big units (amounts) needs a tiny weight and one in small units needs a big one, so the penalty hits them unfairly: AUC fell to <b>0.8028</b>. Scaled, the same penalty kept 0.8104. (MLlib’s LogisticRegression standardises internally by default; we turned that off to show the effect.)'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([("medians: avg_amount 293.9, late_pct 18.0", W), ('nulls before: 4797 | after: 0', G)], size=7.2),
    term([('raw   : [9.0, 216.4, 18.0]', W), ('scaled: [1.22, -0.65, -0.67]', G), ('std   : [2.4, 157.6, 17.3]', Y)], size=7.4),
    term([('LogReg  AUC 0.8105   4.9 s', G), ('Tree d5 AUC 0.7447   2.7 s', Y), ('Forest  AUC 0.7867  10.4 s', W), ('GBT     AUC 0.8069  22.3 s', G)], size=7.2),
    term([('days_since_last  +1.03 | 0.636', G), ('orders_30d       -0.61 | 0.150', G), ('complaints       +0.44 | 0.083', W)], size=7.2),
]
B1 = [
    t(180, 14, 'Fill with the training median', 9.4, bold=True) + flow([('null', 'avg_amount', 'red'), ('median', '293.9', 'violet'), ('filled', 'value', 'green')], y=50, w=96, gap=16) + cap('Stored in the model.', '', 'green', y=144, h=30),
    t(180, 14, 'Same scale for every feature', 9.4, bold=True) + opbox(20, 46, 'orders 9', 'std 2.4', 'card', 90, 32) + opbox(130, 46, '₹216.4', 'std 157.6', 'card', 90, 32) + arrow(222, 62, 244, 62, 'ink3', 1) + opbox(248, 46, '+1.22, −0.65', 'z-scores', 'green', 100, 32) + cap('Weights become comparable.', '', 'green', y=144, h=30),
    t(180, 14, 'Four learners', 9.4, bold=True) + aucbars(20, 36, 170) + cap('Measure on the same test set.', '', 'blue', y=144, h=30),
    t(180, 14, 'What drives churn', 9.4, bold=True) + ''.join(t(20, 48 + k * 18, n, 7.4, 'ink', anchor='start', bold=True) + box(140, 38 + k * 18, v * 300, 12, 'violet', rx=2) for k, (n, v) in enumerate([('days_since_last', 0.636), ('orders_30d', 0.15), ('complaints', 0.083), ('tenure_months', 0.06)])) + cap('Forest importances (lab).', '', 'violet', y=144, h=30),
]
see_caps = ['Imputation.', 'Scaling.', 'Four classifiers.', 'What they learned.']
behind_caps = ['Learned fill values.', 'Standardization.', 'Model comparison.', 'Coefficients and importances.']
two = anim_two('Features and classifiers', 'Prepare, train, compare', 'Real lab outputs', 'What the models do', see, B1, see_caps, behind_caps)

e1 = (t(180, 22, '“GBT always wins”', 9.4, bold=True) + t(180, 56, 'vs “LR is explainable”', 8.4, 'ink2') + cap('A week of debate.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Same features, same split', 9.4, bold=True) + t(180, 56, 'four models in one loop', 8.4, 'ink2') + cap('Fair comparison.', '', 'green', y=150, h=34))
e3 = (t(180, 22, 'LR 0.8105, GBT 0.8069', 9.4, bold=True) + t(180, 56, 'GBT 4.5x slower to train', 8.4, 'ink2') + cap('Our lab.', '', 'green', y=150, h=34))
e4 = (t(180, 22, 'Pick LR for now', 9.4, bold=True) + t(180, 56, 'explainable, fast, as good', 8.4, 'ink2') + cap('Revisit with new features.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Decision by data', 9.4, 'acc', bold=True) + t(180, 56, 'not by reputation', 8.4, 'ink2') + cap('Debate over.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Ending the model debate',
              'Comparing classifiers fairly. (Typical; numbers from our lab.)',
              'Model choice', 'Compare models on the same features and test set before choosing', [e1, e2, e3, e4, e5],
              ['Debate.', 'Same data.', 'Results.', 'Choose.', 'By data.'],
              hid='scenario-compare')
b1 = (t(180, 22, 'Churn model AUC 0.99', 9.4, bold=True) + t(180, 56, 'first try, amazing', 8.4, 'ink2') + cap('Suspicious.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'Top feature: last_refund_ts', 9.4, bold=True) + t(180, 56, 'set when a customer leaves', 8.4, 'ink2') + cap('Leakage feature.', '', 'red', y=150, h=34))
b3 = (t(180, 22, 'Rule: features as of cut-off', 9.4, bold=True) + t(180, 56, 'only data known before churn', 8.4, 'ink2') + cap('Point-in-time.', '', 'green', y=150, h=34))
b4 = (t(180, 22, 'Retrain: AUC 0.81', 9.4, bold=True) + t(180, 56, 'honest, deployable', 8.4, 'ink2') + cap('Real signal.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Check top features', 9.4, 'acc', bold=True) + t(180, 56, 'every model review', 8.4, 'ink2') + cap('Importances help.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'The 0.99 AUC model',
              'Leakage features. (Typical.)',
              'Leakage feature', 'Feature importances help spot features that leak the label', [b1, b2, b3, b4, b5],
              ['0.99.', 'Leak.', 'Cut-off.', '0.81.', 'Review.'],
              hid='scenario-leakfeature')
u1 = (t(180, 22, 'New customers churn most', 9.4, bold=True) + t(180, 56, '47.7% in first 6 months', 8.4, 'ink2') + cap('Our tenure bands.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'Linear model sees a line', 9.4, bold=True) + t(180, 56, 'tenure effect not linear', 8.4, 'ink2') + cap('Underfits the start.', '', 'amber', y=150, h=34))
u3 = (t(180, 22, 'Add tenure bands', 9.4, bold=True) + t(180, 56, 'Bucketizer + OneHotEncoder', 8.4, 'ink2') + cap('One weight per band.', '', 'green', y=150, h=34))
u4 = (t(180, 22, 'Or use a tree model', 9.4, bold=True) + t(180, 56, 'learns the bands itself', 8.4, 'ink2') + cap('Trade-offs.', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'Target onboarding offers', 9.4, 'acc', bold=True) + t(180, 56, 'first 6 months', 8.4, 'ink2') + cap('Business action.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'The first six months',
              'Engineering non-linear features. (Typical; churn rates from our lab.)',
              'Feature bands', 'Bucketized features let linear models capture non-linear effects', [u1, u2, u3, u4, u5],
              ['Pattern.', 'Linear.', 'Bands.', 'Trees.', 'Action.'],
              hid='scenario-bands')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Prepare, train, compare</h2>
  <p>Left: real outputs. Right: what each step and model does.</p>
''' + two + '''
  <p>Three live scenarios follow: choosing a model, a leakage feature, and non-linear tenure effects.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Classification at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'churn', 12, 'blue', bold=True) + t(60, 58, 'retention', 7.4, 'ink2'),
    '1. Churn prediction',
    'Recency, frequency and service quality features predict who will leave.',
    ['Customer features', '*classifier', 'Retention list']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'fraud', 12, 'green', bold=True) + t(60, 58, 'payments', 7.4, 'ink2'),
    '2. Fraud detection',
    'Tree ensembles catch interactions between amount, device and location.',
    ['Payment', '*GBT', 'Fraud flag']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'late', 12, 'violet', bold=True) + t(60, 58, 'delivery', 7.4, 'ink2'),
    '3. Late-delivery risk',
    'Predict whether an order will be late from zone, time, weather and rider load.',
    ['Order', '*random forest', 'Risk']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'credit', 11, 'acc', bold=True) + t(60, 58, 'scoring', 7.4, 'ink2'),
    '4. Credit scoring',
    'Regulated lenders prefer logistic regression for explainable decisions.',
    ['Applicant', '*logistic', 'Score + reasons']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'leads', 12, 'acc', bold=True) + t(60, 58, 'sales', 7.4, 'ink2'),
    '5. Lead scoring',
    'Restaurant sign-up leads are ranked by probability to convert.',
    ['Leads', '*probability', 'Sales queue']) + '''
  <p class="muted">Examples are simplified; the customer data is synthetic.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> pipelines, estimators and the churn data in <a href="../01-ml-pipelines/">10.1</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
