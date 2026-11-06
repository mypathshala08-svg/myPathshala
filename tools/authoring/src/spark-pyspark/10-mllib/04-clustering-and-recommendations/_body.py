import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit2 import *
C = 'l104_ml.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('No labels, no “right answers”. Can Spark still find customer groups, suggest dishes and spot what people order together?',
    'Yes: <b>unsupervised</b> and <b>recommendation</b> algorithms. On TiffinGo data, <b>KMeans</b> found three customer segments (silhouette 0.884 at k=3, best of 2–5); <b>ALS</b> learned tastes from 10,795 ratings and recommended kulfi, jalebi and rasgulla to a dessert lover; <b>FPGrowth</b> found that 87% of lassi orders also contain a thali (lift 4.5). One brand-new user turned the whole RMSE into <code>NaN</code> until we set <code>coldStartStrategy="drop"</code>.',
    ['Clustering with KMeans: scaling, choosing k, reading segments.',
     'Recommendations with ALS: ratings, rank, regularisation, cold start.',
     'Frequent itemsets and association rules with FPGrowth.'])
cmap = concept_map('Concept map. Beginner: supervised vs unsupervised, features. Intermediate: KMeans, silhouette, ALS, FPGrowth. Advanced: scaling, cold start, implicit feedback, lift, RDD mllib vs DataFrame ml.',
    [[('pl', 'ML pipelines', 'Lesson 10.1', B + '10-mllib/01-ml-pipelines/'), ('fe', 'Features', 'Lesson 10.2', B + '10-mllib/02-feature-engineering-and-classification/')],
     [('km', 'KMeans', 'segments', None), ('sl', 'Silhouette', 'choose k', None), ('al', 'ALS', 'recommend', None), ('fp', 'FPGrowth', 'baskets', None)],
     [('sc', 'Scaling', 'StandardScaler', None), ('cs', 'Cold start', 'drop / nan', None), ('lf', 'Lift + confidence', 'rules', None), ('ev', 'Evaluate + save', 'Lesson 10.3', B + '10-mllib/03-evaluation-tuning-and-saving-models/')]],
    [('pl', 'km'), ('fe', 'km'), ('km', 'sl'), ('km', 'sc'), ('fe', 'al'), ('al', 'cs'), ('fe', 'fp'), ('fp', 'lf'), ('al', 'ev')],
    {'km', 'sl', 'al', 'fp', 'sc', 'cs', 'lf'},
    '<b>Builds on:</b> <a href="../01-ml-pipelines/">10.1</a>, <a href="../02-feature-engineering-and-classification/">10.2</a>. <b>Next:</b> <a href="../../11-spark-in-production/01-spark-submit-and-deploy-modes/">Module 11</a>.')
whw = why_how_where(
    'Most business data has no labels: nobody tagged customers as “premium” or dishes as “goes with lassi”. These algorithms find structure that marketing, menus and apps can use.',
    'KMeans repeatedly assigns points to the nearest centre and moves centres (distance-based, so scale features). ALS factorises the sparse user × item rating matrix into user and item vectors by alternating least squares. FPGrowth counts frequent itemsets with an FP-tree and derives rules with confidence and lift.',
    'Customer segmentation, store clustering, “you may also like”, menu bundles, cross-sell, basket analysis; at a scale where a single machine is not enough.',
    'KMeans assumes round clusters of similar size; ALS cannot score unseen users or items (cold start) and needs enough ratings per user; FPGrowth can explode with low minSupport.')

def km(hl=-1):
    pts = [(40, 70), (52, 60), (46, 82), (60, 74), (140, 40), (152, 50), (160, 36), (148, 30), (250, 90), (262, 100), (240, 104), (256, 82)]
    tones = ['blue'] * 4 + ['green'] * 4 + ['violet'] * 4
    o = ''.join(box(x - 4, y - 4, 8, 8, tn, rx=4) for (x, y), tn in zip(pts, tones))
    for (cx, cy), lb in [((50, 72), 'low spend'), ((150, 40), 'frequent'), ((252, 94), 'premium')]:
        o += box(cx - 6, cy - 6, 12, 12, 'acc', rx=2) + t(cx, cy + 22, lb, 7, bold=True)
    return o + t(176, 18, 'orders per month ↑ · average spend →', 7.2) + (box(300, 30, 54, 30, 'amber', rx=5) + t(327, 49, 'k = 3', 8, bold=True) if hl == 1 else '')
