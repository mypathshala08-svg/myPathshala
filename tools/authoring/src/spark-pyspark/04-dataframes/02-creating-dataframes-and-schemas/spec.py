import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
BODY = body(HERE)

META = dict(
    module='04-dataframes', lesson='02-creating-dataframes-and-schemas', n='4.2',
    module_label='Module 4 · DataFrames',
    title='Creating DataFrames and schemas',
    desc='Every way to create a PySpark DataFrame and how to declare its schema, tested with PySpark 4.3.0: tuples, Rows, dicts (columns come out sorted), pandas, RDDs and range; inference that fails on [1, 2.5] but silently turns [1, "two"] into strings; DDL strings and StructType with DECIMAL and nullable checks; nested array, struct and map columns; schemas saved as JSON; and inferSchema on 2M CSV rows costing 2 jobs and 4.6 s versus 0 jobs with a declared schema.',
    og_desc='inferSchema cost 2 jobs and 4.6 s on 2M rows; a declared schema cost 0. And [1, "two"] silently became strings. Creating DataFrames and schemas, measured.',
    minutes=32, level='Beginner → Intermediate',
    lead='A DataFrame is only as good as its <b>schema</b>. This lesson creates DataFrames in every common way, shows where type inference breaks, and declares schemas with DDL strings and <code>StructType</code>, including nested types. <b>All outputs are real</b> (PySpark 4.3.0).',
    chips=['PySpark 4.3.0', 'Inference broken on purpose', '2M-row CSV timed', 'Runs in your browser (Python)'],
)

