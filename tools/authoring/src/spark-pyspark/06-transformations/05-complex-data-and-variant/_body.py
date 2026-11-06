import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
C = 'l65_complex.txt'
def sec(a, b=None, drop=()):
    s = capsec(C, a, b, drop)
    return '\n'.join(l if len(l) <= 140 else l[:137] + ' …' for l in s.split('\n'))

def cells(x, y, vals, tone='card', w=44):
    o = ''
    for k, v in enumerate(vals):
        o += box(x + k * (w + 3), y, w, 18, tone, rx=3) + t(x + k * (w + 3) + w / 2, y + 12, v, 6.8, mono=True)
    return o

# ---------------------------------------------------------------- story
sc_ = (t(14, 30, 'order 9102', 7.6, 'ink', anchor='start', bold=True) + cells(14, 38, ['Dosa', 'Idli', 'Coffee'], 'blue') + cells(14, 62, ['90', '60', '30'], 'green') +
       t(14, 100, '{"spice": "high"}', 7.0, 'violet', anchor='start', mono=True) + t(14, 118, 'rider: {Asha, NULL}', 7.0, 'ink2', anchor='start', mono=True) +
       box(400, 12, 232, 132, 'card') + t(516, 30, 'Measured', 8.6, bold=True) +
       ''.join(t(412, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
           ('explode 5 rows, explode_outer 6', 'amber'), ('from_json: bad row → all NULL', 'red'),
           ('variant_get: order_id "3" → 3', 'green'), ('strict variant_get: error', 'red'),
           ('JSON string 1M rows: 1.9–2.4 s', 'amber'), ('stored VARIANT: 0.62 s', 'green')])))
