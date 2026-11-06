import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
C = 'l101_pipelines.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)

STG = [('Imputer', 'fill nulls', 'violet'), ('Indexer', 'text → index', 'violet'), ('OneHot', 'index → 0/1', 'violet'),
       ('Assembler', '→ vector', 'blue'), ('LogReg', 'learn', 'acc')]
def stages_row(y, fitted=False, hi=None):
    o = ''
    for k, (n, d, tone) in enumerate(STG):
        sub = ('model' if n != 'Assembler' else 'as is') if fitted else d
        o += opbox(8 + k * 70, y, n, sub, ('green' if n != 'Assembler' else 'blue') if fitted else ('acc' if hi == k else tone), 66, 34)
        if k:
            o += arrow(8 + k * 70 - 4, y + 17, 8 + k * 70, y + 17, 'ink3', 1)
    return o

# ---------------------------------------------------------------- story
sc_ = (t(180, 22, 'Pipeline.fit(train)', 8, 'ink2', mono=True) + stages_row(30) + arrow(180, 70, 180, 88, 'ink3', 1.1) +
       t(180, 84, 'PipelineModel.transform(new data)', 8, 'ink2', mono=True) + stages_row(92, fitted=True) +
       box(400, 12, 232, 132, 'card') + t(516, 30, 'Measured (200,000 customers)', 8.6, bold=True) +
       ''.join(t(412, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
           ('5 stages, fit in 6.2 s', 'green'), ('15-feature vector', 'blue'),
           ('test AUC 0.8105', 'green'), ('Surat: keep → index 6', 'green'),
           ('Surat: error → Unseen label', 'red'), ('no Imputer → null error', 'red')])))
