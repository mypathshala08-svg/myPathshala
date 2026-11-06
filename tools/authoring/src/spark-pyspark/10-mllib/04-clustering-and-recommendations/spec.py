import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from svgkit import scn
BODY = body(HERE)
META = dict(module='10-mllib', lesson='04-clustering-and-recommendations', n='10.4', module_label='Module 10 · Machine learning with MLlib',
    title='Clustering and recommendations',
    desc='Unsupervised learning and recommendations in PySpark MLlib: KMeans with scaling and silhouette to choose k, ALS collaborative filtering with rank, regParam and cold-start strategy, implicit feedback, and FPGrowth frequent itemsets with confidence and lift. Real PySpark 4.3 lab on TiffinGo data.',
    og_desc='Three customer segments, dessert recommendations and thali + lassi combos: KMeans, ALS and FPGrowth in PySpark 4.3.',
    minutes=24, level='Intermediate',
    lead='What can ML do without labels? We find <b>customer segments</b> with KMeans, <b>recommend dishes</b> with ALS, and discover <b>combos</b> with FPGrowth. <b>All outputs are real.</b>',
    chips=['Silhouette 0.884 at k=3', 'ALS + cold start', 'Lift 4.5', 'Runs in your browser (Python)'])
MAIN = '''# KMeans by hand: assign to nearest centre, move centres (2 features, already scaled)
pts = [(0.1, 0.2), (0.0, 0.1), (0.2, 0.0), (2.0, 2.1), (2.2, 1.9), (1.9, 2.0), (4.0, 0.1), (4.1, 0.3)]
centres = [(0.0, 0.0), (2.0, 2.0), (4.0, 0.0)]
for it in range(3):
    groups = {i: [] for i in range(len(centres))}
    for p in pts:
        i = min(range(len(centres)), key=lambda c: (p[0] - centres[c][0])**2 + (p[1] - centres[c][1])**2)
        groups[i].append(p)
    centres = [(sum(x for x, _ in g) / len(g), sum(y for _, y in g) / len(g)) for g in groups.values()]
    print(f"iteration {it}: sizes {[len(g) for g in groups.values()]}")
print("centres:", [(round(a, 2), round(b, 2)) for a, b in centres])
'''
RUN = dict(heading='Run the code: KMeans by hand', intro='<p>Assign, move, repeat. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('        i = min(range(len(centres)), key=lambda c: (p[0] - centres[c][0])**2 + (p[1] - centres[c][1])**2)', 'Nearest centre by squared distance.'), ('    centres = [(sum(x for x, _ in g) / len(g), sum(y for _, y in g) / len(g)) for g in groups.values()]', 'Centre = mean of its points.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>. Start with bad centres.', code=None),
        dict(label='2 · Predict first: lift', hint='<b>Predict first:</b> confidence 0.84, P(lassi) 0.19.', code='print(round(0.84 / 0.19, 1))\n'),
        dict(label='3 · Dot product', hint='ALS score = user · item.', code='u, d = [1.2, 0.1, -0.3], [2.0, 0.5, 0.1]\nprint(round(sum(a * b for a, b in zip(u, d)), 2))\n'),
        dict(label='4 · Scale', hint='z-score a column.', code='xs = [180, 220, 650]\nm = sum(xs) / 3; s = (sum((x - m) ** 2 for x in xs) / 3) ** 0.5\nprint([round((x - m) / s, 2) for x in xs])\n'),
        dict(label='5 · Spot the error', hint='NaN RMSE.', expect='error', code='import math\nrmse = float("nan")\nif math.isnan(rmse):\n    raise ValueError("RMSE is NaN: unseen users in test; set coldStartStrategy=\\"drop\\"")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC', intro='<p>PySpark 4.x. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Run the lab', cmd='python3 l104_ml.py', file='terminal', output='  k=3  silhouette 0.884', note='~1 minute.'),
           dict(title='2 · Recommend', cmd='model.recommendForAllUsers(3).show(5, truncate=False)', file='python', output='', note='Top-3 per user.')])
TRACE = dict(heading='One rule step by step', intro='<p>Support, confidence, lift.</p>',
    code='both, thali, lassi, n = 336, 400, 380, 2000\nconf = both / thali\nlift = conf / (lassi / n)\nprint(round(conf, 2), round(lift, 1))\n', notes={2: 'Confidence :: P(lassi | thali).', 3: 'Lift :: vs average.'})
WORKED_INTRO = 'Three unsupervised decisions.'
EXAMPLES = [
    dict(level='b', tag='KMeans · k', title='Choose k', problem='<p>How many segments?</p>', inp='scores',
         approach=['Silhouette for k = 2..8.', 'Pick the peak.', 'Check business sense.'], code='s = {2: 0.65, 3: 0.884, 4: 0.823}\nprint(max(s, key=s.get))\n', notes={1: 'k = 3.'}, tryit='Step 1.'),
    dict(level='i', tag='ALS · eval', title='Evaluate safely', problem='<p>Test set has new users.</p>', inp='config',
         approach=['coldStartStrategy="drop".', 'RMSE on known users.', 'Fallback for new users.'], code='print({"coldStartStrategy": "drop"})\n', notes={1: 'Avoid NaN.'}, tryit='Step 3.'),
    dict(level='a', tag='FPGrowth · rules', title='Pick combos', problem='<p>Which bundles to promote?</p>', inp='rules',
         approach=['Filter lift > 2.', 'Confidence > 0.6.', 'Enough support.'], code='rules = [("thali", "lassi", 0.84, 4.5), ("water", "chai", 0.7, 1.1)]\nprint([r for r in rules if r[3] > 2])\n', notes={1: 'Lift matters.'}, tryit='Step 5.')]
