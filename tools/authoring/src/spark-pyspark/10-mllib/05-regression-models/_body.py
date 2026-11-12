import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit2 import *
C = 'l105_reg.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('“Your tiffin will arrive in 38 minutes.” How does an app predict a number, not a class?',
    'With <b>regression</b>. On 60,000 TiffinGo deliveries, <code>LinearRegression</code> reached R² 0.820 (RMSE 4.37 min), <code>RandomForestRegressor</code> 0.850, and <code>GBTRegressor</code> <b>0.912 (RMSE 3.06)</b>. Why? Linear models cannot see that 1 pm and 8 pm are rush hours: they under-predicted those hours by about 5 minutes. For a rainy 9 km dinner order in Mumbai, linear said 46.9 min, GBT 55.6.',
    ['LinearRegression: coefficients, intercept, R² and RMSE.', 'Tree regressors: RandomForest and GBT, feature importances.', 'Reading errors by segment to choose a model.'])
cmap = concept_map('Concept map. Beginner: label is a number, features. Intermediate: LinearRegression, RMSE, MAE, R². Advanced: tree ensembles, non-linear effects, feature importance, residual analysis.',
    [[('pl', 'Pipelines', 'Lesson 10.1', B + '10-mllib/01-ml-pipelines/'), ('st', 'corr + splits', 'Lesson 4.7', B + '04-dataframes/07-statistics-and-sampling/')],
     [('lr', 'LinearRegression', 'coefficients', None), ('mt', 'RMSE · MAE · R²', 'evaluate', None), ('rf', 'RandomForest', 'averaged trees', None), ('gb', 'GBT', 'boosted trees', None)],
     [('nl', 'Non-linear', 'rush hours', None), ('fi', 'Importances', 'what matters', None), ('rs', 'Residuals', 'by segment', None), ('tu', 'Tuning + saving', 'Lesson 10.3', B + '10-mllib/03-evaluation-tuning-and-saving-models/')]],
    [('pl', 'lr'), ('st', 'lr'), ('lr', 'mt'), ('lr', 'rf'), ('rf', 'gb'), ('lr', 'nl'), ('gb', 'fi'), ('mt', 'rs'), ('gb', 'tu')],
    {'lr', 'mt', 'rf', 'gb', 'nl', 'fi', 'rs'},
    '<b>Builds on:</b> <a href="../02-feature-engineering-and-classification/">10.2</a>. <b>Next:</b> <a href="../03-evaluation-tuning-and-saving-models/">10.3</a> to tune and save, <a href="../04-clustering-and-recommendations/">10.4</a>.')
whw = why_how_where(
    'Many business questions are numbers: delivery minutes, demand tomorrow, price, revenue. Classification (10.2) predicts categories; regression predicts amounts.',
    'LinearRegression fits weights by least squares (optionally regularised with regParam/elasticNetParam). RandomForest averages many deep trees; GBT adds small trees one after another, each fixing the previous errors. Evaluate with RegressionEvaluator (rmse, mae, r2).',
    'ETA prediction, demand forecasting features, pricing, credit limits, energy load, any “how much / how long”.',
    'Linear needs hand-made features for curves and interactions; trees cannot extrapolate beyond training ranges; GBT is slower to train (27.6 s vs 3.7 s here).')
def pts(hl=-1):
    import math
    o = ''
    for i in range(22):
        x = 30 + i * 13; y = 120 - (i * 3.2) - (16 if i in (8, 9, 15, 16) else 0)
        o += box(x - 3, y - 3, 6, 6, 'amber' if i in (8, 9, 15, 16) else 'blue', rx=3)
    o += f'<line x1="28" y1="122" x2="310" y2="50" stroke="currentColor" class="s-acc" stroke-width="2"/>'
    if hl == 1:
        o += box(250, 18, 104, 22, 'amber', rx=5) + t(302, 33, 'rush hours missed', 7.4, bold=True)
    return o + t(170, 136, 'distance (km) →   ·   minutes ↑', 7.2)
scene_svg = scene('Delivery minutes plotted against distance with a straight regression line; amber points at rush hours sit above the line because a linear model cannot capture them.', pts(1),
                  'A straight line is a good start, <tspan font-weight="700" class="s-acc">but rush hours bend it</tspan>.')