scene_svg = scene('An ML pipeline chains data preparation steps and a model into one object. We trained a five-stage churn pipeline on 160,000 TiffinGo customers, scored 40,000 more, and tested what happens with an unseen city and with missing values.', sc_,
                  'Fit the whole pipeline once; <tspan font-weight="700" class="s-acc">score with the same object</tspan> everywhere.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“The model works in my notebook”</h2>
  <div class="story">
    <p class="narration">A TiffinGo analyst built a churn model in pandas on a 50,000-row sample. In production, the scoring job had to repeat every preparation step by hand on 2 million customers: encode cities, fill missing values, scale numbers. One step was done in a different order, and the predictions were silently wrong for a month.</p>

{scene_svg}

K> Sir, Spark has machine learning too? Like scikit-learn?
A> <b>MLlib</b> trains models on data spread across the cluster, with the same DataFrames we already use. And like scikit-learn, it has <b>pipelines</b>: every preparation step and the model are fitted together and saved as one object.
R> So the scoring job cannot get the steps wrong?
A> Exactly. It loads the fitted pipeline and calls <code>transform</code>. Today we build a churn pipeline on 200,000 customers, look at what each stage does, and break it twice on purpose. All outputs are real (PySpark 4.3.0).
  </div>
</section>
'''

lv = '''
LEVELS> Pipelines at three levels
L1> A recipe card
      <ul>
        <li>Wash, chop, marinate, cook: always in that order. Writing it on one card means any cook makes the same dish.</li>
        <li>Some steps first need to measure the ingredients (how much salt for this batch): that is <code>fit</code>. Following the measured card is <code>transform</code>.</li>
      </ul>
L2> The API
      <ul>
        <li><b>Transformer</b>: <code>transform(df)</code> adds columns (VectorAssembler, a fitted model).</li>
        <li><b>Estimator</b>: <code>fit(df)</code> learns from data and returns a Transformer (StringIndexer → StringIndexerModel, LogisticRegression → LogisticRegressionModel).</li>
        <li><code>Pipeline(stages=[…]).fit(train)</code> → <code>PipelineModel</code>; <code>.transform(test)</code> adds <code>rawPrediction</code>, <code>probability</code>, <code>prediction</code>.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>StringIndexer learned labels by frequency: Free 0, Silver 1, Gold 2.</li>
        <li>5 stages fitted in 6.2 s on 159,838 rows; test AUC 0.8105 on 40,162 rows.</li>
        <li>An unseen city broke scoring unless <code>handleInvalid="keep"</code>; nulls broke VectorAssembler unless imputed.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>ML Pipelines</h2>
''' + def_block(
    '<b>MLlib</b> is Spark’s machine-learning library; its DataFrame-based API (<code>pyspark.ml</code>) is organised around <b>pipelines</b>. A <b>Transformer</b> converts one DataFrame into another, typically by appending columns, through <code>transform()</code>. An <b>Estimator</b> learns parameters from a DataFrame through <code>fit()</code> and returns a Transformer (a model). A <b>Pipeline</b> is an Estimator made of an ordered list of stages; <code>Pipeline.fit()</code> runs the stages in order on the training data, fitting each Estimator and transforming the data for the next stage, and returns a <b>PipelineModel</b> containing only Transformers. Applying the same PipelineModel at training, evaluation and serving time guarantees identical feature preparation. Models expect features as a single <b>vector column</b>, usually built with <code>VectorAssembler</code>.',
    'A pipeline is a list of steps: preparation steps and a model. Steps that must learn something from data (like the list of cities) are estimators; <code>fit</code> learns it. The result is a fitted pipeline you apply to any new data with <code>transform</code>, so the same preparation is always used.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Transformer', 'transform(df) → df with new columns.'),
    ('Estimator', 'fit(df) → a Transformer (model).'),
    ('Pipeline', 'Ordered stages; an Estimator.'),
    ('PipelineModel', 'Fitted pipeline; a Transformer.'),
    ('Feature vector', 'All inputs in one vector column.'),
    ('StringIndexer', 'Category → number by frequency.'),
    ('OneHotEncoder', 'Index → sparse 0/1 vector.'),
    ('handleInvalid', 'error / skip / keep for bad values.'),
]) + '''

  <h3>The five stages of our churn pipeline</h3>
''' + table(['Stage', 'Type', 'Learns in fit()', 'Adds'], [
    ['Imputer (median)', 'Estimator', 'median of avg_amount, late_pct', 'filled columns'],
    ['StringIndexer', 'Estimator', 'label order per column', 'city_idx, plan_idx'],
    ['OneHotEncoder', 'Estimator', 'number of categories', 'city_oh, plan_oh'],
    ['VectorAssembler', 'Transformer', 'nothing', 'features (15 values)'],
    ['LogisticRegression', 'Estimator', 'coefficients', 'rawPrediction, probability, prediction'],
], minw=620) + lv + '''
EXAM> “Transformer vs Estimator in Spark ML?” A Transformer has <code>transform()</code> and maps a DataFrame to a new one (e.g. VectorAssembler, a fitted model). An Estimator has <code>fit()</code> and learns from data, returning a Transformer (e.g. StringIndexer → StringIndexerModel). A Pipeline is an Estimator of stages; its fitted form, PipelineModel, is a Transformer used to score new data with the same preprocessing.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Common stages</h2>
''' + table(['Need', 'Stage', 'Kind'], [
    ['Missing numbers', '<code>Imputer</code>', 'Estimator'],
    ['Categories → numbers', '<code>StringIndexer</code> (+ <code>OneHotEncoder</code>)', 'Estimators'],
    ['Many columns → one vector', '<code>VectorAssembler</code>', 'Transformer'],
    ['Scale numbers', '<code>StandardScaler</code>, <code>MinMaxScaler</code>', 'Estimators'],
    ['Text', '<code>Tokenizer</code>, <code>HashingTF</code>, <code>IDF</code>', 'Mixed'],
    ['SQL-style feature', '<code>SQLTransformer</code>', 'Transformer'],
    ['Model', '<code>LogisticRegression</code>, <code>RandomForestClassifier</code>, …', 'Estimators'],
], minw=560) + '''
WARN> Fit the pipeline on the <b>training</b> split only. If you fit an Imputer, scaler or indexer on all data before splitting, test-set information leaks into the model and your evaluation looks better than reality. And set <code>handleInvalid</code> deliberately: in production new categories (a new city) and nulls always appear; the default <code>"error"</code> stops the whole scoring job.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>A churn pipeline, stage by stage</h2>
  <p>All outputs are real: PySpark 4.3.0, <code>local[4]</code>. Data: 200,000 synthetic TiffinGo customers with city, plan, orders in the last 30 days, average amount, days since last order, complaints, late-delivery %, tenure and a <code>churned</code> label (37.2% churn); 3% of amounts and 2% of late % are missing.</p>
''' + stepper([
    ('Step 1 · Data and the split',
     code('python', 'l101_pipelines.py', 'df = spark.read.parquet("customers.parquet")\ntrain, test = df.randomSplit([0.8, 0.2], seed=7)', sec('== 1)', '== 2)')),
     'A random 80/20 split with a fixed seed so results repeat. Everything that learns from data must see only <code>train</code>; <code>test</code> stays untouched until evaluation.'),
    ('Step 2 · An Estimator and a Transformer',
     code('python', 'l101_pipelines.py', 'idx = StringIndexer(inputCol="plan", outputCol="plan_idx")\nidx_model = idx.fit(train)                    # learns the labels\nidx_model.transform(train)\nva = VectorAssembler(inputCols=["orders_30d", "days_since_last"], outputCol="v")\nva.transform(train)                           # nothing to learn', sec('== 2)', '== 3)')),
     '<code>StringIndexer</code> must first <b>learn</b> the categories, ordered by frequency: Free (most common) 0, Silver 1, Gold 2. <code>fit</code> returns a <code>StringIndexerModel</code> that does the mapping. <code>VectorAssembler</code> has no <code>fit</code>: it just packs columns into the single <b>vector</b> column that every MLlib model reads.'),
    ('Step 3 · The full pipeline',
     code('python', 'l101_pipelines.py', 'pipe = Pipeline(stages=[\n    Imputer(inputCols=["avg_amount", "late_pct"], outputCols=[…], strategy="median"),\n    StringIndexer(inputCols=["city", "plan"], outputCols=["city_idx", "plan_idx"], handleInvalid="keep"),\n    OneHotEncoder(inputCols=["city_idx", "plan_idx"], outputCols=["city_oh", "plan_oh"]),\n    VectorAssembler(inputCols=num + ["city_oh", "plan_oh"], outputCol="features"),\n    LogisticRegression(featuresCol="features", labelCol="churned", maxIter=50)])\nmodel = pipe.fit(train); pred = model.transform(test)', sec('== 3)', '== 4)')),
     'One <code>fit</code> fitted all four estimators in order (6.2 s on 160K rows across 4 cores) and returned a <code>PipelineModel</code> whose stages are now all models. <code>transform</code> added the intermediate columns and three outputs: <code>rawPrediction</code> (scores), <code>probability</code> ([P(stay), P(churn)]) and <code>prediction</code> (1 if P(churn) ≥ 0.5). 6 numbers + 6 city slots + 3 plan slots = 15 features. AUC on unseen customers: <b>0.81</b>.'),
    ('Step 4 · A city the model has never seen',
     code('python', 'l101_pipelines.py', 'new = spark.createDataFrame([(999001, "Surat", "Gold", 3, 250.0, 40, 2, 30.0, 5, 0)], df.schema)\nmodel.transform(new)                                  # handleInvalid="keep"\nPipeline(stages=[StringIndexer(inputCol="city", outputCol="city_idx")]).fit(train).transform(new)', sec('== 4)', '== 5)')),
     'TiffinGo launched in Surat after training. With <code>handleInvalid="keep"</code>, unknown cities get an extra index (6) and the customer is still scored. With the default <code>"error"</code>, the whole scoring job fails on the first unseen label. <code>"skip"</code> would silently drop the row.'),
    ('Step 5 · Missing values',
     code('python', 'l101_pipelines.py', 'Pipeline(stages=stages[1:]).fit(train)     # same pipeline without the Imputer', sec('== 5)')),
     'Without the Imputer, <code>VectorAssembler</code> hit the first null <code>avg_amount</code> and failed: models cannot take null features. Fill them (Imputer), drop them, or set <code>handleInvalid</code> on the assembler; deciding which is part of the model design, so it belongs <b>inside</b> the pipeline.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('StringIndexer is an Estimator', W), ('fit() -> StringIndexerModel', G), ("labels: ['Free', 'Silver', 'Gold']", G)], size=7.2),
    term([('fit: 6.2 s -> PipelineModel', G), ('ImputerModel, StringIndexerModel,', W), ('OneHotEncoderModel, VectorAssembler,', W), ('LogisticRegressionModel', W)], size=7.0),
    term([('probability [0.351, 0.649] -> 1.0', W), ('probability [0.794, 0.206] -> 0.0', W), ('test AUC: 0.8105', G)], size=7.2),
    term([('keep : Surat -> city_idx 6.0', G), ('error: Unseen label: Surat', RD), ('no Imputer: Encountered null', RD)], size=7.2),
]
B1 = [
    t(180, 14, 'Estimator → fit → Transformer', 9.4, bold=True) + flow([('StringIndexer', 'estimator', 'violet'), ('fit(train)', 'count labels', 'blue'), ('…Model', 'transformer', 'green')], y=50, w=96, gap=16) + cap('Learns from training data only.', '', 'green', y=144, h=30),
    t(180, 14, 'Pipeline.fit runs stages in order', 9.4, bold=True) + stages_row(50, hi=None) + cap('Each stage feeds the next.', '', 'blue', y=144, h=30),
    t(180, 14, 'PipelineModel.transform', 9.4, bold=True) + stages_row(50, fitted=True) + cap('Same steps for every new row.', '', 'green', y=144, h=30),
    t(180, 14, 'Real data is messy', 9.4, bold=True) + opbox(20, 46, 'new city', 'handleInvalid', 'amber', 150, 34) + opbox(190, 46, 'null value', 'Imputer', 'amber', 150, 34) + cap('Decide inside the pipeline.', '', 'amber', y=144, h=30),
]
see_caps = ['Estimator vs transformer.', 'Fitted pipeline.', 'Predictions.', 'Messy inputs.']
behind_caps = ['fit() learns parameters.', 'Stages in order.', 'One object to score.', 'handleInvalid and nulls.']
two = anim_two('ML Pipelines', 'From raw rows to predictions', 'Real lab outputs', 'What Spark does', see, B1, see_caps, behind_caps)

e1 = (t(180, 22, 'Notebook model, pandas', 9.4, bold=True) + t(180, 56, 'prep steps copied into a job', 8.4, 'ink2') + cap('Two versions of the truth.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'One step in a different order', 9.4, bold=True) + t(180, 56, 'predictions wrong for a month', 8.4, 'ink2') + cap('No error raised.', '', 'red', y=150, h=34))
e3 = (t(180, 22, 'Rebuild as a Pipeline', 9.4, bold=True) + t(180, 56, 'prep + model in stages', 8.4, 'ink2') + cap('Fit once.', '', 'green', y=150, h=34))
e4 = (t(180, 22, 'Save the PipelineModel', 9.4, bold=True) + t(180, 56, 'scoring job only loads it', 8.4, 'ink2') + cap('Lesson 10.3.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Train = serve', 9.4, 'acc', bold=True) + t(180, 56, 'same code path everywhere', 8.4, 'ink2') + cap('Skew removed.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Training-serving skew',
              'Why pipelines exist. (Typical.)',
              'Training-serving skew', 'Packing preparation and model in one PipelineModel removes training-serving skew', [e1, e2, e3, e4, e5],
              ['Notebook.', 'Wrong order.', 'Pipeline.', 'Save.', 'Same path.'],
              hid='scenario-skew')
b1 = (t(180, 22, 'New city launched', 9.4, bold=True) + t(180, 56, 'Surat customers appear', 8.4, 'ink2') + cap('Model trained before.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'Nightly scoring fails', 9.4, bold=True) + t(180, 56, 'Unseen label: Surat', 8.4, 'red', mono=True) + cap('No churn list today.', '', 'red', y=150, h=34))
b3 = (t(180, 22, 'handleInvalid="keep"', 9.4, bold=True) + t(180, 56, 'extra bucket for unknowns', 8.4, 'ink2') + cap('Index 6 in our lab.', '', 'green', y=150, h=34))
b4 = (t(180, 22, 'Monitor the unknown share', 9.4, bold=True) + t(180, 56, '% rows in the “other” bucket', 8.4, 'ink2') + cap('Retrain when it grows.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Scoring never stops', 9.4, 'acc', bold=True) + t(180, 56, 'new values degrade gracefully', 8.4, 'ink2') + cap('Robust.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'The city that broke scoring',
              'Unseen categories. (Typical; error from our lab.)',
              'Unseen labels', 'Set handleInvalid so new categories do not stop scoring jobs', [b1, b2, b3, b4, b5],
              ['New city.', 'Failure.', 'keep.', 'Monitor.', 'Robust.'],
              hid='scenario-unseen')
u1 = (t(180, 22, 'AUC 0.93 in testing', 9.4, bold=True) + t(180, 56, '0.80 in production', 8.4, 'ink2') + cap('Too good to be true.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'Scaler fitted on all data', 9.4, bold=True) + t(180, 56, 'then split train/test', 8.4, 'ink2') + cap('Leakage.', '', 'red', y=150, h=34))
u3 = (t(180, 22, 'Split first', 9.4, bold=True) + t(180, 56, 'randomSplit([0.8, 0.2], seed)', 8.4, 'ink', mono=True) + cap('Then fit the pipeline.', '', 'green', y=150, h=34))
u4 = (t(180, 22, 'Or split by time', 9.4, bold=True) + t(180, 56, 'train on Jan–Sep, test on Oct', 8.4, 'ink2') + cap('Closer to reality.', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'Honest metrics', 9.4, 'acc', bold=True) + t(180, 56, 'test numbers match production', 8.4, 'ink2') + cap('Trust restored.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'The model that looked too good',
              'Data leakage through preprocessing. (Typical.)',
              'Leakage', 'Fitting preprocessing on all data leaks test information; split first, then fit the pipeline', [u1, u2, u3, u4, u5],
              ['Too good.', 'Leak.', 'Split first.', 'By time.', 'Honest.'],
              hid='scenario-leak')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>From raw rows to predictions</h2>
  <p>Left: real outputs. Right: what fit and transform do.</p>
''' + two + '''
  <p>Three live scenarios follow: training-serving skew, an unseen city, and leakage.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Pipelines at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'churn', 12, 'blue', bold=True) + t(60, 58, 'scoring', 7.4, 'ink2'),
    '1. Churn scoring',
    'Millions of customers scored nightly with one saved PipelineModel.',
    ['Customers', '*PipelineModel', 'Risk list']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'fraud', 12, 'green', bold=True) + t(60, 58, 'features', 7.4, 'ink2'),
    '2. Fraud features',
    'Payment features and a classifier trained on months of transactions.',
    ['Payments', '*pipeline', 'Fraud score']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'ETA', 12, 'violet', bold=True) + t(60, 58, 'delivery', 7.4, 'ink2'),
    '3. Delivery time',
    'Regression pipelines predict delivery minutes from distance, zone and time.',
    ['Orders', '*GBTRegressor', 'ETA']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'text', 12, 'acc', bold=True) + t(60, 58, 'reviews', 7.4, 'ink2'),
    '4. Review classification',
    'Tokenizer, HashingTF and IDF stages feed a classifier for complaint reviews.',
    ['Reviews', '*text stages', 'Category']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'stream', 11, 'acc', bold=True) + t(60, 58, 'scoring', 7.4, 'ink2'),
    '5. Streaming scoring',
    'A fitted PipelineModel transforms a streaming DataFrame for live risk scores.',
    ['Kafka', '*model.transform', 'Live scores']) + '''
  <p class="muted">Examples are simplified; the customer data is synthetic.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> DataFrames and columns in <a href="../../04-dataframes/03-working-with-columns/">4.3</a>, nulls in <a href="../../04-dataframes/04-nulls-and-duplicates/">4.4</a>; basic ML ideas (features, labels, train/test) help.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
