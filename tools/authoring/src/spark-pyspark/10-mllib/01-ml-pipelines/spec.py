import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
BODY = body(HERE)

META = dict(
    module='10-mllib', lesson='01-ml-pipelines', n='10.1',
    module_label='Module 10 · MLlib',
    title='ML Pipelines',
    desc='Spark MLlib pipelines with PySpark 4.3.0 on 200,000 customers: Transformers vs Estimators, StringIndexer learning Free/Silver/Gold, VectorAssembler, a five-stage churn Pipeline (Imputer, StringIndexer, OneHotEncoder, VectorAssembler, LogisticRegression) fitted in 6.2 s with test AUC 0.81, the rawPrediction/probability/prediction columns, an unseen city with handleInvalid keep vs error, and the null error without an Imputer.',
    og_desc='Build a five-stage Spark ML churn pipeline, score unseen customers, and see what breaks with a new city or missing values.',
    minutes=28, level='Beginner → Intermediate',
    lead='MLlib trains models on distributed DataFrames, and <b>pipelines</b> keep preparation and model together. This lesson separates Transformers from Estimators, builds a five-stage churn pipeline on 200,000 customers, reads its predictions, and breaks it with an unseen city and missing values. <b>All outputs are real</b> (PySpark 4.3.0).',
    chips=['PySpark 4.3.0', '200,000 customers', 'Pipeline + PipelineModel', 'Runs in your browser (Python)'],
)