dialogue = '''K> Sir, the app shows a fixed “30–40 min”. Customers complain. Can we predict real minutes?
A> Yes: regression. Label = minutes, features = km, hour, rain, city. Start with LinearRegression.
R> And if it is not linear? Rain plus long distance is worse than both together.
A> Then trees: RandomForest and GBT. We will compare all three on the same test set.'''
lv = '''
LEVELS> Regression at three levels
L1> The tiffin uncle’s rule
      <ul>
        <li>“10 minutes to pack, 2.5 minutes per km, add more if it rains.” That rule is a linear model. A trained eye that also knows “8 pm is chaos” is a tree model.</li>
      </ul>
L2> The API (pyspark.ml.regression)
      <ul>
        <li><code>Linear<wbr>Regression(labelCol, regParam, elastic<wbr>NetParam)</code> → <code>model.coefficients</code>, <code>intercept</code>, <code>summary.r2</code>, <code>summary.<wbr>rootMeanSquared<wbr>Error</code>.</li>
        <li><code>RandomForest<wbr>Regressor(numTrees, maxDepth)</code>, <code>GBT<wbr>Regressor(maxIter, maxDepth, stepSize)</code>, also <code>DecisionTree<wbr>Regressor</code>, <code>Generalized<wbr>Linear<wbr>Regression</code>, <code>Isotonic<wbr>Regression</code>, <code>FMRegressor</code>.</li>
        <li><code>Regression<wbr>Evaluator(metricName="rmse" | "mae" | "r2")</code>; <code>feature<wbr>Importances</code> for tree models.</li>
      </ul>
L3> Practical details
      <ul>
        <li>Encode categories with StringIndexer + OneHotEncoder; one category is dropped (baseline), so coefficients read “compared with Delhi”.</li>
        <li>Group errors by segment (hour, city) to find what the model misses: our linear model was −5.5 min at 13:00.</li>
        <li>For linear models, add features (hour buckets, km × rain) or switch to trees; tune with CrossValidator (10.3).</li>
      </ul>
/LEVELS
'''
DIS = figure('Dissection of the linear model: intercept 9.09 minutes, 2.62 minutes per km, 7.7 minutes for rain, 4.05 minutes extra in Mumbai compared with Delhi.',
    t(16, 22, 'The learned linear rule (real)', 8.6, 'ink', anchor='start', bold=True) +
    fields(16, 34, [('9.09', 'blue', 1), ('+ 2.62 × km', 'green', 2), ('+ 7.7 × rain', 'amber', 3), ('+ 4.05 Mumbai', 'violet', 4)]) +
    legend(16, 84, [(1, 'Intercept', 'base minutes'), (2, 'Coefficient', 'per extra km'), (3, 'Binary feature', 'rain = 1'),
                    (4, 'One-hot', 'vs Delhi (baseline)')], size=8, gap=15, w=90),
    h=156, caption='True rule used to generate the data: 2.5 per km, +6 rain, +4 Mumbai, plus rush hours.')
extra = '''

  <h3>Dissect the linear model</h3>
''' + DIS
types_html = table(['Regressor', 'Idea', 'Strength', 'Watch out'], [
    ['LinearRegression', 'weighted sum', 'fast, explainable', 'misses curves/interactions'],
    ['DecisionTreeRegressor', 'one tree of rules', 'simple, non-linear', 'overfits'],
    ['RandomForestRegressor', 'average of many trees', 'robust', 'bigger models'],
    ['GBTRegressor', 'trees fix previous errors', 'often most accurate', 'slower, sequential'],
    ['GeneralizedLinearRegression', 'linear + link function', 'counts (Poisson), skewed', 'choose family']], minw=600)
