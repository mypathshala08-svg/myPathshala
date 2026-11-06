import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
BODY = body(HERE)

META = dict(
    module='06-transformations', lesson='05-complex-data-and-variant', n='6.5',
    module_label='Module 6 · Transformations',
    title='Complex data and VARIANT',
    desc='Arrays, maps, structs and the Spark 4 VARIANT type in PySpark 4.3.0: transform, filter, aggregate and arrays_zip inside arrays, explode (5 rows) vs explode_outer (6), map and struct access, from_json turning a whole record null on one bad field, schema_of_json missing a field, parse_json and variant_get extracting fields independently, INVALID_VARIANT_CAST vs try_variant_get, and one field read from 1M payloads in about 2 s as text vs 0.62 s as stored VARIANT.',
    og_desc='One bad field made from_json return an all-null record; VARIANT kept the rest. Arrays, maps, structs and VARIANT in Spark 4, tested.',
    minutes=32, level='Intermediate',
    lead='Orders contain lists of dishes, preference maps and nested objects, and app payloads arrive as JSON that changes with every release. This lesson works with arrays, maps and structs without exploding, parses JSON with a schema, and uses Spark 4’s <b>VARIANT</b> type for evolving payloads. <b>All outputs are real</b> (PySpark 4.3.0).',
    chips=['PySpark 4.3.0', 'VARIANT (Spark 4)', '1M payloads timed', 'Runs in your browser (Python)'],
)

