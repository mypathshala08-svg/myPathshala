import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from svgkit import scn
BODY = body(HERE)
META = dict(module='11-spark-in-production', lesson='06-writing-clean-modular-pyspark', n='11.6', module_label='Module 11 · Spark in production',
    title='Writing clean, modular PySpark',
    desc='How to structure PySpark code for production: small DataFrame-to-DataFrame functions, DataFrame.transform chains, configuration passed in, I/O at the edges and tests per function, plus plan-aware habits: select or withColumns instead of looped withColumn, toDF for renames, early filters and isEmpty instead of count. Real PySpark 4.3 measurements and pytest results.',
    og_desc='21 Project nodes vs 2, isEmpty vs count, and a tested transform chain: clean PySpark measured.',
    minutes=20, level='Intermediate',
    lead='How should production PySpark look? We refactor a job into a <b>transform chain</b>, measure <b>plan-changing habits</b>, and <b>test</b> each function. <b>All outputs are real.</b>',
    chips=['df.transform(f)', '21 → 2 Project nodes', 'isEmpty 0.12 s', 'Runs in your browser (Python)'])
MAIN = '''# DataFrame -> DataFrame style, with plain Python lists of dicts
def only_valid(rows):
    return [r for r in rows if r["qty"] > 0 and r["item"]]

def add_amount(prices):
    def _f(rows):
        return [{**r, "amount": r["qty"] * prices.get(r["item"], 0)} for r in rows]
    return _f

def revenue_by_city(rows):
    out = {}
    for r in rows: out[r["city"]] = out.get(r["city"], 0) + r["amount"]
    return out

def pipe(data, *steps):              # like df.transform(f).transform(g)...
    for s in steps: data = s(data)
    return data

orders = [{"city": "Pune", "item": "idli", "qty": 2}, {"city": "Pune", "item": None, "qty": 1}, {"city": "Delhi", "item": "dosa", "qty": 1}]
print(pipe(orders, only_valid, add_amount({"idli": 45, "dosa": 90}), revenue_by_city))
'''
RUN = dict(heading='Run the code: a transform chain', intro='<p>The same shape as the lab, in plain Python. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('def add_amount(prices):', 'Settings come in as parameters.'), ('def pipe(data, *steps):              # like df.transform(f).transform(g)...', 'Compose small steps.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>. Add a step that keeps only Pune.', code=None),
        dict(label='2 · Predict first: nodes', hint='<b>Predict first:</b> withColumn × 20 → Project nodes?', code='print(20 + 1)\n'),
        dict(label='3 · Test', hint='Assert a step.', code='rows = [{"qty": 0, "item": "idli"}]\nassert [r for r in rows if r["qty"] > 0] == []\nprint("ok")\n'),
        dict(label='4 · Rename', hint='toDF-style names.', code='print([c.upper() for c in ["city", "item", "qty"]])\n'),
        dict(label='5 · Spot the error', hint='Hard-coded prod path in dev.', expect='error', code='env, path = "dev", "s3://prod/orders"\nif env == "dev" and "prod" in path:\n    raise RuntimeError("dev job pointing at production data: pass paths as config")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC', intro='<p>PySpark 4.x + pytest. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Run', cmd='python3 l116_clean.py', file='terminal', output='  withColumn x20 : 21 Project nodes', note='Lab script.'),
           dict(title='2 · Test', cmd='pytest -q clean/test_transforms.py', file='terminal', output='2 passed', note='Tiny DataFrames.')])
TRACE = dict(heading='A chain step by step', intro='<p>Each step returns new data.</p>',
    code='data = [1, 0, 3]\nfor step in (lambda d: [x for x in d if x > 0], lambda d: [x * 45 for x in d]):\n    data = step(data)\nprint(data)\n', notes={3: 'Next step :: Gets the output.'})
WORKED_INTRO = 'Three structure decisions.'
EXAMPLES = [
    dict(level='b', tag='Clean · function', title='Extract a step', problem='<p>A block filters bad orders.</p>', inp='code',
         approach=['def only_valid(df): return df.filter(...).', 'No I/O inside.', 'Name by meaning.'], code='print("def only_valid(df): return df.filter(...)")\n', notes={1: 'Pure.'}, tryit='Step 1.'),
    dict(level='i', tag='Clean · columns', title='Many derived columns', problem='<p>30 features.</p>', inp='pattern',
         approach=['Build a dict of expressions.', 'withColumns(dict).', 'Check explain.'], code='print("df.withColumns({name: expr for name, expr in features.items()})")\n', notes={1: 'Small plan.'}, tryit='Step 2.'),
    dict(level='a', tag='Clean · project', title='Package the job', problem='<p>Ship to a cluster.</p>', inp='layout',
         approach=['transforms.py, io.py, main.py, tests/.', 'Wheel or --py-files.', 'Config per environment.'], code='print(["transforms.py", "io.py", "main.py", "config.yaml", "tests/"])\n', notes={1: 'Lesson 11.1.'}, tryit='Peel.')]
