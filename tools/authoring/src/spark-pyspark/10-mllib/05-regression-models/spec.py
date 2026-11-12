import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from svgkit import scn
BODY = body(HERE)
META = dict(module='10-mllib', lesson='05-regression-models', n='10.5', module_label='Module 10 · Machine learning with MLlib',
    title='Regression models',
    desc='Regression in PySpark MLlib: LinearRegression coefficients, intercept, R² and RMSE; RandomForestRegressor and GBTRegressor; feature importances; error analysis by segment. Real PySpark 4.3 lab predicting delivery minutes.',
    og_desc='Linear R² 0.820 vs GBT 0.912: predicting delivery minutes with PySpark 4.3 regression models.',
    minutes=22, level='Intermediate',
    lead='Predict a <b>number</b>, not a class. We estimate delivery minutes with <b>LinearRegression</b>, <b>RandomForest</b> and <b>GBT</b>, read coefficients and importances, and find where each model fails. <b>All outputs are real.</b>',
    chips=['GBT RMSE 3.06', 'Rush hours −5.5 min', 'Coefficients explained', 'Runs in your browser (Python)'])
MAIN = '''# Least squares by hand: minutes = a + b * km
km   = [1, 2, 4, 6, 8, 10]
mins = [13, 15, 20, 26, 30, 36]
n = len(km); mk = sum(km) / n; mm = sum(mins) / n
b = sum((x - mk) * (y - mm) for x, y in zip(km, mins)) / sum((x - mk) ** 2 for x in km)
a = mm - b * mk
print(f"minutes = {a:.2f} + {b:.2f} * km")
pred = [a + b * x for x in km]
rmse = (sum((p - y) ** 2 for p, y in zip(pred, mins)) / n) ** 0.5
ss_tot = sum((y - mm) ** 2 for y in mins)
r2 = 1 - sum((p - y) ** 2 for p, y in zip(pred, mins)) / ss_tot
print("RMSE", round(rmse, 2), " R2", round(r2, 3))
'''
RUN = dict(heading='Run the code: a regression line by hand', intro='<p>Fit, predict, measure. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('b = sum((x - mk) * (y - mm) for x, y in zip(km, mins)) / sum((x - mk) ** 2 for x in km)', 'Slope = covariance ÷ variance.'), ('r2 = 1 - sum((p - y) ** 2 for p, y in zip(pred, mins)) / ss_tot', 'R² = 1 − unexplained ÷ total.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>.', code=None),
        dict(label='2 · Predict first: 9 km', hint='<b>Predict first:</b> use the lab rule.', code='print(round(9.09 + 2.62 * 9 + 7.7 + 4.05, 1))\n'),
        dict(label='3 · MAE vs RMSE', hint='One big error.', code='e = [1, 1, 1, 10]\nprint(sum(map(abs, e)) / 4, round((sum(x * x for x in e) / 4) ** 0.5, 2))\n'),
        dict(label='4 · Boosting', hint='Add trees to residuals.', code='pred, target = 28.0, 55.0\nfor i in range(5):\n    pred += 0.5 * (target - pred)\n    print(round(pred, 1))\n'),
        dict(label='5 · Spot the error', hint='Train vs test.', expect='error', code='train_r2, test_r2 = 0.99, 0.61\nif train_r2 - test_r2 > 0.2:\n    raise ValueError("overfitting: judge models on the test split")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC', intro='<p>PySpark 4.x. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Run the lab', cmd='python3 l105_reg.py', file='terminal', output='  GBTRegressor           RMSE  3.06  MAE  2.44  R2 0.912', note='~1 minute.'),
           dict(title='2 · Residuals', cmd='lr.transform(test).select((F.col("prediction")-F.col("mins")).alias("err")).summary().show()', file='python', output='', note='Error spread.')])
TRACE = dict(heading='One prediction step by step', intro='<p>Linear rule from the lab.</p>',
    code='km, rain, mumbai = 9, 1, 1\nmins = 9.09 + 2.62 * km + 7.7 * rain + 4.05 * mumbai\nprint(round(mins, 1))\n', notes={1: 'Weighted sum :: plus intercept.'})
WORKED_INTRO = 'Three modelling decisions.'
EXAMPLES = [
    dict(level='b', tag='metric', title='Pick a metric', problem='<p>Report error in minutes.</p>', inp='metrics',
         approach=['RMSE or MAE in minutes.', 'R² for variance.', 'Same test set.'], code='print({"rmse": 3.06, "mae": 2.44})\n', notes={1: 'Minutes.'}, tryit='Step 2.'),
    dict(level='i', tag='segments', title='Find blind spots', problem='<p>Where does linear fail?</p>', inp='errors',
         approach=['Error by hour.', 'Spot peaks.', 'Add features or trees.'], code='err = {12: 0.9, 13: -5.5, 20: -4.5}\nprint([h for h, e in err.items() if abs(e) > 3])\n', notes={1: 'Rush hours.'}, tryit='Step 3.'),
    dict(level='a', tag='trade-off', title='Accuracy vs cost', problem='<p>GBT or linear?</p>', inp='timings',
         approach=['Compare RMSE.', 'Compare training time.', 'Need explainability?'], code='print({"LR": (4.37, 3.7), "GBT": (3.06, 27.6)})\n', notes={1: 'RMSE, seconds.'}, tryit='Step 2.')]