MAIN = '''# from_json vs VARIANT on a payload with one bad field (simplified model)
import json
payloads = ['{"order_id": 1, "items": [{"dish": "Thali", "qty": 2}]}',
            '{"order_id": "3", "items": "none"}']

def from_json(p):                        # all fields must fit the schema
    d = json.loads(p)
    if not isinstance(d.get("items"), list):
        return {"order_id": None, "items": None}
    return {"order_id": int(d["order_id"]), "items": d["items"]}

def variant_get(p, key, cast):          # each field on its own
    try:
        return cast(json.loads(p)[key])
    except (KeyError, ValueError, TypeError):
        return None

for p in payloads:
    print("from_json  :", from_json(p))
    print("variant_get:", variant_get(p, "order_id", int))
'''
RUN = dict(
    heading='Run the code: record-level vs field-level parsing',
    intro='<p>A model of Steps 4–5. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('        return {"order_id": None, "items": None}', 'In the lab the whole record came back null.'),
        ('def variant_get(p, key, cast):          # each field on its own', 'VARIANT extracts each path independently.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Then add a payload without order_id.', code=None),
        dict(label='2 · Predict first: explode', hint='<b>Predict first:</b> rows from explode and explode_outer for lists of 2, 3 and 0 items.',
             code='''lists = [2, 3, 0]
print("explode:", sum(lists), "| explode_outer:", sum(max(n, 1) for n in lists))
'''),
        dict(label='3 · aggregate()', hint='Order total without exploding.',
             code='''from functools import reduce
items = [{"price": 90, "qty": 1}, {"price": 60, "qty": 2}]
print(reduce(lambda acc, i: acc + i["price"] * i["qty"], items, 0))
'''),
        dict(label='4 · transform and filter', hint='Add GST and keep items from ₹60.',
             code='''prices = [90, 60, 30]
print([p * 105 / 100 for p in prices], [p for p in prices if p >= 60])
'''),
        dict(label='5 · Spot the error', hint='This schema was inferred from one payload.', expect='error',
             code='''inferred_from = 1
assert inferred_from > 100, "schema_of_json on one record misses optional fields (coupon): write the schema or use VARIANT"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: complex data',
    intro='<p>In the <code>pyspark</code> shell. <b>Outputs are real</b> (PySpark 4.3.0).</p>',
    items=[
        dict(title='1 · explode vs explode_outer', cmd='o.select(F.explode("dishes")).count(), o.select(F.explode_outer("dishes")).count()', file='pyspark',
             output='(5, 6)', note='The empty order is kept only by explode_outer.'),
        dict(title='2 · VARIANT path', cmd='spark.sql("SELECT parse_json(\'{\\"a\\": {\\"b\\": [10, 20]}}\'):a.b[1]::int AS b").first()', file='pyspark',
             output='Row(b=20)', note='SQL path syntax.'),
        dict(title='3 · Strict cast', cmd='v.select(F.variant_get("v", "$.items", "array<struct<dish string, qty int>>")).collect()', file='pyspark',
             output='[INVALID_VARIANT_CAST] The variant value `"none"` cannot be cast into `"ARRAY<STRUCT<dish: STRING, qty: INT>>"`. Please use `try_variant_get` instead.', note='try_variant_get returns null.'),
    ],
)

TRACE = dict(
    heading='aggregate() step by step',
    intro='<p>Follow the accumulator through an array.</p>',
    code='''prices = [90, 60, 30]
acc = 0
for p in prices:
    acc = acc + p
    print("after", p, "acc =", acc)
''',
    notes={2: 'Start :: F.lit(0) is the initial value.', 4: 'Merge :: The lambda (acc, p) -> acc + p.'},
)

WORKED_INTRO = 'Three nested-data tasks at TiffinGo.'
EXAMPLES = [
    dict(level='b', tag='Arrays · basics', title='Flag orders with dessert',
         problem='<p>Add a boolean: does the order contain a dessert?</p>',
         inp='dishes ARRAY<STRING>',
         approach=['exists with a lambda.', 'No explode.', 'One row per order.'],
         code='''desserts = {"Gulab Jamun", "Kheer"}
for dishes in (["Thali", "Kheer"], ["Dosa"]):
    print(dishes, any(d in desserts for d in dishes))
''', notes={3: 'Spark :: F.exists("dishes", lambda d: d.isin("Gulab Jamun", "Kheer")).'},
         tryit='Step 1.'),
    dict(level='i', tag='JSON · parsing', title='Parse payloads with a schema',
         problem='<p>Turn app payloads into typed columns.</p>',
         inp='payload STRING',
         approach=['Write the schema (not from one example).', 'from_json.', 'Count all-null results.'],
         code='''print("""parsed = raw.select(F.from_json("payload", SCHEMA).alias("j")).select("j.*")
bad = parsed.where("order_id IS NULL").count()""")
''', notes={2: 'Watch :: A mismatch nulls the whole record.'},
         tryit='Step 4.'),
    dict(level='a', tag='VARIANT · design', title='Bronze VARIANT, silver columns',
         problem='<p>Ingest evolving payloads without losing records.</p>',
         inp='payload STRING',
         approach=['bronze: parse_json → VARIANT.', 'silver: try_variant_get hot fields.', 'Monitor schema_of_variant.'],
         code='''print("""bronze = raw.select(F.parse_json("payload").alias("v"))
silver = bronze.select(F.try_variant_get("v", "$.order_id", "bigint").alias("order_id"),
                       F.try_variant_get("v", "$.coupon.code", "string").alias("coupon"), "v")""")
''', notes={2: 'Keep v :: New fields are still available later.'},
         tryit='Steps 5–6.'),
]

QUIZ = mix([
    dict(q='Beginner: How do you read map value "spice"?', options=['notes.spice', 'notes["spice"]', 'notes(spice)', 'map_keys'], answer=1,
         why='Brackets for maps.'),
    dict(q='Beginner: Which keeps orders with empty arrays?', options=['explode', 'explode_outer', 'posexplode', 'flatten'], answer=1,
         why='6 rows vs 5.'),
    dict(q='Beginner: Which Spark version added VARIANT?', options=['2.4', '3.5', '4.0', '1.6'], answer=2,
         why='GA in 4.1.'),
    dict(q='Intermediate: Total of an array without exploding?', options=['sum()', 'aggregate()', 'count()', 'size()'], answer=1,
         why='Higher-order function.'),
    dict(q='Intermediate: from_json with one mismatched field returns…', options=['Only that field null', 'The whole record null', 'An error', 'A string'], answer=1,
         why='PERMISSIVE at record level.'),
    dict(q='Intermediate: What does try_variant_get return on a failed cast?', options=['Error', 'NULL', 'String', 'Empty array'], answer=1,
         why='variant_get would fail.'),
    dict(q='Advanced: Why was stored VARIANT faster than JSON text?', options=['Smaller', 'No text parsing: binary encoding with addressable paths', 'Cached', 'Compressed'], answer=1,
         why='0.62 s vs ~2 s.'),
    dict(q='Advanced: Risk of schema_of_json on one record?', options=['None', 'Optional fields are missed', 'Slow', 'Fails'], answer=1,
         why='coupon missing.'),
])

REVISION = [
    'ARRAY, MAP, STRUCT: <code>c[0]</code>, <code>c["k"]</code>, <code>c.f</code>.',
    'Higher-order functions: <code>transform</code>, <code>filter</code>, <code>exists</code>, <code>aggregate</code>: no explode needed.',
    '<code>explode</code> drops empty/null arrays (5 rows); <code>explode_outer</code> keeps them (6).',
    '<code>from_json</code> + schema: one bad field → whole record null. Do not infer from one example.',
    'VARIANT: <code>parse_json</code>, <code>variant_get</code>/<code>try_variant_get</code>, <code>schema_of_variant</code>, SQL <code>v:a.b::int</code>.',
    'Parse once: stored VARIANT read in 0.62 s vs ~2 s from text.',
    'Promote hot fields to typed columns; keep the VARIANT for the rest.',
]
FAQ = [
    ('Can I write VARIANT to Parquet?', 'Yes, Spark 4 writes VARIANT to Parquet and Delta. Check that readers (other engines) support it before sharing.'),
    ('Is explode expensive?', 'It multiplies rows; any later aggregation must shuffle them. Use higher-order functions when one row per record is enough.'),
    ('How do I flatten a struct into columns?', '<code>df.select("order_id", "rider.*")</code>.'),
    ('Can I update a field inside a struct?', '<code>F.col("rider").withField("rating", F.lit(5.0))</code>; <code>dropFields</code> removes fields.'),
    ('Are Python lambdas in transform slow?', 'No: they are converted to Spark expressions, not executed in Python, as long as you use Column operations inside.'),
]

PRACTICE_INTRO = 'Programs about nested data.'
PROBLEMS = [
    dict(level='easy', title='Array size', stmt='Items per order.', inp='lists',
         code='''print([len(x) for x in (["Thali", "Lassi"], ["Dosa", "Idli", "Coffee"], [])])
''', explain='F.size.'),
    dict(level='easy', title='Contains', stmt='Orders that contain Dosa.', inp='lists',
         code='''orders = {9101: ["Thali"], 9102: ["Dosa", "Idli"]}
print([o for o, d in orders.items() if "Dosa" in d])
''', explain='array_contains.'),
    dict(level='easy', title='Map keys', stmt='Keys of a preference map.', inp='{"spice": "medium", "cutlery": "no"}',
         code='''print(sorted({"spice": "medium", "cutlery": "no"}))
''', explain='map_keys.'),
    dict(level='medium', title='Zip', stmt='Pair dishes with prices.', inp='two arrays',
         code='''print(list(zip(["Dosa", "Idli"], [90, 60])))
''', explain='arrays_zip.'),
    dict(level='medium', title='Explode outer', stmt='Flatten keeping empty orders.', inp='orders with lists',
         code='''orders = {9101: ["Thali"], 9103: []}
print([(o, d) for o, ds in orders.items() for d in (ds or [None])])
''', explain='explode_outer.'),
    dict(level='medium', title='Safe path', stmt='Get a nested value or None.', inp='{"coupon": {"code": "FEST20"}}',
         code='''d = {"coupon": {"code": "FEST20"}}
print(d.get("coupon", {}).get("code"), {}.get("coupon", {}).get("code"))
''', explain='variant_get / try_variant_get.'),
    dict(level='business', title='Parse savings', stmt='Seconds saved per day by storing VARIANT.', inp='~2.0 vs 0.62 s per query, 500 queries/day',
         code='''print(round((2.0 - 0.62) * 500), "s")
''', explain='Parse once, read many times.'),
    dict(level='business', title='Lost orders', stmt='Orders lost if 1% of payloads mismatch with from_json.', inp='200,000 orders/day',
         code='''print(int(200_000 * 0.01), "orders per day")
''', explain='VARIANT keeps their ids.'),
]

SCN_INTRO = 'Nested data questions are common at product companies with event data.'
SCENARIOS = (
    scn('Any company · PySpark', 'Fresher', '“How do you flatten a JSON array?”',
        'Each order has an array of items. Get one row per item.',
        'explode?',
        '<p><code>df.select("order_id", F.explode_outer("items").alias("it")).select("order_id", "it.dish", "it.qty")</code>. I use explode_outer so orders without items are not lost.</p>', 'Using a Python loop on collected data.') +
    scn('Data engineering', 'Mid-level', 'Totals per order',
        'Compute each order’s total from its item array.',
        'higher-order functions?',
        '''<ul>
          <li>F.aggregate over items with price × qty.</li>
          <li>No explode, no shuffle, one row per order.</li>
          <li>Explode only for item-level analysis.</li>
        </ul>''', 'explode + groupBy for a per-row value.') +
    scn('Data engineering', 'Mid-level', 'Changing payload schema',
        'App payloads keep changing and parsing breaks.',
        'VARIANT awareness?',
        '''<ol>
          <li>from_json nulls whole records on mismatch.</li>
          <li>Ingest as VARIANT (Spark 4), extract fields with try_variant_get.</li>
          <li>Monitor schema drift with schema_of_variant.</li>
        </ol>''', 'Making every field a string.') +
    scn('Platform', 'Senior', 'Semi-structured storage',
        'How would you store and serve evolving event data?',
        'design?',
        '''<ul>
          <li>Bronze: VARIANT column in Delta/Parquet.</li>
          <li>Silver: promoted typed columns for hot fields.</li>
          <li>Parse once; queries read binary VARIANT (0.62 s vs ~2 s per 1M rows in my test).</li>
        </ul>''', 'Querying raw JSON text forever.')
)