QUIZ = mix([
    dict(q='Beginner: A clean transform function…', options=['Reads and writes files', 'Takes a DataFrame and returns a DataFrame', 'Prints counts', 'Uses globals'], answer=1, why='Pure.'),
    dict(q='Beginner: df.transform(f) calls…', options=['f(df)', 'df.f', 'Spark SQL', 'A UDF'], answer=0, why='Chaining.'),
    dict(q='Beginner: Settings like prices should be…', options=['Hard-coded', 'Passed in', 'In comments', 'Random'], answer=1, why='Reuse.'),
    dict(q='Intermediate: 20 withColumn gave…', options=['2 nodes', '21 Project nodes', '0', '200'], answer=1, why='Step 2.'),
    dict(q='Intermediate: Rename all columns with…', options=['20 withColumnRenamed', 'toDF(*names)', 'UDF', 'collect'], answer=1, why='One projection.'),
    dict(q='Intermediate: Faster “any rows?”', options=['count() > 0', 'isEmpty()', 'collect()', 'show()'], answer=1, why='Stops early.'),
    dict(q='Advanced: Logging count() after every step…', options=['Free', 'Runs a job each time', 'Caches', 'Speeds up'], answer=1, why='Warning.'),
    dict(q='Advanced: Does modular code change Catalyst plans?', options=['Always slower', 'Usually same plan', 'Always faster', 'Disables AQE'], answer=1, why='Myth.')])
REVISION = ['Small DataFrame → DataFrame functions; df.transform chains; config in; I/O at edges.', 'Lab: withColumn ×20 → 21 nodes/220 ms; select → 2/70 ms.',
    'toDF(*cols) for renames; isEmpty 0.12 s vs count 0.31 s.', 'pytest per function with tiny DataFrames: 2 passed.', 'Package: transforms, io, main, config, tests.']
FAQ = [('Is withColumn bad?', 'No for a few columns; avoid it in long loops.'),
    ('Where do UDFs go?', 'In the transforms module, with tests; prefer built-ins first.'),
    ('Should every step be a function?', 'Group by meaning, not by line; three to ten steps per job is typical.'),
    ('How do I test without a cluster?', 'local[1] SparkSession fixture (Lesson 11.4).')]
PRACTICE_INTRO = 'Clean code programs.'
PROBLEMS = [
    dict(level='easy', title='Filter fn', stmt='Keep qty > 0.', inp='list', code='def only_valid(xs): return [x for x in xs if x > 0]\nprint(only_valid([1, 0, 2]))\n', explain='[1, 2].'),
    dict(level='easy', title='Closure', stmt='Price function factory.', inp='dict', code='def amount(p):\n    return lambda item, q: q * p[item]\nprint(amount({"idli": 45})("idli", 2))\n', explain='90.'),
    dict(level='easy', title='Upper names', stmt='Rename list.', inp='list', code='print([c.upper() for c in ["a", "b"]])\n', explain='[A, B].'),
    dict(level='medium', title='Pipe', stmt='Compose steps.', inp='funcs', code='def pipe(x, *fs):\n    for f in fs: x = f(x)\n    return x\nprint(pipe(3, lambda v: v + 1, lambda v: v * 2))\n', explain='8.'),
    dict(level='medium', title='Exprs dict', stmt='Build 3 names.', inp='int', code='print({f"c{i}": f"qty + {i}" for i in range(3)})\n', explain='withColumns input.'),
    dict(level='medium', title='Any?', stmt='Short-circuit check.', inp='list', code='print(any(x == 0 for x in [3, 0, 5]))\n', explain='Like isEmpty.'),
    dict(level='business', title='Review time', stmt='Hours saved per change.', inp='ints', code='print(8 - 1, "hours")\n', explain='Readable code.'),
    dict(level='business', title='Driver time', stmt='220 → 70 ms × 1,000 jobs.', inp='ints', code='print((220 - 70) * 1000 / 1000, "s/day")\n', explain='150 s.')]
SCN_INTRO = 'Code-structure interview questions.'
SCENARIOS = (scn('Any company · data', 'Fresher', '“How do you organise PySpark code?”', 'Explain.', 'answer?', '<p>Small pure functions that take and return DataFrames, chained with transform; configuration passed in; reading and writing at the edges; unit tests per function with small DataFrames.</p>', '“One big notebook.”') +
    scn('Data', 'Mid-level', 'Slow driver', 'Big plan.', 'fix?', '<ul><li>Replace looped withColumn with select/withColumns.</li></ul>', 'More executors.') +
    scn('Data', 'Mid-level', 'Existence check', 'count() slow.', 'fix?', '<ul><li>isEmpty() / limit(1).</li></ul>', 'collect().') +
    scn('Platform', 'Senior', 'Team standards', 'Define.', 'what?', '<ul><li>Layout, transforms, tests, config, explain in review, lint rules.</li></ul>', 'No standards.'))