QUIZ = mix([
    dict(q='Beginner: Regression predicts…', options=['A class', 'A number', 'A cluster', 'A rule'], answer=1, why='Continuous label.'),
    dict(q='Beginner: RMSE is in…', options=['Percent', 'Units of the label', 'Seconds always', 'No units'], answer=1, why='Minutes here.'),
    dict(q='Beginner: R² of 1 means…', options=['Useless', 'Perfect fit', 'Overfit always', 'Error'], answer=1, why='All variance explained.'),
    dict(q='Intermediate: Best model in our lab…', options=['Linear', 'RandomForest', 'GBT', 'All equal'], answer=2, why='RMSE 3.06.'),
    dict(q='Intermediate: Mumbai coefficient 4.05 means…', options=['4 km', '+4 min vs Delhi', '4% faster', 'Error'], answer=1, why='One-hot baseline.'),
    dict(q='Intermediate: Linear missed…', options=['Rain', 'Rush hours', 'Distance', 'Nothing'], answer=1, why='Step 3.'),
    dict(q='Advanced: GBT builds trees…', options=['In parallel independently', 'Sequentially on residuals', 'Randomly', 'Once'], answer=1, why='Boosting.'),
    dict(q='Advanced: Trees on a 25 km order (max 12 in training)…', options=['Extrapolate well', 'Cannot extrapolate', 'Error', 'Return 0'], answer=1, why='Range limit.')])
REVISION = ['Regression = numeric label; RegressionEvaluator rmse/mae/r2.', 'Linear: 9.09 + 2.62·km + 7.7·rain + 4.05·Mumbai; R² 0.820.', 'RF 0.850, GBT 0.912 (RMSE 3.06) but 27.6 s vs 3.7 s.',
    'Check errors by segment: rush hours −5.5 min.', 'featureImportances: hour 0.507, km 0.420.']
FAQ = [('Which regressor to start with?', 'LinearRegression as a baseline, then a tree ensemble.'),
    ('How to regularise linear?', 'regParam (strength) and elasticNetParam (0 = L2 ridge, 1 = L1 lasso).'),
    ('Can I see p-values?', 'Yes for LinearRegression with solver="normal": summary.pValues; or GeneralizedLinearRegression.'),
    ('How to save?', 'pipelineModel.save(path); PipelineModel.load(path) (10.3).')]
PRACTICE_INTRO = 'Regression programs.'
PROBLEMS = [
    dict(level='easy', title='Predict', stmt='a + b·x.', inp='floats', code='print(9.09 + 2.62 * 5)\n', explain='22.19.'),
    dict(level='easy', title='Residual', stmt='actual − predicted.', inp='floats', code='print(round(30 - 27.4, 1))\n', explain='2.6.'),
    dict(level='easy', title='MAE', stmt='Mean absolute error.', inp='list', code='e = [2, -3, 1]\nprint(sum(map(abs, e)) / 3)\n', explain='2.0.'),
    dict(level='medium', title='RMSE', stmt='Root mean square.', inp='list', code='e = [2, -3, 1]\nprint(round((sum(x * x for x in e) / 3) ** 0.5, 2))\n', explain='2.16.'),
    dict(level='medium', title='R²', stmt='1 − SSE/SST.', inp='floats', code='print(round(1 - 120 / 1000, 2))\n', explain='0.88.'),
    dict(level='medium', title='One-hot', stmt='Encode cities.', inp='list', code='cities = ["Delhi", "Mumbai", "Pune"]\nprint({c: [int(c == k) for k in cities[1:]] for c in cities})\n', explain='Delhi baseline.'),
    dict(level='business', title='Late orders', stmt='Late if ETA − 10.', inp='floats', code='print(55 - 46.9 > 5)\n', explain='Linear would mislead.'),
    dict(level='business', title='Error gain', stmt='RMSE improvement.', inp='floats', code='print(round((4.37 - 3.06) / 4.37 * 100), "% better")\n', explain='30%.')]
SCN_INTRO = 'Regression interview questions.'
SCENARIOS = (scn('Any company · data', 'Fresher', '“Regression vs classification?”', 'Explain.', 'answer?', '<p>Regression predicts a continuous number (minutes); classification predicts a category. Different evaluators: RMSE/MAE/R² vs accuracy/AUC.</p>', '“Same thing.”') +
    scn('Delivery app', 'Mid-level', 'ETA model', 'Design.', 'answer?', '<ul><li>Features, linear baseline, GBT, errors by segment.</li></ul>', 'Average of past orders.') +
    scn('Data', 'Mid-level', 'Linear underfits', 'Peaks missed.', 'fix?', '<ul><li>Hour buckets or tree ensemble.</li></ul>', 'More iterations.') +
    scn('Ops', 'Senior', 'New city', 'Errors rising.', 'answer?', '<ul><li>Monitor, blend, retrain; trees do not extrapolate.</li></ul>', 'Ignore.'))