warn = 'Do not compare models on training error: compare on the same held-out test split (randomSplit with a seed). And remember trees do not extrapolate: a 25 km order (never seen in training) gets roughly the prediction of the longest trips seen.'
steps = [
    ('Step 1 · LinearRegression',
     code('python', 'l105_reg.py', 'prep = [StringIndexer(inputCol="city", outputCol="ci"), OneHotEncoder(inputCols=["ci"], outputCols=["cv"]),\n        VectorAssembler(inputCols=["km", "hour", "rain", "cv"], outputCol="features")]\nlr = Pipeline(stages=prep + [LinearRegression(labelCol="mins")]).fit(train)', sec('== 1)', '== 2)')),
     'Coefficients match the hidden rule closely: about 2.6 min per km, ~8 for rain, +4 in Mumbai.'),
    ('Step 2 · Three models, one test set',
     code('python', 'l105_reg.py', 'for est in [LinearRegression(...), RandomForestRegressor(numTrees=40, maxDepth=8), GBTRegressor(maxIter=40, maxDepth=5)]:\n    p = Pipeline(stages=prep + [est]).fit(train).transform(test)\n    RegressionEvaluator(labelCol="mins", metricName="rmse").evaluate(p)', sec('== 2)', '== 3)')),
     'GBT wins (RMSE 3.06, R² 0.912) but takes 7× longer to train than linear.'),
    ('Step 3 · Where linear fails',
     code('python', 'l105_reg.py', 'lr.transform(test).withColumn("err", prediction - mins).groupBy("hour").agg(avg("err"))', sec('== 3)', '== 4)')),
     'At 13:00 and 20:00 linear under-predicts by ~5 min: one slope for “hour” cannot model two peaks.'),
    ('Step 4 · Feature importances',
     code('python', 'l105_reg.py', 'gm.stages[-1].featureImportances', sec('== 4)', '== 5)')),
     'Hour (0.507) and km (0.420) drive the trees; city adds little once rush hours are known.'),
    ('Step 5 · Predict one order',
     code('python', 'l105_reg.py', 'new = spark.createDataFrame([(9.0, 20, 1, "Mumbai", 0.0)], df.schema)\nlr.transform(new); gbt.transform(new)', sec('== 5)')),
     'True rule gives ≈ 54.5 min: GBT 55.6 is close; linear 46.9 would anger a hungry customer.'),
]
see = [term([('km 2.62 rain 7.7', G), ('R2 0.825', W)], size=7.0), term([('LR  RMSE 4.37', W), ('RF  RMSE 3.98', W), ('GBT RMSE 3.06', G)], size=6.8),
       term([('13h err -5.5', RD), ('20h err -4.5', RD)], size=7.0), term([('hour 0.507', G), ('km 0.420', G)], size=7.0), term([('linear 46.9', RD), ('GBT 55.6', G)], size=7.0)]
B1 = [pts(-1), pts(-1), pts(1), pts(1), pts(1)]
B1 = [b + cap(c, '', tn, y=140, h=26) for b, c, tn in zip(B1, ['Line fitted', 'Trees win', 'Peaks missed', 'Hour matters', 'Better ETA'], ['blue', 'green', 'red', 'amber', 'green'])]
two = anim_two('Regression models', 'Predicting delivery minutes', 'Real outputs (local[2])', 'Numbers, not classes', see, B1, ['Linear.', 'Compare.', 'Errors.', 'Importance.', 'Predict.'], ['0.825.', 'GBT.', '−5.5.', 'Hour.', '55.6.'])
pe = peel('GBTRegressor, layer by layer', 'How boosting fixes errors step by step. (Simplified.)',
    [('Start', ''), ('Residuals', ''), ('Small tree', ''), ('Add', ''), ('Repeat', ''), ('Predict', '')],
    [['Start', 'predict the mean', '~28 min', ''], ['Residuals', 'actual − prediction', 'per row', ''], ['Small tree', 'fits residuals', 'depth 5', ''],
     ['Add', 'prediction += step × tree', '', ''], ['Repeat', 'maxIter 40', '', ''], ['Predict', 'sum of all trees', '55.6 min', '']],
    ['Mean.', 'Errors.', 'Tree.', 'Add.', 'Iterate.', 'Sum.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'ETA for the app', 'Fixed “30–40 min” angers users. (Typical.)', ('GBTRegressor', 'Per-order minutes'), [
    ('Collect history', 'km, hour, rain, city', 'Data.', 'blue'), ('Baseline linear', 'RMSE 4.37', 'Start.', 'amber'),
    ('GBT', 'RMSE 3.06', 'Improve.', 'green'), ('Errors by hour', 'peaks fixed', 'Check.', 'green'),
    ('Serve nightly model', 'saved pipeline', 'Operate.', 'blue')], ['Data.', 'Baseline.', 'Boost.', 'Check.', 'Serve.'], 'scenario-eta') + \
       five('Real-time scenario 2', 'Explain to business', 'Ops wants reasons. (Typical.)', ('Coefficients + importances', 'Explainable'), [
    ('Ops asks “why late?”', '', 'Ask.', 'blue'), ('Linear coefficients', '+7.7 min rain', 'Explain.', 'green'),
    ('GBT importances', 'hour, km', 'Rank.', 'green'), ('Segment errors', '13:00, 20:00', 'Find.', 'amber'),
    ('Add riders at peaks', 'action', 'Act.', 'violet')], ['Ask.', 'Coefs.', 'Importance.', 'Segments.', 'Act.'], 'scenario-explain') + \
       five('Real-time scenario 3 · advanced', 'New city, longer trips', 'Extrapolation risk. (Typical.)', ('Monitor + retrain', 'Trees do not extrapolate'), [
    ('Launch Bengaluru', 'unseen city', 'Change.', 'blue'), ('Trips up to 25 km', 'outside training', 'Risk.', 'red'),
    ('Errors rise', 'monitor RMSE daily', 'Detect.', 'amber'), ('Fallback linear for long trips', 'blend', 'Mitigate.', 'green'),
    ('Retrain with new data', 'weekly', 'Fix.', 'green')], ['Launch.', 'Range.', 'Monitor.', 'Blend.', 'Retrain.'], 'scenario-drift')