scene_svg = scene('KMeans groups TiffinGo customers into three segments by orders per month and average spend: low spend, frequent, and premium; each orange square is a cluster centre.', km(),
                  'No labels needed: <tspan font-weight="700" class="s-acc">the data forms groups</tspan>.')
dialogue = '''K> Sir, marketing wants “customer types” but we never labelled customers. Classification from 10.2 needs labels.
A> Then use <b>unsupervised</b> learning: KMeans finds groups by itself. And for “people like you also ordered…”, ALS learns from ratings.
R> And combos like thali + lassi?
A> FPGrowth, from baskets. Three algorithms, three business questions. Let’s run them on our data.'''

lv = '''
LEVELS> Clustering and recommendations at three levels
L1> Seating guests
      <ul>
        <li>KMeans seats similar guests at the same table. ALS guesses which dish a guest will like from guests with similar taste. FPGrowth notices that whoever orders thali usually adds lassi.</li>
      </ul>
L2> The API (pyspark.ml)
      <ul>
        <li><code>VectorAssembler</code> → <code>StandardScaler(withMean=True)</code> → <code>KMeans(k, seed)</code>; <code>ClusteringEvaluator()</code> gives the silhouette (−1…1, higher is better).</li>
        <li><code>ALS(userCol, itemCol, ratingCol, rank, maxIter, regParam, coldStartStrategy, implicitPrefs)</code>; <code>model.recommendForAllUsers(n)</code>, <code>recommendForUserSubset</code>; <code>RegressionEvaluator(metricName="rmse")</code>.</li>
        <li><code>FPGrowth(itemsCol, minSupport, minConfidence)</code> → <code>freqItemsets</code>, <code>associationRules</code> (confidence, lift, support), <code>transform</code> for predictions.</li>
      </ul>
L3> Practical details
      <ul>
        <li>Choose k by silhouette/elbow and business sense; also <code>BisectingKMeans</code>, <code>GaussianMixture</code>, <code>LDA</code> (topics).</li>
        <li>ALS: user and item ids must be integers; <code>coldStartStrategy="drop"</code> for evaluation; <code>implicitPrefs=True</code> for clicks/views (confidence, not ratings); tune rank/regParam with CrossValidator (10.3). In our first try, users with ~4 ratings gave poor test RMSE: data per user matters.</li>
        <li>Old RDD-based <code>pyspark.mllib</code> (ALS.train, KMeans.train) is in maintenance mode; use the DataFrame-based <code>pyspark.ml</code>.</li>
      </ul>
/LEVELS
'''
DIS = figure('Dissection of an association rule: if thali then lassi, confidence 0.84 means 84 percent of baskets with thali also have lassi, lift 4.5 means lassi is 4.5 times more likely with thali than on average.',
    t(16, 22, 'One association rule (real)', 8.6, 'ink', anchor='start', bold=True) +
    fields(16, 34, [('if: thali', 'blue', 1), ('then: lassi', 'green', 2), ('confidence 0.84', 'amber', 3), ('lift 4.5', 'violet', 4)]) +
    legend(16, 84, [(1, 'Antecedent', 'items already in the basket'), (2, 'Consequent', 'item suggested'), (3, 'Confidence', 'P(lassi | thali) = 84%'),
                    (4, 'Lift', 'confidence ÷ P(lassi): > 1 means a real link')], size=8, gap=15, w=90),
    h=156, caption='Lift near 1 means “just popular”, not “goes together”.')
extra = '''

  <h3>Dissect an association rule</h3>
''' + DIS

types_html = table(['Algorithm', 'Input', 'Output', 'Business question'], [
    ['KMeans', 'feature vectors', 'cluster id per row', 'what kinds of customers do we have?'], ['BisectingKMeans / GaussianMixture', 'feature vectors', 'clusters / probabilities', 'hierarchical or soft groups'],
    ['ALS', '(user, item, rating)', 'top-N items per user', 'what will this user like?'], ['FPGrowth', 'list of items per basket', 'itemsets + rules', 'what is bought together?'],
    ['LDA', 'word counts', 'topics', 'what are reviews about?'],
], minw=640)
warn = 'Always scale features before KMeans (distance-based): without StandardScaler, average spend in rupees would dominate orders per month. And never evaluate ALS with coldStartStrategy="nan" on data that may contain unseen users: a single NaN makes the whole RMSE NaN.'