scene_svg = scene('Real data is nested: orders contain lists of dishes, preference maps and rider objects, and app payloads arrive as JSON strings. We used arrays, maps and structs, parsed JSON with a schema and with Spark 4’s VARIANT type, and timed both.', sc_,
                  'Use <tspan font-weight="700" class="s-acc">higher-order functions</tspan> on arrays; store changing JSON as <tspan font-weight="700" class="s-acc">VARIANT</tspan>.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“The app team changed the payload again”</h2>
  <div class="story">
    <p class="narration">TiffinGo’s app sends every order as a JSON string with dishes, coupons and rider details. Each release adds or changes a field. Kabir’s pipeline parses the payload with a fixed schema; when one release sent <code>"items": "none"</code> instead of a list, those orders came out with <b>every</b> field null, including the order id.</p>

{scene_svg}

K> Sir, one field was wrong. Why did the whole record become null?
A> <code>from_json</code> parses the record as a whole: if any field does not fit the schema, the record is null. Spark 4 offers another way: store the payload as <b>VARIANT</b> and extract fields one at a time, each with its own type.
R> And arrays inside the record? Do we always explode them?
A> Not always. Spark has functions that work <b>inside</b> arrays: transform, filter, aggregate. Today: arrays, maps and structs, explode and its variants, JSON strings with from_json, then VARIANT, and a speed test on a million payloads. All outputs are real (PySpark 4.3.0).
  </div>
</section>
'''

lv = '''
LEVELS> Complex data at three levels
L1> A tiffin box
      <ul>
        <li>An order is a tiffin box with compartments (a struct), a list of dishes (an array) and a note card of preferences (a map).</li>
        <li>Exploding is taking every dish out and putting it on its own plate.</li>
        <li>VARIANT is accepting the box as it comes and opening only the compartments you need.</li>
      </ul>
L2> The API
      <ul>
        <li>Types: <code>ArrayType</code>, <code>MapType</code>, <code>StructType</code>, <code>VariantType</code> (Spark 4.0+). Access: <code>col[0]</code>, <code>col["key"]</code>, <code>col.field</code> / <code>"a.b"</code>.</li>
        <li>Arrays: <code>size</code>, <code>array_contains</code>, <code>transform</code>, <code>filter</code>, <code>aggregate</code>, <code>arrays_zip</code>, <code>explode</code>/<code>explode_outer</code>/<code>posexplode</code>.</li>
        <li>JSON: <code>from_json</code>, <code>to_json</code>, <code>schema_of_json</code>, <code>get_json_object</code>; VARIANT: <code>parse_json</code>, <code>variant_get</code>, <code>try_variant_get</code>, <code>schema_of_variant</code>, SQL <code>v:path::type</code>.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li><code>explode</code> gave 5 rows from 3 orders (the empty one vanished); <code>explode_outer</code> gave 6.</li>
        <li>With <code>from_json</code>, the payload with <code>"items": "none"</code> became all-null; VARIANT still returned its order id.</li>
        <li>Summing one field over 1M JSON strings took 1.9–2.4 s; over a stored VARIANT column, 0.62 s.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Complex types and VARIANT</h2>
''' + def_block(
    'Spark SQL supports <b>complex types</b>: <code>ARRAY&lt;T&gt;</code> (ordered elements of one type), <code>MAP&lt;K, V&gt;</code> (key-value pairs) and <code>STRUCT&lt;…&gt;</code> (named fields), which can be nested. <b>Higher-order functions</b> such as <code>transform</code>, <code>filter</code>, <code>exists</code> and <code>aggregate</code> apply lambda expressions to array elements inside the JVM without exploding. <code>explode</code> produces one row per element (dropping rows with null or empty arrays), <code>explode_outer</code> keeps them with null. JSON text is parsed with <code>from_json</code> against a schema; in the default PERMISSIVE mode a record that does not match yields null. The <b>VARIANT</b> type (Spark 4.0, GA in 4.1) stores semi-structured data in a binary encoding without a fixed schema; <code>parse_json</code> creates it and <code>variant_get</code>/<code>try_variant_get</code> extract a path cast to a requested type.',
    'Columns can hold lists, maps and nested objects. Spark has functions to work inside lists without breaking them apart, and explode when you need one row per item. JSON can be parsed with a fixed schema, or stored as VARIANT and read field by field, which survives changing payloads.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Array / map / struct', 'List / key-value pairs / named fields in one column.'),
    ('Higher-order function', 'transform, filter, aggregate with a lambda.'),
    ('explode / explode_outer', 'One row per element (outer keeps empties).'),
    ('from_json', 'Parse a JSON string with a schema.'),
    ('schema_of_json', 'Infer a schema from one JSON example.'),
    ('VARIANT', 'Semi-structured value with no fixed schema.'),
    ('variant_get', 'Extract a path as a type (error if impossible).'),
    ('try_variant_get', 'Same, null instead of an error.'),
]) + '''

  <h3>JSON string, from_json or VARIANT?</h3>
''' + table(['', 'Raw JSON string', 'from_json (schema)', 'VARIANT'], [
    ['Schema needed', 'no', 'yes, fixed', 'no'],
    ['Payload changes', 'fine, but parsed every query', 'mismatch → whole record null', 'per-field: missing → null'],
    ['Reading one field (1M rows)', '2.08 s (get_json_object)', '2.43 s', '0.62 s once stored'],
    ['Typed columns for BI', 'no', 'yes', 'extract to columns'],
    ['Best for', 'landing as-is', 'stable, known payloads', 'evolving payloads, wide JSON'],
], minw=660) + lv + '''
EXAM> “explode vs explode_outer?” explode returns one row per array element and drops rows whose array is null or empty; explode_outer keeps those rows with a null element. In our lab 3 orders gave 5 rows with explode and 6 with explode_outer: the order with no dishes disappeared from the first.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Functions by type</h2>
''' + table(['Type', 'Access', 'Useful functions'], [
    ['ARRAY', '<code>c[0]</code>, <code>element_at(c, 1)</code>', 'size, array_contains, sort_array, array_distinct, slice, transform, filter, exists, aggregate, arrays_zip, flatten, explode'],
    ['MAP', '<code>c["key"]</code>, <code>element_at(c, k)</code>', 'map_keys, map_values, map_entries, map_filter, transform_values, explode (key, value)'],
    ['STRUCT', '<code>c.field</code>, <code>"c.field"</code>, <code>c.*</code>', 'struct, named_struct, withField, dropFields'],
    ['VARIANT', '<code>variant_get(v, "$.a.b[0]", "int")</code>, SQL <code>v:a.b[0]::int</code>', 'parse_json, try_parse_json, schema_of_variant, is_variant_null, to_json'],
], minw=700) + '''
WARN> <code>explode</code> multiplies rows and silently drops records with empty or null arrays. Before exploding, ask whether a higher-order function would do: totals, filters and lookups inside arrays (<code>aggregate</code>, <code>filter</code>, <code>exists</code>) keep one row per order and avoid a later re-aggregation.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Nested orders and changing payloads</h2>
  <p>All outputs are real: PySpark 4.3.0, local mode with 4 cores. Steps 1–5 use three small orders and payloads; Step 6 uses 1,000,000 generated JSON payloads.</p>
''' + stepper([
    ('Step 1 · Working inside arrays',
     code('python', 'l65_complex.py', 'o.select("order_id", F.size("dishes"), F.array_contains("dishes", "Dosa"),\n    F.transform("prices", lambda p: p * 105 / 100), F.filter("prices", lambda p: p >= 60),\n    F.aggregate("prices", F.lit(0), lambda acc, p: acc + p), F.arrays_zip("dishes", "prices"))', sec('== 1)', '== 2)')),
     'Each function worked on the whole array, still one row per order: GST added to every price, cheap items filtered out, totals summed with <code>aggregate</code>, and dishes paired with prices by <code>arrays_zip</code>. The Python lambdas are translated into Spark expressions; they do not run in Python.'),
    ('Step 2 · explode and its variants',
     code('python', 'l65_complex.py', 'o.select(F.explode("dishes")).count()\no.select(F.explode_outer("dishes")).count()\no.select("order_id", F.posexplode("dishes").alias("pos", "dish"))', sec('== 2)', '== 3)')),
     'Five dishes, five rows; order 9103 with an empty list vanished. <code>explode_outer</code> kept it as a sixth row with a null dish. <code>posexplode</code> also returned the position, useful when order inside the array matters.'),
    ('Step 3 · Maps and structs',
     code('python', 'l65_complex.py', 'o.select("order_id", F.col("notes")["spice"], F.map_keys("notes"), "rider.name", F.col("rider.rating"))', sec('== 3)', '== 4)')),
     'Map values are read by key (null if the key is missing); <code>map_keys</code> lists keys. Struct fields are read with a dot. A null struct gives null fields rather than an error, so 9103 (no rider) simply shows nulls.'),
    ('Step 4 · JSON strings with from_json',
     code('python', 'l65_complex.py', 'raw.select(F.schema_of_json(F.lit(raw.first().payload)))\nsch = "order_id INT, items ARRAY<STRUCT<dish: STRING, qty: INT>>, tip INT, coupon STRUCT<code: STRING, pct: INT>"\nraw.select(F.from_json("payload", sch).alias("j")).select("j.order_id", "j.items", "j.tip", "j.coupon.code")', sec('== 4)', '== 5)')),
     '<code>schema_of_json</code> inferred a schema from one example, which missed <code>coupon</code> because the first payload had none: never infer from a single record. With a full schema, missing fields became null. But payload 3, where <code>items</code> was the string "none", came back <b>entirely null</b>, order id included: one bad field cost the whole record.'),
    ('Step 5 · VARIANT',
     code('python', 'l65_complex.py', 'v = raw.select(F.parse_json("payload").alias("v"))\nv.select(F.variant_get("v", "$.order_id", "int"), F.variant_get("v", "$.items[0].dish", "string"),\n         F.variant_get("v", "$.coupon.code", "string"), F.schema_of_variant("v"))\nv.select(F.variant_get("v", "$.items", "array<struct<dish string, qty int>>"))\nv.select(F.try_variant_get("v", "$.items", "array<struct<dish string, qty int>>"))\nspark.sql("SELECT parse_json(\'{\\"a\\": 1}\'):a::int AS a, …")', sec('== 5)', '== 6)')),
     'Parsed as VARIANT, every payload kept its own shape (<code>schema_of_variant</code> shows three different schemas). Each field was extracted independently: payload 3’s order id, sent as the string "3", came back as 3, while its odd <code>items</code> did not affect anything else. Asking for <code>items</code> as an array failed loudly with INVALID_VARIANT_CAST; <code>try_variant_get</code> returned null instead. SQL has a short path syntax <code>v:a.b[1]::int</code>.'),
    ('Step 6 · Speed on 1M payloads',
     code('python', 'l65_complex.py', 'j.select(F.sum(F.get_json_object("payload", "$.amount").cast("int")))\nj.select(F.sum(F.from_json("payload", "amount INT").amount))\nj.select(F.sum(F.variant_get(F.parse_json("payload"), "$.amount", "int")))\nvt = j.select(F.parse_json("payload").alias("v")).cache()\nvt.select(F.sum(F.variant_get("v", "$.amount", "int")))', sec('== 6)')),
     'All three ways to read one field from JSON <b>text</b> took about 2 s, because each must parse the text. Once the payload was stored as VARIANT (here cached; in practice written to a Delta or Parquet table), reading the field took <b>0.62 s</b>: VARIANT’s binary encoding lets Spark jump to the field. Parse once at ingestion, then query many times.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('with_gst [94.5, 63.0, 31.5]', W), ('total 180 via aggregate', G), ('zipped [{Dosa, 90}, …]', W)], size=7.4),
    term([('explode      : 5 rows', Y), ('explode_outer: 6 rows', G)], size=7.6),
    term([('notes["spice"] = high', W), ('rider.name = Asha, rating NULL', W)], size=7.6),
    term([('from_json row 3: NULL NULL NULL', RD), ('schema_of_json missed coupon', Y)], size=7.4),
    term([('variant_get order_id: 1, 2, 3', G), ('strict cast: INVALID_VARIANT_CAST', RD), ('stored VARIANT: 0.62 s vs ~2 s', G)], size=7.2),
]
B1 = [
    t(180, 14, 'Functions inside the array', 9.4, bold=True) + cells(30, 40, ['90', '60', '30'], 'card', 50) + arrow(190, 49, 220, 49, 'ink3', 1.0) + cells(226, 40, ['94.5', '63', '31.5'], 'green', 40) + cells(30, 80, ['90', '60', '30'], 'card', 50) + arrow(190, 89, 220, 89, 'ink3', 1.0) + opbox(226, 80, 'sum 180', '', 'green', 100, 18) + cap('transform and aggregate, one row.', '', 'green', y=144, h=30),
    t(180, 14, 'One row per element', 9.4, bold=True) + cells(20, 40, ['9102: Dosa, Idli, Coffee'], 'blue', 150) + ''.join(cells(220, 30 + k * 22, [d], 'green', 90) for k, d in enumerate(['Dosa', 'Idli', 'Coffee'])) + cells(20, 100, ['9103: [ ]'], 'card', 150) + t(230, 112, 'explode: gone', 7.0, 'red', anchor='start') + cap('explode_outer keeps empty lists.', '', 'amber', y=144, h=30),
    t(180, 14, 'Keys and fields', 9.4, bold=True) + opbox(30, 40, 'notes MAP', 'spice → high', 'violet', 130, 30) + opbox(200, 40, 'rider STRUCT', 'name, rating', 'blue', 130, 30) + cap('Missing key or null struct → null.', '', 'blue', y=144, h=30),
    t(180, 14, 'Schema mismatch kills the record', 9.4, bold=True) + opbox(20, 46, '{"order_id": "3",', '"items": "none"}', 'card', 140, 34) + arrow(160, 63, 200, 63, 'ink3', 1.0) + opbox(204, 46, 'from_json', 'all NULL', 'acc', 120, 34) + cap('One bad field, whole row lost.', '', 'red', y=144, h=30),
    t(180, 14, 'Extract field by field', 9.4, bold=True) + opbox(20, 46, 'VARIANT', 'binary, any shape', 'violet', 110, 34) + ''.join(arrow(130, 63, 196, 40 + k * 26, 'ink3', 1.0) + opbox(200, 30 + k * 26, ['order_id → 3', 'items → error / NULL', 'coupon → NULL'][k], '', ['green', 'acc', 'card'][k], 140, 20) for k in range(3)) + cap('Parse once; reads are fast.', '', 'green', y=144, h=30),
]
see_caps = ['Prices changed without exploding.', 'Empty order lost by explode.', 'Map by key, struct by field.', 'from_json nulled a whole record.', 'VARIANT kept what it could.']
behind_caps = ['Higher-order functions run in the JVM.', 'explode multiplies and drops.', 'Complex types nest freely.', 'PERMISSIVE: mismatch → null record.', 'Each path extracted on its own.']
two = anim_two('Complex data and VARIANT', 'Nested values, changing payloads', 'Real lab outputs', 'Inside the column', see, B1, see_caps, behind_caps)

# ---- scenario 1: payload change
e1 = (t(180, 22, 'App release 8.2', 9.4, bold=True) + t(180, 56, '"items": "none" when the cart is empty', 8.2, 'ink2') + cap('Nobody told the data team.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'from_json → NULL records', 9.4, bold=True) + t(180, 56, 'order ids lost too', 8.4, 'ink2') + cap('Orders vanish from reports.', '', 'red', y=150, h=34))
e3 = (t(180, 22, 'Land as VARIANT', 9.4, bold=True) + t(180, 56, 'parse_json(payload) in bronze', 8.4, 'ink', mono=True) + cap('Nothing is lost on ingest.', '', 'green', y=150, h=34))
e4 = (t(180, 22, 'try_variant_get per field', 9.4, bold=True) + t(180, 56, 'bad fields → null, others kept', 8.4, 'ink2') + cap('Like our Step 5.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Alert on unexpected types', 9.4, 'acc', bold=True) + t(180, 56, 'schema_of_variant drift check', 8.4, 'ink2') + cap('Talk to the app team.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'An app release broke the pipeline',
              'Fixed schemas vs VARIANT. (Behaviour from our lab.)',
              'Payload drift', 'from_json nulls whole records on mismatch; VARIANT with try_variant_get keeps every field that can be read', [e1, e2, e3, e4, e5],
              ['Release.', 'Null records.', 'VARIANT.', 'Per field.', 'Drift alert.'],
              hid='scenario-variant')

# ---- scenario 2: explode then re-aggregate
b1 = (t(180, 22, 'Order value from item list', 9.4, bold=True) + t(180, 56, 'explode items → sum → groupBy order', 8.2, 'ink2') + cap('Shuffle of 5x rows.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'Empty carts disappear', 9.4, bold=True) + t(180, 56, 'explode drops them', 8.4, 'ink2') + cap('Counts drop.', '', 'red', y=150, h=34))
b3 = (t(180, 22, 'aggregate() instead', 9.4, bold=True) + t(180, 56, 'aggregate(items, 0, (a, i) -> a + i.qty * i.price)', 7.6, 'ink', mono=True) + cap('One row per order.', '', 'green', y=150, h=34))
b4 = (t(180, 22, 'No shuffle needed', 9.4, bold=True) + t(180, 56, 'computed inside each row', 8.4, 'ink2') + cap('Faster and correct.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Explode when you need rows', 9.4, 'acc', bold=True) + t(180, 56, 'dish-level analytics', 8.4, 'ink2') + cap('explode_outer for safety.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Explode, sum, group back',
              'Higher-order functions vs explode. (Typical.)',
              'explode vs aggregate', 'Per-row calculations over arrays need no explode or shuffle; aggregate/transform keep rows intact', [b1, b2, b3, b4, b5],
              ['Explode.', 'Lost rows.', 'aggregate.', 'No shuffle.', 'When to explode.'],
              hid='scenario-hof')

# ---- scenario 3: JSON text everywhere
u1 = (t(180, 22, 'Analysts query raw JSON text', 9.4, bold=True) + t(180, 56, 'get_json_object in every dashboard', 8.2, 'ink2') + cap('Slow, repeated parsing.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'Every query parses all text', 9.4, bold=True) + t(180, 56, '~2 s per 1M rows in our lab', 8.4, 'ink2') + cap('Multiplied by dashboards.', '', 'amber', y=150, h=34))
u3 = (t(180, 22, 'Parse once into VARIANT', 9.4, bold=True) + t(180, 56, 'write table(v VARIANT)', 8.4, 'ink', mono=True) + cap('Binary, path-addressable.', '', 'green', y=150, h=34))
u4 = (t(180, 22, '0.62 s per field read', 9.4, bold=True) + t(180, 56, 'our Step 6', 8.4, 'ink2') + cap('Fast enough for BI.', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'Promote hot fields', 9.4, 'acc', bold=True) + t(180, 56, 'common fields as typed columns', 8.4, 'ink2') + cap('Best of both.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Parsing the same JSON a thousand times',
              'Storing semi-structured data. (Timings from our lab.)',
              'VARIANT storage', 'Parsing JSON text on every query is slow; store VARIANT once and extract fields cheaply, promoting hot fields to columns', [u1, u2, u3, u4, u5],
              ['Raw text.', 'Parse cost.', 'VARIANT table.', 'Fast reads.', 'Promote.'],
              hid='scenario-json-text')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Nested values, changing payloads</h2>
  <p>Left: real outputs. Right: what happens inside the column.</p>
''' + two + '''
  <p>Three live scenarios follow: an app release that broke parsing, explode-and-regroup, and JSON parsed a thousand times.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Complex data at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'events', 11, 'blue', bold=True) + t(60, 58, 'VARIANT', 7.4, 'ink2'),
    '1. App and web events',
    'Event payloads land as VARIANT; common fields are promoted to columns for dashboards.',
    ['Payload', '*parse_json', 'Event table']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'cart', 12, 'green', bold=True) + t(60, 58, 'arrays', 7.4, 'ink2'),
    '2. Shopping carts',
    'Order totals, item counts and “contains a dessert?” flags are computed with aggregate and exists.',
    ['Items array', '*aggregate / exists', 'Order metrics']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'tags', 12, 'violet', bold=True) + t(60, 58, 'maps', 7.4, 'ink2'),
    '3. Attributes and tags',
    'Restaurant attributes stored as maps let new attributes appear without schema changes.',
    ['Attributes', '*MAP&lt;string,string&gt;', 'Flexible']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'API', 12, 'acc', bold=True) + t(60, 58, 'responses', 7.4, 'ink2'),
    '4. Third-party API data',
    'Partner API responses with deep nesting are flattened with struct access and explode_outer.',
    ['API JSON', '*from_json + explode', 'Tables']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'export', 11, 'acc', bold=True) + t(60, 58, 'to_json', 7.4, 'ink2'),
    '5. Sending nested data out',
    'Results are packed with struct and to_json into messages for Kafka or APIs.',
    ['Columns', '*to_json(struct)', 'Messages']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> nested schemas in <a href="../../04-dataframes/02-creating-dataframes-and-schemas/">4.2</a>, JSON reading in <a href="../../05-reading-and-writing-data/01-csv-and-json/">5.1</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
