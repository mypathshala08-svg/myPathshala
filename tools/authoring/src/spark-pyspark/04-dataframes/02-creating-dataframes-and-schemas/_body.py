import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
C = 'l42_create.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)

def schema_box(x, y, rows, title='schema', tone='card', w=150):
    """rows: [(name, type, tone_or_None)]"""
    h = 20 + len(rows) * 15
    o = box(x, y, w, h, tone) + t(x + w / 2, y + 13, title, 7.8, bold=True)
    for k, (n, ty, c) in enumerate(rows):
        yy = y + 28 + k * 15
        o += t(x + 8, yy, n, 7.0, 'ink', anchor='start', mono=True) + t(x + w - 8, yy, ty.replace('<', '&lt;').replace('>', '&gt;'), 7.0, c or 'ink2', anchor='end', mono=True)
    return o

# ---------------------------------------------------------------- story
sc_ = (schema_box(10, 18, [('order_id', 'int', None), ('city', 'string', None), ('amount', 'decimal(10,2)', 'green'), ('order_ts', 'timestamp', None)], 'declared schema', 'green', 180) +
       box(400, 12, 232, 132, 'card') + t(516, 30, 'Measured', 8.6, bold=True) +
       ''.join(t(412, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
           ('[1, 2.5]  -> CANNOT_MERGE_TYPE', 'red'), ('[1, "two"] -> string, silently', 'amber'),
           ('dict keys -> sorted columns', 'amber'), ('450 into DECIMAL -> TypeError', 'red'),
           ('inferSchema: 2 jobs, 4.6 s', 'amber'), ('explicit schema: 0 jobs, 0.0 s', 'green')])))