steps = [
    ('Step 1 · Choose k',
     code('python', 'l104_ml.py', 'vec = VectorAssembler(inputCols=["orders_per_month", "avg_spend"], outputCol="raw").transform(cust)\nscaled = StandardScaler(inputCol="raw", outputCol="features", withMean=True).fit(vec).transform(vec)\nfor k in [2, 3, 4, 5]: ClusteringEvaluator().evaluate(KMeans(k=k, seed=1).fit(scaled).transform(scaled))', sec('== 1)', '== 2)')),
     'k=3 has the best silhouette (0.884): it matches the three behaviours hidden in our data.'),
    ('Step 2 · Read the segments',
     code('python', 'l104_ml.py', 'm.transform(scaled).groupBy("prediction").agg(count, avg orders, avg spend)', sec('== 2)', '== 3)')),
     'Premium (₹651, 6 orders), frequent (15 orders, ₹219) and low-spend (4 orders, ₹183): ready for three marketing campaigns.'),
    ('Step 3 · ALS and cold start',
     code('python', 'l104_ml.py', 'ALS(userCol="user", itemCol="dish", ratingCol="rating", rank=3, maxIter=20, regParam=0.05, coldStartStrategy=cs)\nRegressionEvaluator(metricName="rmse", labelCol="rating")', sec('== 3)', '== 4)')),
     'One unseen user (id 9999) in the test set makes RMSE NaN with “nan”; “drop” skips it: RMSE 1.06 on a 1–5 scale.'),
    ('Step 4 · Recommendations',
     code('python', 'l104_ml.py', 'model.recommendForUserSubset(users_0_1_2, 3)', sec('== 4)', '== 5)')),
     'Each user gets dishes of their own taste group, learned only from ratings.'),
    ('Step 5 · FPGrowth',
     code('python', 'l104_ml.py', 'FPGrowth(itemsCol="items", minSupport=0.1, minConfidence=0.6).fit(baskets).associationRules', sec('== 5)')),
     'Thali ↔ lassi and biryani ↔ kulfi are strong pairs (lift ≈ 4–4.5): combo offers write themselves.'),
]
see = [term([('k=2 0.650', W), ('k=3 0.884', G), ('k=4 0.823', W)], size=7.0), term([('0: 999 · 6.0 · 651', W), ('1: 964 · 15.3 · 219', W), ('2: 1037 · 4.1 · 183', W)], size=6.8),
       term([('nan  RMSE nan', RD), ('drop RMSE 1.06', G)], size=7.0), term([('user 2: kulfi, jalebi,', G), ('rasgulla', G)], size=7.0), term([('thali → lassi 0.84 4.5', G), ('biryani → kulfi 0.85 3.9', G)], size=6.8)]
B1 = [km(1), km(1), km(-1), km(-1), km(-1)]
B1 = [b + cap(c, '', tn, y=130, h=30) for b, c, tn in zip(B1, ['Best k = 3', 'Three segments', 'Cold start handled', 'Taste learned', 'Bundles found'], ['blue', 'green', 'amber', 'violet', 'green'])]
two = anim_two('Clustering and recommendations', 'Segments, tastes, baskets', 'Real outputs (local[2])', 'Groups in the data', see, B1, ['k.', 'Segments.', 'ALS.', 'Recs.', 'Rules.'], ['0.884.', '3 groups.', 'drop.', 'Top 3.', 'Lift.'])
pe = peel('ALS, layer by layer', 'Learning tastes from ratings. (Simplified.)',
    [('Matrix', ''), ('Factors', ''), ('Fix items', ''), ('Fix users', ''), ('Repeat', ''), ('Predict', '')],
    [['Matrix', '1,500 users × 12 dishes', 'most cells empty', ''], ['Factors', 'rank 3 vector', 'per user and per dish', ''], ['Fix items', 'solve users', 'least squares', ''],
     ['Fix users', 'solve items', 'least squares', ''], ['Repeat', 'maxIter 20', 'regParam 0.05', ''], ['Predict', 'user · dish', '= expected rating', 'top-N']],
    ['Sparse.', 'Vectors.', 'Users.', 'Items.', 'Iterate.', 'Score.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'Segments for campaigns', 'Marketing wants customer types. (Typical.)', ('KMeans', 'Scale, choose k, profile'), [
    ('Features per customer', 'orders, spend, recency', 'Prepare.', 'blue'), ('Scale + KMeans', 'k by silhouette', 'Cluster.', 'green'),
    ('Profile segments', 'averages per cluster', 'Explain.', 'green'), ('Name them', 'premium, frequent, low', 'Business.', 'amber'),
    ('Refresh monthly', 'saved pipeline', 'Operate.', 'blue')], ['Prepare.', 'Cluster.', 'Profile.', 'Name.', 'Refresh.'], 'scenario-seg') + \
       five('Real-time scenario 2', 'NaN in evaluation', 'Recommendation metrics broken. (Typical.)', ('coldStartStrategy', 'drop for evaluation'), [
    ('RMSE = NaN', 'dashboard broken', 'Alarm.', 'red'), ('New users in test', 'no factors', 'Cause.', 'amber'),
    ('coldStartStrategy="drop"', 'evaluate known users', 'Fix.', 'green'), ('New users: popular items', 'fallback list', 'Serve.', 'green'),
    ('Retrain daily', 'new users join', 'Operate.', 'blue')], ['NaN.', 'Cold.', 'Drop.', 'Fallback.', 'Retrain.'], 'scenario-cold') + \
       five('Real-time scenario 3 · advanced', 'Clicks, not ratings', 'Implicit feedback. (Typical.)', ('implicitPrefs=True', 'Confidence from counts'), [
    ('Only views and orders', 'no stars', 'Data.', 'blue'), ('ALS(implicitPrefs=True, alpha)', 'counts as confidence', 'Model.', 'green'),
    ('Evaluate with ranking metrics', 'precision@k', 'Measure.', 'amber'), ('A/B test', 'click-through', 'Prove.', 'green'),
    ('Combine with popularity', 'cold start', 'Blend.', 'blue')], ['Clicks.', 'Implicit.', 'Rank.', 'Test.', 'Blend.'], 'scenario-implicit')