MAIN = '''# How inference merges the types of one column (a simplified model)
def spark_type(v):
    if v is None: return None
    if isinstance(v, bool): return "boolean"
    if isinstance(v, int): return "bigint"
    if isinstance(v, float): return "double"
    return "string"

def merge(values):
    types = {spark_type(v) for v in values} - {None}
    if not types:
        return "CANNOT_DETERMINE_TYPE"
    if types == {"bigint", "double"}:
        return "CANNOT_MERGE_TYPE"
    if "string" in types:
        return "string"            # silently: everything becomes text
    return types.pop()

for col in ([1, 2], [1, 2.5], [1, "two"], [None, None]):
    print(col, "->", merge(col))
'''
RUN = dict(
    heading='Run the code: how inference decides',
    intro='<p>A model of Step 2. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('        return "string"            # silently: everything becomes text', 'In our lab [1, "two"] became ["1", "two"] with no error.'),
        ('    if types == {"bigint", "double"}:', 'PySpark 4.3 refused to merge LongType and DoubleType.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Add <code>[True, 1]</code>: what would you expect?', code=None),
        dict(label='2 · Predict first: inference cost', hint='<b>Predict first:</b> jobs started by read() with inferSchema vs a declared schema (lab).',
             code='''for how, jobs, secs in (("inferSchema", 2, 4.6), ("declared", 0, 0.0)):
    print(f"{how:12} jobs={jobs} read() {secs} s")
'''),
        dict(label='3 · DDL from a dict', hint='Build a DDL string from column names and types.',
             code='''cols = {"order_id": "INT", "city": "STRING", "amount": "DECIMAL(10,2)"}
print(", ".join(f"{k} {v}" for k, v in cols.items()))
'''),
        dict(label='4 · Sorted dict keys', hint='Rows from dicts came out with sorted column names.',
             code='''row = {"id": 1, "dish": "Idli", "on": "2026-11-04"}
print(sorted(row))
'''),
        dict(label='5 · Spot the error', hint='This schema stores phone numbers as numbers.', expect='error',
             code='''schema = {"phone": "BIGINT", "pincode": "INT"}
assert all(t == "STRING" for t in schema.values()), "phone numbers and PIN codes are text: leading zeros and + signs matter"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: schemas',
    intro='<p>In the <code>pyspark</code> shell. <b>Outputs are real</b> (PySpark 4.3.0).</p>',
    items=[
        dict(title='1 · Python int', cmd='spark.createDataFrame([(1, "Idli")], ["id", "dish"]).dtypes', file='pyspark',
             output="[('id', 'bigint'), ('dish', 'string')]", note='Declare INT if you need 32-bit.'),
        dict(title='2 · A silent string', cmd='spark.createDataFrame([(1,), ("two",)], ["v"]).collect()', file='pyspark',
             output="[Row(v='1'), Row(v='two')]", note='No error, no warning.'),
        dict(title='3 · Schema as DDL', cmd='spark.createDataFrame([], "id INT, city STRING").schema.simpleString()', file='pyspark',
             output='struct<id:int,city:string>', note='printSchema() shows it as a tree.'),
    ],
)

TRACE = dict(
    heading='Verifying rows against a schema',
    intro='<p>Follow which rows a declared schema accepts.</p>',
    code='''schema = [("order_id", int, False), ("city", str, True)]
rows = [(1, "Pune"), (None, "Delhi"), ("x", "Pune")]
for r in rows:
    ok = all((v is None and nullable) or isinstance(v, typ)
             for v, (name, typ, nullable) in zip(r, schema))
    print(r, "accepted" if ok else "rejected")
''',
    notes={1: 'Schema :: order_id is NOT NULL.', 4: 'Check :: None only where nullable; otherwise the right type.', 6: 'Lab :: Both bad rows were rejected with FIELD_* errors.'},
)

WORKED_INTRO = 'Three schema tasks from real pipelines.'
EXAMPLES = [
    dict(level='b', tag='Schemas · basics', title='Declare a CSV schema',
         problem='<p>Read the orders export with fixed types.</p>',
         inp='orders.csv',
         approach=['Write a DDL string.', 'Pass it to read.schema().', 'Money as DECIMAL.'],
         code='''ddl = ("order_id INT, customer_id INT, restaurant_id INT, city STRING, "
       "order_ts TIMESTAMP, amount DECIMAL(10,2), payment STRING, status STRING")
print(f'spark.read.schema("{ddl[:40]}…").option("header", True).csv(path)')
''', notes={2: 'Money :: DECIMAL keeps paise exact.'},
         tryit='Step 6: 0 jobs at read time.'),
    dict(level='i', tag='Schemas · contracts', title='Store the schema as JSON',
         problem='<p>Share one schema between three jobs.</p>',
         inp='df.schema',
         approach=['schema.json() to a file in git.', 'StructType.fromJson() when reading.', 'Compare in tests.'],
         code='''import json
schema = {"type": "struct", "fields": [{"name": "order_id", "type": "integer", "nullable": True, "metadata": {}}]}
text = json.dumps(schema)
print(json.loads(text) == schema)
''', notes={3: 'Round trip :: The lab compared fromJson(json) == schema: True.'},
         tryit='Lesson 11.4 tests schemas with assertSchemaEqual.'),
    dict(level='a', tag='Schemas · nested', title='Model a restaurant record',
         problem='<p>Write a schema for restaurants.json.</p>',
         inp='id, tags list, contact object, price map',
         approach=['ArrayType for tags.', 'StructType for contact.', 'MapType for prices.'],
         code='''print("restaurant_id INT, tags ARRAY<STRING>, "
      "contact STRUCT<phone: STRING, email: STRING>, prices MAP<STRING, INT>")
''', notes={1: 'DDL :: The lab printed this exact DDL from the StructType.'},
         tryit='Lesson 6.5 works with complex data in depth.'),
]

QUIZ = mix([
    dict(q='Beginner: What Spark type does a Python int become?', options=['int', 'bigint', 'double', 'string'], answer=1,
         why='LongType.'),
    dict(q='Beginner: Which is a valid DDL schema?', options=['{"id": int}', '"id INT, city STRING"', 'id=int', 'INT id'], answer=1,
         why='SQL column definitions.'),
    dict(q='Beginner: Which type for money?', options=['double', 'float', 'DECIMAL(p,s)', 'string'], answer=2,
         why='Exact arithmetic.'),
    dict(q='Intermediate: createDataFrame([(1,), ("two",)]) gives…', options=['An error', 'A string column', 'A bigint column', 'Two columns'], answer=1,
         why='Silently converted.'),
    dict(q='Intermediate: Why did dict rows produce columns dish, id, on?', options=['Random', 'Keys were sorted', 'Alphabetical by value', 'Bug in pandas'], answer=1,
         why='Use tuples or Rows for order.'),
    dict(q='Intermediate: A column has only None values. What happens?', options=['string', 'null type', 'CANNOT_DETERMINE_TYPE', 'int'], answer=2,
         why='Provide a schema.'),
    dict(q='Advanced: Why is inferSchema slow on big CSVs?', options=['It compresses', 'It reads the data an extra time', 'It writes Parquet', 'It sorts'], answer=1,
         why='2 jobs, 4.6 s on 2M rows.'),
    dict(q='Advanced: How do you share one schema across jobs?', options=['Copy-paste code', 'schema.json() + StructType.fromJson()', 'inferSchema everywhere', 'pickle'], answer=1,
         why='A data contract in the repo.'),
])

REVISION = [
    '<code>createDataFrame</code> from tuples, Rows, dicts, pandas, RDDs; <code>spark.range</code>; files and SQL.',
    'Python int → <b>bigint</b>; dict keys → <b>sorted</b> columns.',
    'Inference: [1, 2.5] fails, [None] fails, <b>[1, "two"] silently becomes string</b>.',
    'Schemas: DDL string or <code>StructType</code>/<code>StructField</code> with nullable.',
    'Local data is verified: DECIMAL accepts only <code>Decimal</code>; NOT NULL rejects None.',
    'Nested: ArrayType, StructType, MapType; access with <code>[i]</code>, <code>.field</code>, <code>[key]</code>.',
    'inferSchema on 2M rows: 2 jobs, 4.6 s; declared schema: 0 jobs.',
]
FAQ = [
    ('Is DDL or StructType better?', 'Same result. DDL is shorter and readable; StructType lets you set metadata and build schemas in code. Many teams store schemas as JSON from StructType.'),
    ('Does JSON reading also infer?', 'Yes, JSON is always inferred unless you give a schema, and it also scans the data. Give a schema for large or changing JSON (Lesson 5.1).'),
    ('What does nullable=False do for files?', 'File sources mark columns nullable regardless; nulls are not rejected while reading. Validate nulls explicitly (Lesson 4.4).'),
    ('Can I change a column type later?', 'Yes: <code>withColumn("c", col("c").cast("int"))</code> or <code>try_cast</code> (Lesson 4.3). It is cheaper to read the right type.'),
    ('What is the VARIANT type?', 'Since Spark 4.0, VARIANT stores semi-structured JSON without a fixed schema; Lesson 6.5 covers it.'),
]

PRACTICE_INTRO = 'Programs about types, schemas and inference.'
PROBLEMS = [
    dict(level='easy', title='Count columns', stmt='Count columns in a DDL string.', inp='"order_id INT, city STRING, amount DECIMAL(10,2)"',
         code='''ddl = "order_id INT, city STRING, amount DECIMAL(10,2)"
print(len([c for c in ddl.split(", ")]))
''', explain='Careful: DECIMAL(10,2) contains a comma without a space.'),
    dict(level='easy', title='Python to Spark', stmt='Map Python types to Spark types.', inp='int, float, str, bool',
         code='''m = {int: "bigint", float: "double", str: "string", bool: "boolean"}
print([m[type(v)] for v in (5, 2.5, "Pune", True)])
''', explain='As in Step 1.'),
    dict(level='easy', title='Inference saving', stmt='Seconds saved per run with a schema.', inp='4.6 s vs 0.0 s, 24 runs a day',
         code='''print(round(4.6 * 24, 1), "s per day")
''', explain='On 200 GB files it is minutes per run.'),
    dict(level='medium', title='Validate rows', stmt='Count rows whose amount is not a valid number.', inp='strings from a CSV',
         code='''vals = ["450", "450.75", "abc", "", "380"]
def ok(v):
    try:
        float(v); return True
    except ValueError:
        return False
print(sum(not ok(v) for v in vals))
''', explain='try_cast in Spark gives null for these.'),
    dict(level='medium', title='Decimal vs float', stmt='Sum 0.1 ten times with float and Decimal.', inp='paise',
         code='''from decimal import Decimal
print(sum([0.1] * 10), sum([Decimal("0.1")] * 10))
''', explain='Why money uses DECIMAL.'),
    dict(level='medium', title='Leading zeros', stmt='What happens to a PIN read as a number?', inp='"011001"',
         code='''print(int("011001"), "vs", "011001")
''', explain='Store codes as STRING.'),
    dict(level='business', title='Wrong totals', stmt='Error in a day of float sums.', inp='1 lakh payments of ₹0.10',
         code='''print(sum([0.1] * 100000) - 10000)
''', explain='Small, but auditors notice.'),
    dict(level='business', title='Late dashboard', stmt='Hours lost when a nightly job fails at 2 a.m. and is fixed at noon.', inp='2 → 12',
         code='''print(12 - 2, "hours without a dashboard")
''', explain='A declared schema would have failed loudly or kept types stable.'),
]

SCN_INTRO = 'Schema questions test whether you have run Spark on real, messy data.'
SCENARIOS = (
    scn('Any company · PySpark', 'Fresher', '“How do you create a DataFrame?”',
        'Show three ways to create a DataFrame.',
        'do you know the API?',
        '<p><code>spark.createDataFrame(list_of_tuples, "id INT, city STRING")</code>, from a pandas DataFrame, and <code>spark.read.schema(s).csv(path)</code> for files; also <code>rdd.toDF()</code> and <code>spark.range()</code>. I prefer giving a schema rather than relying on inference.</p>', 'Only knowing how to read a CSV.') +
    scn('Data engineering', 'Mid-level', 'inferSchema in production?',
        'Should we use inferSchema for the hourly feed?',
        'do you know its cost and risk?',
        '''<ul>
          <li>It reads data an extra time (2 jobs, 4.6 s on 2M rows in my test).</li>
          <li>Types follow the data and can change between runs.</li>
          <li>Declare the schema (DDL or JSON in git); quarantine bad rows.</li>
        </ul>''', '“It is fine, Spark is fast.”') +
    scn('Data engineering', 'Mid-level', 'Strange types in tests',
        'Our tests pass but production writes fail with type mismatches.',
        'can you connect test data to schemas?',
        '''<ol>
          <li>Inferred test DataFrames use bigint and sorted dict columns.</li>
          <li>Build fixtures with the production schema.</li>
          <li>Assert schemas in tests.</li>
        </ol>''', 'Loosening production types to match tests.') +
    scn('Platform', 'Senior', 'Schema governance',
        'How would you manage schemas for 50 feeds?',
        'do you think in contracts?',
        '''<ul>
          <li>Schemas versioned in git or a registry, loaded by jobs.</li>
          <li>Columnar formats (Parquet/Delta) carry the schema; schema evolution rules per table.</li>
          <li>Checks for unexpected columns and types at ingestion; alert on drift.</li>
        </ul>''', 'Letting each job infer.')
)