scene_svg = scene('A DataFrame can be created from Python lists, Rows, dicts, pandas, RDDs or files, with a schema inferred from the data or declared by you. We tried each way and measured what inference costs and where it goes wrong.', sc_,
                  'Infer while <tspan font-weight="700" class="s-acc">exploring</tspan>; declare the schema in <tspan font-weight="700" class="s-acc">production</tspan>.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“It worked yesterday”</h2>
  <div class="story">
    <p class="narration">TiffinGo’s nightly job reads a CSV export of 2 million orders with <code>inferSchema=True</code>. One night a partner sent amounts like <code>450.5</code> instead of <code>450</code>. Spark quietly inferred <code>double</code> instead of <code>int</code>, the table write failed on a type mismatch, and the dashboard stayed empty until noon.</p>

{scene_svg}

R> Sir, inference saves so much typing. Why not always use it?
A> Because the data decides your types, and the data changes. Inference also costs an extra pass over the file. In production we <b>declare the schema</b>: in a DDL string or a <code>StructType</code>.
K> And when I build small DataFrames in tests from Python lists?
A> Same rules apply, with a few surprises. Today we create DataFrames every common way, break inference on purpose, declare schemas with nested types, save a schema as JSON, and time inference on 2 million rows. All outputs are real (PySpark 4.3.0).
  </div>
</section>
'''

lv = '''
LEVELS> Schemas at three levels
L1> A form with labelled boxes
      <ul>
        <li>A schema is the printed form: each box has a name and says what may go in it (a number, a date, text).</li>
        <li>Inference is guessing the form by looking at the answers people wrote; one odd answer changes the guess.</li>
        <li>Declaring the schema is printing the form first, so wrong answers are noticed.</li>
      </ul>
L2> The API
      <ul>
        <li><code>spark.createDataFrame(data, schema)</code>: data is a list of tuples, Rows or dicts, a pandas DataFrame or an RDD; schema is a list of names, a DDL string (<code>"id INT, city STRING"</code>) or a <code>StructType</code>.</li>
        <li>Files: <code>spark.read.schema(…).csv(…)</code>, or <code>inferSchema=True</code> (CSV) and automatic inference (JSON).</li>
        <li><code>df.schema</code>, <code>df.printSchema()</code>, <code>df.schema.json()</code>, <code>StructType.fromJson()</code>.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>Python ints became <code>bigint</code>; <code>[1, 2.5]</code> failed with CANNOT_MERGE_TYPE; <code>[1, "two"]</code> silently became strings; dict keys came out sorted.</li>
        <li>A declared <code>DECIMAL</code> refused Python <code>int</code> and <code>float</code>; <code>nullable=False</code> rejected <code>None</code>.</li>
        <li>On 2M CSV rows, <code>inferSchema</code> ran 2 jobs and took 4.6 s before any query; an explicit schema took 0 jobs.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Creating DataFrames and schemas</h2>
''' + def_block(
    'A DataFrame’s <b>schema</b> is a <code>StructType</code>: an ordered list of <code>StructField</code>s, each with a name, a data type and a <code>nullable</code> flag. Types include atomic types (<code>IntegerType</code>, <code>LongType</code>, <code>DoubleType</code>, <code>DecimalType(p,s)</code>, <code>StringType</code>, <code>BooleanType</code>, <code>DateType</code>, <code>TimestampType</code>) and complex types (<code>ArrayType</code>, <code>MapType</code>, nested <code>StructType</code>). <code>SparkSession.createDataFrame()</code> builds a DataFrame from local data (tuples, Rows, dicts, pandas, NumPy) or an RDD; when no types are given, PySpark <b>infers</b> them from the data, otherwise the data is verified against the supplied schema. Data sources infer schemas from files (for CSV only with <code>inferSchema</code>, which requires an extra pass over the data) or use a schema supplied with <code>.schema()</code>.',
    'Every DataFrame has a list of column names and types. You can let Spark guess them from the data, or write them yourself. Guessing is handy for exploring but slow on big files and unsafe when the data changes; writing the schema makes jobs fast and predictable.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('StructType / StructField', 'The schema and one column in it.'),
    ('DDL string', '<code>"id INT, city STRING"</code>: a schema in SQL syntax.'),
    ('nullable', 'Whether a column may contain null.'),
    ('Inference', 'Spark guesses types from the data.'),
    ('inferSchema', 'CSV option: read the data to guess types.'),
    ('samplingRatio', 'Guess types from a fraction of rows.'),
    ('ArrayType / MapType', 'Lists and key-value maps in a column.'),
    ('schema.json()', 'Save a schema as JSON text.'),
]) + '''

  <h3>Python value → Spark type (inferred)</h3>
''' + table(['Python', 'Spark type', 'Note'], [
    ['<code>int</code>', '<code>bigint</code> (LongType)', 'Not <code>int</code>: declare INT if you want 32-bit'],
    ['<code>float</code>', '<code>double</code>', ''],
    ['<code>str</code>', '<code>string</code>', ''],
    ['<code>bool</code>', '<code>boolean</code>', ''],
    ['<code>datetime.date</code> / <code>datetime</code>', '<code>date</code> / <code>timestamp</code>', ''],
    ['<code>Decimal</code>', '<code>decimal(38,18)</code>', 'Declare precision yourself'],
    ['<code>list</code> / <code>dict</code> / <code>Row</code>', 'array / map / struct', 'Nested types'],
    ['<code>None</code> only', '—', 'CANNOT_DETERMINE_TYPE'],
], minw=620) + lv + '''
EXAM> “Why define a schema instead of inferSchema?” Inference needs an extra pass over the data (2 jobs and 4.6 s on our 2M-row CSV, 0 jobs with a schema), and the inferred types depend on the data, so one unusual value changes them. A declared schema is faster, stable across runs and documents the data contract.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Ways to create a DataFrame</h2>
''' + table(['From', 'Code', 'Use for'], [
    ['List of tuples', '<code>spark.createDataFrame(rows, "id INT, dish STRING")</code>', 'Tests, small lookups'],
    ['Row objects / dicts', '<code>createDataFrame([Row(id=1, …)])</code>', 'Readable test data'],
    ['pandas DataFrame', '<code>createDataFrame(pdf)</code>', 'Local results to Spark (Lesson 4.6)'],
    ['RDD', '<code>rdd.toDF(["id", "code"])</code>', 'Legacy RDD code'],
    ['Range', '<code>spark.range(0, 10, 2)</code>', 'Generated ids, benchmarks'],
    ['Files and tables', '<code>spark.read.schema(s).csv(…)</code>, <code>spark.table("t")</code>', 'Real data (Module 5)'],
    ['SQL', '<code>spark.sql("SELECT …")</code>', 'Queries'],
], minw=720) + '''
WARN> Phone numbers, PIN codes and ids with leading zeros are <b>text</b>, not numbers. Inference will happily read <code>0091…</code> or <code>400001</code> as a number and drop zeros or change formats. Declare such columns as <code>STRING</code> (Lesson 4.4 shows a phone column inferred as <code>bigint</code>).
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Every way in, and where inference breaks</h2>
  <p>All outputs are real: PySpark 4.3.0, local mode. Step 6 reads a 2-million-row CSV export of TiffinGo orders.</p>
''' + stepper([
    ('Step 1 · From Python objects',
     code('python', 'l42_create.py', 'spark.createDataFrame([(1, "Idli", 60.0), (2, "Dosa", 90.5)], ["id", "dish", "price"])\nspark.createDataFrame([Row(id=1, dish="Idli", veg=True)])\nspark.createDataFrame([{"id": 1, "dish": "Idli", "on": dt.date(2026, 11, 4)}])\nspark.createDataFrame(pd.DataFrame({"id": [1, 2], "price": [60.0, 90.5]}))\nsc.parallelize([(1, "a")]).toDF(["id", "code"])\nspark.range(0, 10, 2)', sec('== 1)', '== 3)')),
     'Every route gives a DataFrame with a schema. Python <code>int</code> always became <code>bigint</code>. Look at the dict: the columns came out <b>sorted by name</b> (<code>dish, id, on</code>), not in the order we wrote them. Use tuples with names, or Rows, when column order matters.'),
    ('Step 2 · Breaking inference',
     code('python', 'l42_create.py', 'spark.createDataFrame([(1,), (2.5,)], ["v"])\nspark.createDataFrame([(1,), ("two",)], ["v"])\nspark.createDataFrame([(None,), (None,)], ["v"])', sec('== 3)', '== 4)')),
     'Three outcomes, only two of them loud. An int and a float could not be merged; a column with only <code>None</code> had no type at all. But an int and a string were silently turned into <b>strings</b>: <code>1</code> became <code>"1"</code>. Silent changes are the dangerous ones.'),
    ('Step 3 · A DDL schema is checked',
     code('python', 'l42_create.py', 'ddl = "order_id INT, city STRING, amount DECIMAL(10,2), order_ts TIMESTAMP"\nfor v in (450, 450.75, Decimal("450.75")):\n    spark.createDataFrame([(1, "Pune", v, dt.datetime(2026, 11, 4, 20, 15))], ddl)', sec('== 4)', '== 5)')),
     'A DDL string is the shortest way to declare a schema. PySpark <b>verifies</b> local data against it: a <code>DECIMAL</code> column accepted only Python <code>Decimal</code>, not <code>int</code> or <code>float</code>. Money belongs in <code>DECIMAL</code>, never <code>double</code>, so this strictness protects you.'),
    ('Step 4 · StructType and nullable',
     code('python', 'l42_create.py', 'schema = StructType([StructField("order_id", IntegerType(), nullable=False),\n                     StructField("city", StringType(), True)])\nspark.createDataFrame([(1, "Pune"), (None, "Delhi")], schema)\nspark.createDataFrame([("x", "Pune")], schema)', sec('== 5)', '== 6)')),
     '<code>StructType</code> says the same as DDL in Python objects, plus <code>nullable</code>. For local data both a <code>None</code> in a non-nullable column and a wrong type were rejected immediately. (For files, Spark treats read columns as nullable; checks on nulls belong in your data-quality step, Lesson 4.4.)'),
    ('Step 5 · Nested types and schema as JSON',
     code('python', 'l42_create.py', 'nested = StructType([StructField("restaurant_id", IntegerType()),\n    StructField("tags", ArrayType(StringType())),\n    StructField("contact", StructType([StructField("phone", StringType()), StructField("email", StringType())])),\n    StructField("prices", MapType(StringType(), IntegerType()))])\nn.select("restaurant_id", n.tags[0], "contact.email", n.prices["thali"])\nStructType.fromJson(json.loads(n.schema.json())) == n.schema', sec('== 6)', '== 9)')),
     'Arrays, structs and maps let one row hold a restaurant’s tags, contact and price list, like the JSON in <code>restaurants.json</code>. Reach inside with <code>tags[0]</code>, <code>contact.email</code> and <code>prices["thali"]</code>. A schema can be saved as JSON and loaded back unchanged: keep it in your repository as the data contract. An empty DataFrame with a schema is handy as a starting point for unions.'),
    ('Step 6 · What inference costs on 2M rows',
     code('python', 'l42_create.py', 'spark.read.options(header=True).csv(path)                       # no schema\nspark.read.options(header=True, inferSchema=True).csv(path)     # guess types\nspark.read.options(header=True).csv(path, schema=big_schema)    # declared\nspark.read.options(header=True, inferSchema=True, samplingRatio=0.01).csv(path)', sec('== 9)')),
     'Without a schema every column is a <b>string</b>, and Spark still ran 1 job to read the header. <code>inferSchema</code> ran <b>2 jobs and 4.6 s</b> before our query even started, because it read the whole file to guess. The declared schema: <b>0 jobs</b>, instant. <code>samplingRatio</code> cut inference to 0.8 s and guessed right here, but a sample can miss the one odd value that matters.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('tuples  : id bigint, price double', W), ('dict    : dish, id, on  (sorted!)', Y), ('pandas  : id bigint', W)], size=7.4),
    term([('[1, 2.5]   : CANNOT_MERGE_TYPE', RD), ('[1, "two"] : string -> ["1", "two"]', Y), ('[None]     : CANNOT_DETERMINE_TYPE', RD)], size=7.4),
    term([('DECIMAL(10,2) <- 450      : TypeError', RD), ('DECIMAL(10,2) <- Decimal : 450.75', G), ('nullable=False <- None    : error', RD)], size=7.0),
    term([('tags[0]       : late-night', W), ('contact.email : k@t.in', W), ('fromJson(json) == schema : True', G)], size=7.4),
    term([('no schema  : all string, 1 job', Y), ('inferSchema: 2 jobs, 4.6 s', Y), ('declared   : 0 jobs, 0.0 s', G)], size=7.6),
]
B1 = [
    t(180, 14, 'Python objects become rows', 9.4, bold=True) + flow([('tuples', 'list', 'card'), ('Rows', 'named', 'card'), ('pandas', 'pdf', 'card'), ('DataFrame', 'schema', 'blue')], y=44, w=72, gap=14) + cap('Types are guessed from values.', '', 'blue', y=144, h=30),
    t(180, 14, 'Inference merges types', 9.4, bold=True) + schema_box(30, 34, [('v: 1', 'bigint', None), ('v: 2.5', 'double', 'red'), ('v: "two"', 'string', 'amber')], 'values seen', 'card', 150) + opbox(210, 50, 'merged type', 'error or string', 'amber', 130, 30) + arrow(180, 64, 210, 64, 'ink3', 1.1) + cap('One odd value changes the column.', '', 'amber', y=144, h=30),
    t(180, 14, 'A declared schema is a contract', 9.4, bold=True) + schema_box(30, 34, [('order_id', 'INT NOT NULL', 'green'), ('amount', 'DECIMAL(10,2)', 'green')], 'schema', 'green', 160) + opbox(220, 46, 'bad row', 'rejected', 'acc', 120, 30) + cap('Wrong types are stopped early.', '', 'green', y=144, h=30),
    t(180, 14, 'Nested columns', 9.4, bold=True) + schema_box(30, 30, [('tags', 'array<string>', 'violet'), ('contact', 'struct<…>', 'violet'), ('prices', 'map<string,int>', 'violet')], 'restaurant', 'violet', 200) + cap('One row holds lists and objects.', '', 'violet', y=144, h=30),
    t(180, 14, 'Inference reads the data first', 9.4, bold=True) + flow([('read.csv', 'infer', 'amber'), ('scan 2M', 'extra job', 'amber'), ('query', 'scan again', 'card')], y=40, w=96, gap=22) + flow([('read.csv', 'schema', 'green'), ('query', 'one scan', 'green')], y=88, w=96, gap=22) + cap('A schema skips the extra pass.', '', 'green', y=144, h=30),
]
see_caps = ['Many routes, one schema each.', 'Two loud failures, one silent.', 'Declared types were enforced.', 'Nested data and a JSON schema.', 'Inference cost 2 jobs on 2M rows.']
behind_caps = ['PySpark infers types from the values.', 'Types must merge across rows.', 'Local data is verified against the schema.', 'Arrays, structs and maps.', 'Declared schema: no extra scan.']
two = anim_two('Creating DataFrames', 'Guess or declare', 'Real lab outputs', 'The schema', see, B1, see_caps, behind_caps)

# ---- scenario 1: nightly type drift
e1 = (t(180, 22, 'Nightly CSV, inferSchema=True', 9.4, bold=True) + t(180, 56, 'amount inferred as int', 8.4, 'ink2') + cap('Worked for months.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Partner sends 450.5', 9.4, bold=True) + t(180, 56, 'amount now inferred as double', 8.4, 'ink2') + cap('The data changed the type.', '', 'amber', y=150, h=34))
e3 = (t(180, 22, 'Write to table fails', 9.4, bold=True) + t(180, 56, 'type mismatch: int vs double', 8.4, 'ink', mono=True) + cap('Dashboard empty till noon.', '', 'red', y=150, h=34))
e4 = (t(180, 22, 'Declare the schema', 9.4, bold=True) + t(180, 56, 'amount DECIMAL(10,2)', 8.4, 'ink', mono=True) + cap('Types fixed by contract.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Bad values become visible', 9.4, 'acc', bold=True) + t(180, 56, 'mode / quarantine (Module 5)', 8.4, 'ink2') + cap('Fail loudly, not silently.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Inference changed a type overnight',
              'Why production jobs declare schemas. (Typical; behaviour from our lab.)',
              'Schema drift', 'Inferred types follow the data; a declared schema keeps types stable and exposes bad values', [e1, e2, e3, e4, e5],
              ['Inferred.', 'Data changed.', 'Write failed.', 'Declare it.', 'Handle bad rows.'],
              hid='scenario-drift')

# ---- scenario 2: slow start
b1 = (t(180, 22, '200 GB of CSV every hour', 9.4, bold=True) + t(180, 56, 'inferSchema=True', 8.4, 'ink', mono=True) + cap('Job starts slowly.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'Spark UI: an extra job', 9.4, bold=True) + t(180, 56, 'whole files read to guess types', 8.4, 'ink2') + cap('Like our 2 jobs, 4.6 s.', '', 'amber', y=150, h=34))
b3 = (t(180, 22, 'Schema stored in the repo', 9.4, bold=True) + t(180, 56, 'StructType.fromJson(…)', 8.4, 'ink', mono=True) + cap('Loaded at start.', '', 'green', y=150, h=34))
b4 = (t(180, 22, 'One scan instead of two', 9.4, bold=True) + t(180, 56, 'read() runs 0 jobs', 8.4, 'ink2') + cap('Faster every hour.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Better: Parquet upstream', 9.4, 'acc', bold=True) + t(180, 56, 'schema stored in the files', 8.4, 'ink2') + cap('Lesson 5.2.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Paying to guess, every hour',
              'The hidden cost of inferSchema. (Typical; costs from our lab.)',
              'Inference cost', 'inferSchema reads the data an extra time; loading a stored schema avoids the pass', [b1, b2, b3, b4, b5],
              ['Big hourly CSV.', 'Extra job.', 'Stored schema.', 'One scan.', 'Use Parquet.'],
              hid='scenario-infer')

# ---- scenario 3: test data
u1 = (t(180, 22, 'Unit test builds test rows', 9.4, bold=True) + t(180, 56, 'createDataFrame([{…}, {…}])', 8.4, 'ink', mono=True) + cap('Dicts, no schema.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'Columns come out sorted', 9.4, bold=True) + t(180, 56, 'dish, id, on', 8.4, 'ink', mono=True) + cap('Union by position mixes them.', '', 'amber', y=150, h=34))
u3 = (t(180, 22, 'ints are bigint', 9.4, bold=True) + t(180, 56, 'production table uses INT', 8.4, 'ink2') + cap('Test and prod differ.', '', 'red', y=150, h=34))
u4 = (t(180, 22, 'Same schema as production', 9.4, bold=True) + t(180, 56, 'createDataFrame(rows, PROD_SCHEMA)', 8.0, 'ink', mono=True) + cap('Tests match reality.', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'assertSchemaEqual', 9.4, 'acc', bold=True) + t(180, 56, 'pyspark.testing (Lesson 11.4)', 8.4, 'ink2') + cap('Check schemas in tests.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Tests that pass, production that fails',
              'Test DataFrames need real schemas. (Typical; behaviour from our lab.)',
              'Test data schemas', 'Inferred test DataFrames have sorted dict columns and bigint ints; build them with the production schema', [u1, u2, u3, u4, u5],
              ['Dict rows.', 'Sorted columns.', 'Different types.', 'Use prod schema.', 'Assert schemas.'],
              hid='scenario-tests')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Guess or declare</h2>
  <p>Left: real outputs. Right: what happens to the schema.</p>
''' + two + '''
  <p>Three live scenarios follow: a type that changed overnight, the cost of guessing, and test data that does not match production.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Schemas at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'contract', 10, 'blue', bold=True) + t(60, 58, 'in git', 7.4, 'ink2'),
    '1. Data contracts',
    'Teams keep schemas as JSON or DDL in the repository and load them in every job that reads a feed.',
    ['schema.json', '*fromJson', 'read.schema()']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, '₹', 14, 'green', bold=True) + t(60, 58, 'DECIMAL', 7.4, 'ink2'),
    '2. Money columns',
    'Payments and invoices use DECIMAL(p,s), never double, so totals do not drift by paise.',
    ['amount', '*DECIMAL(12,2)', 'Exact sums']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'JSON', 12, 'violet', bold=True) + t(60, 58, 'nested', 7.4, 'ink2'),
    '3. Nested events',
    'App events with arrays and objects keep their shape as array, struct and map columns.',
    ['Event JSON', '*struct/array', 'Query fields']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'tests', 12, 'acc', bold=True) + t(60, 58, 'fixtures', 7.4, 'ink2'),
    '4. Test fixtures',
    'Unit tests build small DataFrames from tuples with the production schema.',
    ['Tuples', '*PROD_SCHEMA', 'Assertions']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'lookup', 11, 'acc', bold=True) + t(60, 58, 'small', 7.4, 'ink2'),
    '5. Small lookup tables',
    'Code lists such as city to region are created in code and joined to large tables.',
    ['Python list', '*createDataFrame', 'Join']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> the SparkSession and a first DataFrame in <a href="../01-sparksession-and-dataframes/">4.1</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