QUIZ = mix([
    dict(q='Beginner: KMeans needs…', options=['Labels', 'Number of clusters k', 'Ratings', 'Baskets'], answer=1, why='Unsupervised, k given.'),
    dict(q='Beginner: ALS is used for…', options=['Clustering', 'Recommendations', 'Text', 'Graphs'], answer=1, why='Collaborative filtering.'),
    dict(q='Beginner: FPGrowth finds…', options=['Clusters', 'Items bought together', 'Ratings', 'Outliers only'], answer=1, why='Itemsets.'),
    dict(q='Intermediate: Best k in our lab was…', options=['2', '3', '4', '5'], answer=1, why='0.884.'),
    dict(q='Intermediate: An unseen user with coldStartStrategy="nan" gives…', options=['0', 'NaN RMSE', 'Error', 'Random'], answer=1, why='Step 3.'),
    dict(q='Intermediate: Lift > 1 means…', options=['Unpopular', 'Items appear together more than by chance', 'Error', 'Negative'], answer=1, why='Real link.'),
    dict(q='Advanced: Before KMeans you should…', options=['Shuffle', 'Scale features', 'Sort', 'Cache only'], answer=1, why='Distances.'),
    dict(q='Advanced: Clicks instead of ratings need…', options=['coldStart', 'implicitPrefs=True', 'rank 100', 'FPGrowth'], answer=1, why='Implicit feedback.')])
REVISION = ['KMeans: scale → fit → silhouette; lab best k=3 (0.884).', 'Segments: premium, frequent, low-spend.',
    'ALS: rank, maxIter, regParam, coldStartStrategy; drop → RMSE 1.06; implicitPrefs for clicks.', 'FPGrowth: thali→lassi conf 0.84, lift 4.5.', 'Use pyspark.ml (DataFrame), not pyspark.mllib (RDD).']
FAQ = [('Why was RMSE poor at first?', 'With only ~4 ratings per user, ALS could not place users; more ratings per user fixed it.'),
    ('Can I save these models?', 'Yes, like any pyspark.ml model: model.save(path) (Lesson 10.3).'),
    ('How do I recommend to new users?', 'Use popular items, content features or ask a few questions until they have ratings.'),
    ('Is KMeans good for odd-shaped clusters?', 'No; consider GaussianMixture or density-based methods outside MLlib.')]
PRACTICE_INTRO = 'Unsupervised programs.'
PROBLEMS = [
    dict(level='easy', title='Distance', stmt='Squared distance.', inp='points', code='a, b = (0, 0), (3, 4)\nprint((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)\n', explain='25.'),
    dict(level='easy', title='Mean', stmt='Centre of points.', inp='list', code='ps = [(1, 1), (3, 3)]\nprint((sum(x for x, _ in ps) / 2, sum(y for _, y in ps) / 2))\n', explain='(2, 2).'),
    dict(level='easy', title='Confidence', stmt='336 / 400.', inp='ints', code='print(336 / 400)\n', explain='0.84.'),
    dict(level='medium', title='Nearest', stmt='Nearest centre index.', inp='lists', code='p, cs = (2.1, 1.9), [(0, 0), (2, 2), (4, 0)]\nprint(min(range(3), key=lambda i: (p[0] - cs[i][0]) ** 2 + (p[1] - cs[i][1]) ** 2))\n', explain='1.'),
    dict(level='medium', title='Top-N', stmt='Top 2 scores.', inp='dict', code='s = {"kulfi": 3.8, "idli": 1.2, "jalebi": 3.8}\nprint(sorted(s, key=s.get, reverse=True)[:2])\n', explain='Desserts.'),
    dict(level='medium', title='RMSE', stmt='RMSE of errors.', inp='list', code='e = [1, -1, 0.5]\nprint(round((sum(x * x for x in e) / 3) ** 0.5, 2))\n', explain='0.87.'),
    dict(level='business', title='Bundle revenue', stmt='Combo uplift.', inp='ints', code='print(400 * 0.1 * 45, "₹ extra per day")\n', explain='10% more lassi.'),
    dict(level='business', title='Segment size', stmt='Premium share.', inp='ints', code='print(round(999 / 3000 * 100), "%")\n', explain='33%.')]
SCN_INTRO = 'Unsupervised ML interview questions.'
SCENARIOS = (scn('Any company · data', 'Fresher', '“Which MLlib algorithm for segmentation?”', 'Explain.', 'answer?', '<p>KMeans (or BisectingKMeans/GaussianMixture) on scaled behavioural features, choosing k with the silhouette score and business sense.</p>', '“Logistic regression.”') +
    scn('E-commerce', 'Mid-level', 'Recommendations', 'Design.', 'answer?', '<ul><li>ALS on ratings or implicit clicks; cold-start fallback.</li></ul>', 'Random items.') +
    scn('Data', 'Mid-level', 'NaN RMSE', 'ALS eval.', 'fix?', '<ul><li>coldStartStrategy="drop".</li></ul>', 'Fill NaN with 0.') +
    scn('Retail', 'Senior', 'Bundles', 'Pick promotions.', 'answer?', '<ul><li>FPGrowth rules filtered by lift, confidence, support; A/B test.</li></ul>', 'Most popular items.'))