assemble(HERE, h2_story='From “30–40 minutes” to a real ETA', hook_html=hk,
    narration='TiffinGo shows every customer the same delivery window. The product team wants a per-order prediction in minutes, trained on 60,000 past deliveries.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Regression in MLlib',
    formal='<b>Regression</b> is supervised learning with a continuous label. <b>LinearRegression</b> fits weights minimising squared error (with optional L1/L2 regularisation); <b>RandomForestRegressor</b> averages bootstrap-trained decision trees; <b>GBTRegressor</b> builds trees sequentially on the residuals of the current ensemble (gradient boosting). Models are compared with RMSE, MAE and R² on held-out data.',
    simple='The model learns how much each input (distance, rain, time) adds to the answer, and then predicts a number for a new order.',
    term_rows=[('Label', 'Number to predict.'), ('Coefficient', 'Effect of one feature.'), ('Intercept', 'Base value.'), ('RMSE', 'Typical error, big errors weigh more.'), ('MAE', 'Average absolute error.'), ('R²', 'Share of variance explained.'), ('Residual', 'actual − predicted.'), ('Boosting', 'Trees fix errors in turn.')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('High R² on train is enough.', 'Compare on test.', 'Step 2.'),
               ('Linear handles any pattern.', 'Rush hours missed by ~5 min.', 'Step 3.'),
               ('The most accurate model is always best.', 'GBT took 7× longer; explainability matters.', 'Step 2.')],
    exam='“Regression algorithms in Spark ML?” LinearRegression (regParam, elasticNetParam), Generalized<wbr>Linear<wbr>Regression, DecisionTree/<wbr>RandomForest/<wbr>GBTRegressor, Isotonic<wbr>Regression, FMRegressor; metrics rmse, mae, r2 via Regression<wbr>Evaluator; feature<wbr>Importances for trees; one-hot baseline.',
    types_h2='Regressors in pyspark.ml', types_html=types_html, warn=warn,
    steps_h2='Predicting delivery minutes', steps_intro='All outputs are real: PySpark 4.3.0 MLlib, local[2], 60,000 synthetic TiffinGo deliveries generated with a fixed seed.',
    steps=steps, two=two, peel_intro='Now peel GBT.', peel_html=pe,
    scen_intro='Three live scenarios: ETA, explaining, and drift.', scen=scen,
    uc_h2='Regression at work', ucs=[uc_('eta', 'eta', 'blue', '1. Delivery ETA', 'Minutes per order.', ['History', '*GBT', 'App']),
        uc_('dem', 'demand', 'green', '2. Demand', 'Orders tomorrow per kitchen.', ['Sales', '*Regressor', 'Stock']),
        uc_('price', 'price', 'amber', '3. Pricing', 'Fair price per dish.', ['Menu', '*Linear', 'Price']),
        uc_('energy', 'energy', 'violet', '4. Energy load', 'Kitchen power use.', ['Meters', '*RF', 'Plan'])],
    uc_note='Examples are simplified descriptions of common practice.',
    pre='<b>Before you start:</b> <a href="../02-feature-engineering-and-classification/">10.2 Features</a>.')