MAIN = '''# fit() vs transform() for a StringIndexer, in plain Python
from collections import Counter
train_plans = ["Free", "Free", "Silver", "Free", "Gold", "Silver", "Free"]

# fit: learn labels ordered by frequency
labels = [p for p, _ in Counter(train_plans).most_common()]
print("learned labels:", labels)

# transform: map values with the learned labels
def transform(values, handle_invalid="keep"):
    out = []
    for v in values:
        if v in labels:
            out.append(float(labels.index(v)))
        elif handle_invalid == "keep":
            out.append(float(len(labels)))       # extra index for unknowns
        else:
            raise ValueError(f"Unseen label: {v}")
    return out

print(transform(["Gold", "Free", "Platinum"]))
'''
RUN = dict(
    heading='Run the code: fit and transform',
    intro='<p>What a StringIndexer does in <code>fit</code> and <code>transform</code>. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('labels = [p for p, _ in Counter(train_plans).most_common()]', 'fit: learn from training data only. Most frequent value gets index 0.'),
        ('            out.append(float(len(labels)))       # extra index for unknowns', 'handleInvalid="keep": unseen values get one extra index instead of failing.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Then call <code>transform(["Platinum"], "error")</code>.', code=None),
        dict(label='2 · Predict first: one-hot size', hint='<b>Predict first:</b> 6 cities with keep (+1) and dropLast.',
             code='''cities, keep_extra, drop_last = 6, 1, 1
print(cities + keep_extra - drop_last, "slots per city vector")
'''),
        dict(label='3 · Feature count', hint='Total features in the lab vector.',
             code='''numeric, city_slots, plan_slots = 6, 6, 3
print(numeric + city_slots + plan_slots)
'''),
        dict(label='4 · Median imputer', hint='Fill missing values with the training median.',
             code='''import statistics
vals = [120.0, None, 300.0, 250.0, None, 90.0]
med = statistics.median(v for v in vals if v is not None)
print([v if v is not None else med for v in vals])
'''),
        dict(label='5 · Spot the error', hint='A null reaches VectorAssembler.', expect='error',
             code='''row = {"orders_30d": 5, "avg_amount": None}
assert None not in row.values(), "Encountered null while assembling a row with handleInvalid = error"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: a pipeline',
    intro='<p>In the <code>pyspark</code> shell with the lab data. <b>Outputs are real</b> (PySpark 4.3.0).</p>',
    items=[
        dict(title='1 · Learned labels', cmd='StringIndexer(inputCol="plan", outputCol="plan_idx").fit(train).labels', file='pyspark',
             output="['Free', 'Silver', 'Gold']", note='By frequency.'),
        dict(title='2 · Fitted stages', cmd='[type(s).__name__ for s in model.stages]', file='pyspark',
             output="['ImputerModel', 'StringIndexerModel', 'OneHotEncoderModel', 'VectorAssembler', 'LogisticRegressionModel']", note='All transformers now.'),
        dict(title='3 · Evaluate', cmd='BinaryClassificationEvaluator(labelCol="churned").evaluate(model.transform(test))', file='pyspark',
             output='0.8105…', note='AUC on 40,162 customers.'),
    ],
)

TRACE = dict(
    heading='How Pipeline.fit walks the stages',
    intro='<p>Each estimator is fitted, then its output feeds the next stage.</p>',
    code='''stages = ["Imputer", "StringIndexer", "VectorAssembler", "LogReg"]
estimators = {"Imputer", "StringIndexer", "LogReg"}
fitted = []
for s in stages:
    if s in estimators:
        fitted.append(s + "Model")
    else:
        fitted.append(s)
print(fitted)
''',
    notes={5: 'Estimator :: fit() on the data so far.', 8: 'Transformer :: Used as is.'},
)

WORKED_INTRO = 'Three pipeline design decisions at TiffinGo.'
EXAMPLES = [
    dict(level='b', tag='Pipelines · basics', title='Order the stages',
         problem='<p>Put Imputer, VectorAssembler, StringIndexer, LogisticRegression, OneHotEncoder in order.</p>',
         inp='five stages',
         approach=['Fill and encode before assembling.', 'Indexer before encoder.', 'Model last.'],
         code='''print(["Imputer", "StringIndexer", "OneHotEncoder", "VectorAssembler", "LogisticRegression"])
''', notes={1: 'Rule :: Assembler needs every input column ready.'},
         tryit='Step 3.'),
    dict(level='i', tag='Pipelines · robustness', title='Choose handleInvalid',
         problem='<p>New cities appear monthly; scoring must not fail.</p>',
         inp='production scoring',
         approach=['error stops the job.', 'skip drops customers silently.', 'keep adds an unknown bucket.'],
         code='''options = {"error": "job fails", "skip": "rows vanish", "keep": "scored as unknown"}
print("choose keep ->", options["keep"])
''', notes={1: 'Monitor :: Track how many rows hit the unknown bucket.'},
         tryit='Step 4.'),
    dict(level='a', tag='Pipelines · leakage', title='Where does fit happen?',
         problem='<p>A teammate scales all data, then splits.</p>',
         inp='StandardScaler before randomSplit',
         approach=['Scaler mean/std include test rows.', 'Test metrics are optimistic.', 'Split first; scaler inside the pipeline.'],
         code='''steps_bad = ["scale(all)", "split", "fit model"]
steps_ok = ["split", "pipeline.fit(train)", "evaluate(test)"]
print(steps_ok)
''', notes={2: 'Leakage :: Any fit on test data counts.'},
         tryit='Scenario 3.'),
]

QUIZ = mix([
    dict(q='Beginner: Which has fit()?', options=['Transformer', 'Estimator', 'DataFrame', 'Row'], answer=1,
         why='Returns a Transformer.'),
    dict(q='Beginner: VectorAssembler is…', options=['An estimator', 'A transformer', 'A model', 'An evaluator'], answer=1,
         why='Nothing to learn.'),
    dict(q='Beginner: Pipeline.fit() returns…', options=['Pipeline', 'PipelineModel', 'DataFrame', 'Vector'], answer=1,
         why='All stages fitted.'),
    dict(q='Intermediate: StringIndexer orders labels by…', options=['Alphabet', 'Frequency (most frequent = 0)', 'Random', 'Insertion'], answer=1,
         why='Free 0, Silver 1, Gold 2.'),
    dict(q='Intermediate: Output columns of a classifier?', options=['score only', 'rawPrediction, probability, prediction', 'label', 'features'], answer=1,
         why='Probability is [P(0), P(1)].'),
    dict(q='Intermediate: Unseen city with default handleInvalid?', options=['Index 0', 'Job fails: Unseen label', 'Row skipped', 'null'], answer=1,
         why='Use keep.'),
    dict(q='Advanced: Null in VectorAssembler input?', options=['Treated as 0', 'Error unless imputed/handled', 'Ignored', 'Becomes NaN silently'], answer=1,
         why='Encountered null.'),
    dict(q='Advanced: Why fit the pipeline on train only?', options=['Speed', 'Avoid leakage into evaluation', 'Required by API', 'Memory'], answer=1,
         why='Honest metrics.'),
])

REVISION = [
    'Transformer: transform(); Estimator: fit() → Transformer.',
    'Pipeline = ordered stages; fit → PipelineModel; transform scores new data.',
    'Models read one vector column (VectorAssembler).',
    'StringIndexer by frequency; OneHotEncoder to sparse 0/1.',
    'Lab: 5 stages, 6.2 s, 15 features, test AUC 0.8105.',
    'handleInvalid="keep" for unseen categories; impute nulls.',
    'Split first, fit on train: no leakage.',
]
FAQ = [
    ('Is pyspark.mllib the same as pyspark.ml?', 'No. pyspark.mllib is the old RDD-based API in maintenance mode; use the DataFrame-based pyspark.ml.'),
    ('Can I use scikit-learn models in Spark?', 'For scoring, yes via pandas UDFs; for training on huge data, use MLlib or distributed frameworks.'),
    ('Do I always need OneHotEncoder?', 'Linear models need it; tree models can use StringIndexer output directly.'),
    ('Can a stage be my own code?', 'Yes, SQLTransformer for SQL, or a custom Python Transformer class (harder to save).'),
    ('How big can training data be?', 'As big as the cluster can process; most MLlib algorithms are iterative and benefit from caching.'),
]

PRACTICE_INTRO = 'Programs about pipeline mechanics.'
PROBLEMS = [
    dict(level='easy', title='Split sizes', stmt='Rows in an 80/20 split of 200,000.', inp='200000',
         code='''print(int(200000 * 0.8), int(200000 * 0.2))
''', explain='Lab got 159,838 / 40,162 (random).'),
    dict(level='easy', title='Label order', stmt='Index by frequency.', inp='plan counts',
         code='''c = {"Free": 120000, "Silver": 60000, "Gold": 20000}
print(sorted(c, key=c.get, reverse=True))
''', explain='Free 0.'),
    dict(level='easy', title='Prediction', stmt='Prediction for P(churn) = 0.649.', inp='0.649',
         code='''print(1.0 if 0.649 >= 0.5 else 0.0)
''', explain='Default threshold 0.5.'),
    dict(level='medium', title='One-hot', stmt='One-hot vector for index 2 of 4 (dropLast).', inp='2, 4',
         code='''print([1.0 if i == 2 else 0.0 for i in range(4 - 1)])
''', explain='Last category = all zeros.'),
    dict(level='medium', title='Assemble', stmt='Assemble columns into a vector.', inp='row',
         code='''row = {"orders_30d": 9, "days_since_last": 18}
print([float(row[c]) for c in ["orders_30d", "days_since_last"]])
''', explain='[9.0, 18.0], as in the lab.'),
    dict(level='medium', title='Sigmoid', stmt='Probability from rawPrediction 0.6126.', inp='0.6126',
         code='''import math
print(round(1 / (1 + math.exp(-0.6126)), 4))
''', explain='0.6485, as in the lab.'),
    dict(level='business', title='Scoring scale', stmt='Customers per second scored if 2M take 7 s.', inp='2M, 7 s',
         code='''print(int(2_000_000 / 7))
''', explain='Batch scoring is cheap.'),
    dict(level='business', title='Retention budget', stmt='Coupons for top 10% risk of 2M at ₹40.', inp='10%, 2M, 40',
         code='''print("₹", int(2_000_000 * 0.10 * 40))
''', explain='Lesson 10.3 picks the threshold.'),
]

SCN_INTRO = 'Pipeline basics are asked in every Spark ML interview.'
SCENARIOS = (
    scn('Any company · Spark', 'Fresher', '“Transformer vs Estimator”',
        'Explain with examples.',
        'fit vs transform?',
        '<p>An Estimator learns from data with <code>fit()</code> and returns a Transformer (StringIndexer → StringIndexerModel, LogisticRegression → LogisticRegressionModel). A Transformer maps a DataFrame with <code>transform()</code> (VectorAssembler, any fitted model).</p>', 'Saying VectorAssembler must be fitted.') +
    scn('Data science', 'Mid-level', 'Why pipelines?',
        'Your team scores models with hand-written prep code.',
        'risk and fix?',
        '''<ul>
          <li>Training-serving skew: prep differs between training and scoring.</li>
          <li>Pipeline with all prep stages + model, fitted once.</li>
          <li>Save and load the PipelineModel for scoring.</li>
        </ul>''', 'Copying notebook code into the job.') +
    scn('Data engineering', 'Mid-level', 'Scoring job failure',
        'The nightly scoring job fails after a new city launch.',
        'fix?',
        '''<ol>
          <li>Error: Unseen label from StringIndexer.</li>
          <li>Retrain with handleInvalid="keep".</li>
          <li>Monitor unknown-category rate; retrain regularly.</li>
        </ol>''', 'Filtering out the new city.') +
    scn('ML platform', 'Senior', 'Pipeline standards',
        'Define standards for production Spark ML pipelines.',
        'checklist?',
        '''<ul>
          <li>All preprocessing inside the pipeline; split before fit.</li>
          <li>Explicit handleInvalid and null handling.</li>
          <li>Versioned saved models with metrics.</li>
        </ul>''', 'Preprocessing in a separate untracked script.')
)