assemble(HERE, h2_story='Finding groups and tastes without labels', hook_html=hk,
    narration='TiffinGo’s marketing team wants customer types, the app team wants “you may also like”, and the menu team wants combo offers. None of the data is labelled.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Clustering and recommendations',
    formal='<b>Clustering</b> partitions unlabelled data into groups of similar points; <b>KMeans</b> minimises within-cluster squared distances to k centroids. <b>Collaborative filtering</b> with <b>Alternating Least Squares (ALS)</b> factorises a sparse user–item rating matrix into low-rank user and item factors to predict missing ratings. <b>FPGrowth</b> mines frequent itemsets from transactions and derives association rules measured by support, confidence and lift.',
    simple='KMeans puts similar customers together, ALS guesses what a person will like from people with similar taste, and FPGrowth finds items that are often bought together.',
    term_rows=[('Unsupervised', 'No labels.'), ('KMeans', 'k groups by distance.'), ('Silhouette', 'Cluster quality −1..1.'), ('ALS', 'Matrix factorisation.'), ('Rank', 'Size of factor vectors.'), ('Cold start', 'Unseen user/item.'), ('FPGrowth', 'Frequent itemsets.'), ('Lift', 'Strength of a rule.')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('KMeans works on raw columns.', 'Scale first; distance is unit-sensitive.', 'Step 1.'),
               ('ALS can score anyone.', 'Unknown users give NaN.', 'Step 3.'),
               ('High confidence means a real link.', 'Check lift.', 'Rule figure.')],
    exam='“Which MLlib algorithms are unsupervised/recommendation?” KMeans (+ silhouette, scaling), BisectingKMeans, GaussianMixture, LDA; ALS (rank, regParam, maxIter, coldStartStrategy, implicitPrefs); FPGrowth (minSupport, minConfidence, lift). pyspark.ml (DataFrame) over pyspark.mllib (RDD).',
    types_h2='Algorithms and questions', types_html=types_html, warn=warn,
    steps_h2='Segments, tastes and baskets', steps_intro='All outputs are real: PySpark 4.3.0 MLlib, local[2], synthetic TiffinGo data generated with a fixed seed.',
    steps=steps, two=two, peel_intro='Now peel ALS.', peel_html=pe,
    scen_intro='Three live scenarios: campaigns, NaN metrics, and click data.', scen=scen,
    uc_h2='Unsupervised ML at work', ucs=[uc_('seg', 'segments', 'blue', '1. Customer segments', 'KMeans on behaviour.', ['Customers', '*KMeans', 'Campaigns']),
        uc_('rec', 'recs', 'green', '2. Recommendations', 'ALS for “you may like”.', ['Ratings', '*ALS', 'Top-N']),
        uc_('bundle', 'bundles', 'amber', '3. Combos', 'FPGrowth rules.', ['Baskets', '*FPGrowth', 'Offers']),
        uc_('topic', 'topics', 'violet', '4. Review topics', 'LDA on text.', ['Reviews', '*LDA', 'Themes'])],
    uc_note='Examples are simplified descriptions of common practice.',
    pre='<b>Before you start:</b> <a href="../02-feature-engineering-and-classification/">10.2 Features</a>.')
