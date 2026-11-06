import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()
def err(n):
    return capf(n).split('; Query ID')[0]

# ---------------------------------------------------------------- story
sc = (box(10, 12, 300, 128, 'card') + t(160, 30, 'App events: one JSON document per line', 8.6, bold=True) +
      t(24, 54, '{"event":"order_placed",', 7.8, 'ink', anchor='start', mono=True) + t(24, 70, ' "user":{"id":1376,"city":"Chennai"},', 7.8, 'ink', anchor='start', mono=True) +
      t(24, 86, ' "items":[{"dish":"Rajma Chawal",', 7.8, 'ink', anchor='start', mono=True) + t(24, 102, '           "qty":3,"price":120}, …]}', 7.8, 'ink', anchor='start', mono=True) +
      t(160, 128, '1 of 2,000 lines is cut off', 7.8, 'red') +
      arrow(316, 76, 330, 76, 'ink3', 2) +
      box(334, 12, 300, 128, 'green') + t(484, 30, 'Columns you can GROUP BY', 8.8, 'green', bold=True) +
      ''.join(t(348, 54 + k * 18, s, 7.8, 'ink', anchor='start', mono=True) for k, s in enumerate(['event  user_id  city', 'order_placed  1376  Chennai', 'dish  qty  price', 'Rajma Chawal  3  120'])))
scene_svg = scene('A JSON app event with nested user and items on the left; on the right the same data as typed columns that can be grouped and summed.', sc,
                  'Hive reads JSON <tspan font-weight="700" class="s-acc">at query time</tspan> (functions) or <tspan font-weight="700" class="s-acc">through a SerDe</tspan> (typed table).')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“The app team sends us JSON. Can Hive read it?”</h2>
  <div class="story">
    <p class="narration">TiffinGo’s mobile app writes every action as a JSON line: app opens, searches, coupons and orders. Each order event has a nested <code>user</code> object and an <code>items</code> list with dish, quantity and price. The product team wants revenue per city and the order rate on Android vs iOS. One upload was cut off half-way, so one line is broken JSON.</p>

{scene_svg}

K> Sir, the file is 2,000 lines of JSON. Do I need to convert it to CSV first?
A> No. There are two ways. Keep each line as one STRING column and pull fields out at query time with <code>get_json_object</code> or <code>json_tuple</code>. Or define a typed table with the <b>JsonSerDe</b>, where nested objects become STRUCT and lists become ARRAY columns.
R> And the broken line?
A> That is where the two ways differ, and we will see it fail for real. Today: path syntax and its limits, json_tuple, JsonSerDe, quarantining bad lines, turning JSON into an ORC table, and a quick look at URLs and XML. All outputs are real.
  </div>
</section>
'''

lv = '''
LEVELS> JSON in Hive at three levels
L1> A form with boxes inside boxes
      <ul>
        <li>JSON stores data as <b>name: value</b> pairs. A value can be another object (<code>"user": {"id": 1376}</code>) or a list (<code>"items": [ … ]</code>).</li>
        <li>To read a value you give its <b>path</b>: <code>$.user.city</code> means “start at the top, open user, take city”.</li>
        <li>Hive can read the path in a query, or read the whole file as a table whose columns follow the JSON.</li>
      </ul>
L2> Three tools
      <ul>
        <li><code>get_json_object(json, '$.path')</code>: one value per call; supports <code>.key</code>, <code>[index]</code> and <code>[*]</code>; returns a STRING (lists come back as JSON text).</li>
        <li><code>json_tuple(json, 'k1', 'k2', …)</code>: several top-level keys in one parse, used with LATERAL VIEW; nested objects need a second json_tuple.</li>
        <li><b>JsonSerDe</b> (<code>org.apache.hive.hcatalog.data.JsonSerDe</code>): a table definition where each JSON field is a typed column, including STRUCT and ARRAY&lt;STRUCT&gt;.</li>
        <li>Missing keys, wrong case and broken JSON all give <b>NULL</b> with the functions.</li>
      </ul>
L3> Production choices
      <ul>
        <li><b>Parse once.</b> Functions re-parse the JSON text for every call and every query. Land raw JSON, then build a typed ORC table (CTAS) and query that.</li>
        <li><b>Schema on read is strict with the SerDe:</b> one malformed line made a full scan of the JsonSerDe table fail (JsonEOFException). Quarantine bad lines first using a raw STRING table.</li>
        <li><b>Path limits</b> (official docs): no recursive <code>..</code>, no filters <code>?()</code>, no slices or unions; keys with special characters are a problem.</li>
        <li><b>Reserved words:</b> a JSON key such as <code>user</code> needs back-ticks as a column name.</li>
        <li><b>Hive 4 additions</b> listed by <code>SHOW FUNCTIONS LIKE '%json%'</code>: <code>json_read(json, type)</code> parses into a typed value, plus <code>parse_json</code>, <code>to_json</code> and <code>variant_get</code> for the VARIANT type. In our Docker lab json_read worked in a quick fetch query but failed inside a Tez job (a Java 17 module-access error), so test new functions on your cluster before building pipelines on them.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Semi-structured data in Hive</h2>
''' + def_block(
    '<b>Semi-structured data</b> carries its own structure in the data itself (field names, nesting, optional fields), as in JSON or XML, rather than in a fixed table schema. Hive handles it in two ways: <b>schema-on-read functions</b> that parse a string column at query time (<code>get_json_object</code>, <code>json_tuple</code>, <code>xpath</code>, <code>parse_url_tuple</code>), and <b>SerDes</b> that map each record to typed columns when the table is read (JsonSerDe, including nested STRUCT and ARRAY types).',
    'JSON is text that describes itself: each value has a name, and values can sit inside other values. Hive can either look up one value at a time from the text, or read the text as a proper table with columns.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('JSON Lines', 'One complete JSON document per line. The format Hive tables expect.'),
    ('JSONPath', 'A path like <code>$.items[0].dish</code>. <code>$</code> is the root.'),
    ('get_json_object', 'Returns one value at a path, as a STRING.'),
    ('json_tuple', 'Returns several top-level values in one parse (a UDTF).'),
    ('JsonSerDe', 'Reads each JSON line into typed columns.'),
    ('Quarantine', 'Moving bad records aside so the good ones can load.'),
    ('xpath', 'Path language for XML: <code>/order/city</code>.'),
]) + '''

  <h3>get_json_object paths on a real event</h3>
''' + table(['Path', 'Real result', 'Note'], [
    ["<code>$.event</code>", 'order_placed', 'Top-level key'],
    ["<code>$.user.city</code>", 'Chennai', 'Nested object'],
    ["<code>$.items[0].dish</code>", 'Rajma Chawal', 'First list element'],
    ["<code>$.items[*].dish</code>", '["Rajma Chawal","Chai","Idli"]', 'JSON text, not a Hive array'],
    ["<code>$.User.id</code>", 'NULL', 'Keys are case-sensitive'],
    ["<code>$.items[9].dish</code>", 'NULL', 'No such element'],
    ["get_json_object('{\"a\":1', '$.a')", 'NULL', 'Broken JSON'],
], minw=600) + lv + '''
EXAM> “get_json_object vs json_tuple vs JsonSerDe.” get_json_object: one path per call, nested paths allowed, re-parses each call. json_tuple: many top-level keys in one parse with LATERAL VIEW, no nested paths. JsonSerDe: typed table with STRUCT/ARRAY columns; strict about malformed lines. Production: land raw, quarantine bad lines, CTAS into ORC.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Choosing a JSON approach</h2>
''' + table(['Approach', 'Strengths', 'Weaknesses', 'Use when'], [
    ['Raw STRING + <code>get_json_object</code>', 'No schema needed; nested paths; bad lines just give NULL', 'Parses again for every field and query; all results are STRING', 'Exploring, a few fields, messy sources'],
    ['Raw STRING + <code>json_tuple</code>', 'Several keys in one parse', 'Top-level keys only; needs LATERAL VIEW', 'Many flat fields'],
    ['JsonSerDe table', 'Typed columns, STRUCT and ARRAY, normal SQL', 'Malformed line fails the scan; schema must be maintained', 'Clean, stable feeds'],
    ['CTAS to ORC (from either)', 'Parse once, fast columnar reads, statistics', 'One more pipeline step', 'Anything queried repeatedly'],
], minw=760) + '''
  <h3>Other semi-structured helpers (real results)</h3>
''' + table(['Call', 'Real result'], [
    ["<code>parse_url('https://tiffingo.in/menu/pune?dish=poha&amp;src=ad', 'HOST')</code>", 'tiffingo.in'],
    ["<code>parse_url(…, 'QUERY', 'src')</code>", 'ad'],
    ["<code>parse_url_tuple(…, 'HOST', 'PATH', 'QUERY:dish')</code>", 'tiffingo.in · /menu/pune · poha'],
    ["<code>xpath_string('&lt;order&gt;…&lt;city&gt;Pune&lt;/city&gt;…', '/order/city')</code>", 'Pune'],
    ["<code>xpath(xml, '/order/dish/text()')</code>", '["Poha","Chai"]'],
], minw=640) + '''
WARN> A single malformed line can stop a whole JsonSerDe query. In our lab <code>LIMIT 3</code> on the SerDe table worked (it read only the first lines), but <code>COUNT(*)</code> failed on line 1,500 with a JsonEOFException. Validate or quarantine raw files before pointing a typed table at them.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>From raw app events to revenue per city</h2>
  <p>All outputs are real, from the Hive 4.2.1 lab (2,000 generated events, one deliberately truncated).</p>
''' + stepper([
    ('Step 1 · Land the raw JSON as one STRING column',
     code('sql', 'Beeline', "CREATE EXTERNAL TABLE events_raw (line STRING) LOCATION '/data/events';\nSELECT COUNT(*) AS lines FROM events_raw;\nSELECT line FROM events_raw LIMIT 1;", capf('l43_setup.txt')),
     'With the default text format, each line becomes one row, whatever it contains. Nothing can fail at this stage.'),
    ('Step 2 · Pull fields with get_json_object',
     code('sql', 'Beeline', "SELECT get_json_object(line, '$.event') AS event,\n  get_json_object(line, '$.user.id') AS user_id,\n  get_json_object(line, '$.user.city') AS city,\n  get_json_object(line, '$.items[0].dish') AS first_dish,\n  get_json_object(line, '$.items[*].dish') AS all_dishes,\n  get_json_object(line, '$.coupon') AS coupon\nFROM events_raw LIMIT 3;", capf('l43_gjo.txt')),
     'Nested paths and list indexes work. Fields that an event does not have (items on app_open, coupon on orders) come back NULL. <code>[*]</code> returns JSON text, not a Hive array.'),
    ('Step 3 · Traps: case, lists as text, broken JSON',
     code('sql', 'Beeline', "SELECT get_json_object(line, '$.User.id') AS wrong_case,\n  get_json_object(line, '$.items') AS items_text,\n  get_json_object('{\"a\":1', '$.a') AS broken,\n  get_json_object(line, '$.items[9].dish') AS no_item\nFROM events_raw WHERE get_json_object(line, '$.event') = 'order_placed' LIMIT 1;", capf('l43_gjo_traps.txt')),
     'All silent: a wrong-case key, a missing element and invalid JSON all return NULL. The items list comes back as a plain string.'),
    ('Step 4 · Find the bad line',
     code('sql', 'Beeline', "SELECT COUNT(*) AS lines, COUNT(get_json_object(line, '$.event')) AS parsed,\n  SUM(IF(get_json_object(line, '$.event') IS NULL, 1, 0)) AS unparsed\nFROM events_raw;\n\nSELECT get_json_object(line, '$.event') AS event, COUNT(*) AS n\nFROM events_raw GROUP BY get_json_object(line, '$.event') ORDER BY n DESC;",
          capf('l43_bad.txt') + '\n' + capf('l43_events.txt')),
     'One line could not be parsed. With functions it only shows up as a NULL group, which is easy to miss unless you count it.'),
    ('Step 5 · json_tuple: several keys in one parse',
     code('sql', 'Beeline', "SELECT j.event, j.ts, u.id, u.city\nFROM events_raw r\nLATERAL VIEW json_tuple(r.line, 'event', 'ts', 'user') j AS event, ts, user_json\nLATERAL VIEW json_tuple(j.user_json, 'id', 'city') u AS id, city\nLIMIT 3;\n\nSELECT j.user_json FROM events_raw r\nLATERAL VIEW json_tuple(r.line, 'user') j AS user_json LIMIT 1;\nSELECT j.uid FROM events_raw r\nLATERAL VIEW json_tuple(r.line, 'user.id') j AS uid LIMIT 1;",
          capf('l43_jt.txt') + '\n' + capf('l43_jt_nested.txt')),
     'json_tuple takes key names, not paths. The nested user object comes back as JSON text, so a second json_tuple opens it. A dotted key like <code>user.id</code> just returns NULL.'),
    ('Step 6 · A typed JsonSerDe table, and how one bad line breaks it',
     code('sql', 'Beeline', "CREATE EXTERNAL TABLE events_json (\n  event STRING, ts STRING,\n  `user` STRUCT<id:INT, city:STRING>,\n  device STRUCT<os:STRING, app_ver:STRING>,\n  items ARRAY<STRUCT<dish:STRING, qty:INT, price:INT>>,\n  coupon STRING, query STRING)\nROW FORMAT SERDE 'org.apache.hive.hcatalog.data.JsonSerDe'\nLOCATION '/data/events';\n\nSELECT event, `user`.city AS city, size(items) AS n_items FROM events_json LIMIT 3;\nSELECT COUNT(*) AS n FROM events_json WHERE event = 'order_placed';",
          capf('l43_serde.txt') + '\nError: … TezTask. Vertex failed … Hive Runtime Error while processing row\n(root cause in the HiveServer2 log)\nSerDeException: … JsonEOFException: Unexpected end-of-input in field name'),
     'The first three lines read fine (size is -1 where there is no items list). The full scan fails when it reaches the truncated line. <code>user</code> is a reserved word, so it needs back-ticks: without them the query fails with “cannot recognize input near \'user\' \'.\' \'city\'”.'),
    ('Step 7 · Quarantine bad lines, then parse once into ORC',
     code('sql', 'Beeline', "INSERT OVERWRITE DIRECTORY '/data/events_good'\nSELECT line FROM events_raw WHERE get_json_object(line, '$.event') IS NOT NULL;\nINSERT OVERWRITE DIRECTORY '/data/events_bad'\nSELECT line FROM events_raw WHERE get_json_object(line, '$.event') IS NULL;\n-- recreate events_json with LOCATION '/data/events_good'\nSELECT COUNT(*) AS n FROM events_json;\n\nCREATE TABLE events_clean STORED AS ORC AS\nSELECT event, CAST(substr(ts, 1, 10) AS DATE) AS event_date,\n       `user`.id AS user_id, `user`.city AS city, device.os AS os, items, coupon\nFROM events_json;\nDESCRIBE events_clean;",
          capf('l43_quarantine.txt') + '\n' + capf('l43_ctas.txt')),
     'The raw STRING table acts as a safety net: good lines go to one folder, the single bad line to another for investigation. The typed ORC table keeps <code>items</code> as an array of structs, so it is parsed once and queried many times.'),
    ('Step 8 · Answer the product team',
     code('sql', 'Beeline', "SELECT city, COUNT(DISTINCT user_id) AS buyers, SUM(it.qty * it.price) AS revenue\nFROM events_clean LATERAL VIEW inline(items) it\nWHERE event = 'order_placed'\nGROUP BY city ORDER BY revenue DESC;\n\nSELECT os, COUNT(*) AS events, SUM(IF(event = 'order_placed', 1, 0)) AS orders,\n  ROUND(100 * SUM(IF(event = 'order_placed', 1, 0)) / COUNT(*), 1) AS order_pct\nFROM events_clean GROUP BY os;",
          capf('l43_revenue.txt') + '\n' + capf('l43_os.txt')),
     '<code>inline</code> (Lesson 4.2) turns each item struct into dish, qty and price columns. iOS events turned into orders slightly more often (40.8% vs 38.1%) in this generated data.'),
    ('Step 9 · URLs and XML',
     code('sql', 'Beeline', "SELECT parse_url('https://tiffingo.in/menu/pune?dish=poha&src=ad', 'HOST') AS host,\n  parse_url('https://tiffingo.in/menu/pune?dish=poha&src=ad', 'QUERY', 'src') AS src;\nSELECT t.* FROM (SELECT 1) x LATERAL VIEW parse_url_tuple(\n  'https://tiffingo.in/menu/pune?dish=poha&src=ad', 'HOST', 'PATH', 'QUERY:dish') t AS host, path, dish;\n\nSELECT xpath_string('<order><id>100001</id><city>Pune</city>…</order>', '/order/city') AS city,\n  xpath_int('<order><id>100001</id></order>', '/order/id') AS id,\n  xpath('<order><dish>Poha</dish><dish>Chai</dish></order>', '/order/dish/text()') AS dishes;",
          capf('l43_url.txt') + '\n' + capf('l43_xml.txt')),
     'parse_url and parse_url_tuple split web links into host, path and query parameters, useful for campaign tracking. The xpath family reads XML stored in a string column; <code>xpath</code> returns an array of all matches.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([("> SELECT get_json_object(line, '$.user.city')", W), ('| Chennai |', G), ('| Chennai |', G), ('| Delhi   |', G)]),
    term([("> … '$.items[0].dish', '$.items[*].dish'", W), ('| Rajma Chawal | ["Rajma Chawal","Chai","Idli"] |', G), ('| Poha         | ["Poha","Idli"]                |', G)]),
    term([("> … json_tuple(r.line, 'event','ts','user') j", W), ("  … json_tuple(j.user_json, 'id','city') u", W), ('| order_placed | … | 1376 | Chennai |', G), ('| order_placed | … | 1279 | Delhi   |', G)]),
    term([('> SELECT COUNT(*) FROM events_json …', W), ('Error: Vertex failed … processing row', RD), ('  JsonEOFException: Unexpected', RD), ('  end-of-input in field name', RD)]),
    term([('> CREATE TABLE events_clean STORED AS ORC AS …', W), ('| items | array<struct<dish:string,', G), ('|       |   qty:int,price:int>>      |', G), ('> … LATERAL VIEW inline(items) it …', W), ('| Chennai | 119 | 39330 |', G)]),
]
def jtree(hl):
    nodes = [('$', 180, 46), ('event', 70, 82), ('user', 180, 82), ('items[ ]', 290, 82), ('id', 110, 118), ('city', 180, 118), ('[0].dish', 254, 118), ('[1].dish', 324, 118)]
    o = arrow(170, 54, 80, 72, 'ink3', 1.2) + arrow(180, 54, 180, 72, 'ink3', 1.2) + arrow(190, 54, 286, 72, 'ink3', 1.2) + arrow(174, 90, 116, 108, 'ink3', 1.2) + arrow(180, 90, 180, 108, 'ink3', 1.2) + arrow(284, 90, 258, 108, 'ink3', 1.2) + arrow(296, 90, 320, 108, 'ink3', 1.2)
    for name, x, y in nodes:
        on = name in hl
        o += box(x - 31, y - 10, 62, 18, 'acc' if on else 'card', rx=4) + t(x, y + 3, name, 7.6, 'ink', mono=True, bold=on)
    return o
B1 = [
    t(180, 22, 'A path walks the tree', 9.4, bold=True) + jtree({'$', 'user', 'city'}) + cap('$.user.city → Chennai', '', 'blue', y=150, h=34),
    t(180, 22, 'Index one element, or [*] for all', 9.4, bold=True) + jtree({'$', 'items[ ]', '[0].dish', '[1].dish'}) + cap('[*] returns JSON text: ["Rajma Chawal","Chai",…]', '', 'blue', y=150, h=34),
    t(180, 22, 'json_tuple opens one level per call', 9.4, bold=True) + jtree({'$', 'event', 'user', 'id', 'city'}) + cap('First call: event, user. Second call: id, city.', '', 'green', y=150, h=34),
    t(180, 22, 'SerDe reads every line strictly', 9.4, bold=True) + ''.join(box(30 + k * 62, 58, 54, 26, 'red' if k == 3 else 'green', rx=4) + t(57 + k * 62, 75, s, 7.6, 'ink', mono=True) for k, s in enumerate(['1', '2', '…', '1500', '2000'])) + t(180, 112, 'line 1500 is cut off → the whole task fails', 8.2, 'red') + cap('Functions return NULL; the SerDe stops.', '', 'amber', y=150, h=34),
    t(180, 22, 'Parse once, query many times', 9.4, bold=True) + ''.join(box(20 + k * 112, 60, 96, 30, tone, rx=5) + t(68 + k * 112, 79, s, 7.8, 'ink', bold=True) for k, (s, tone) in enumerate([('raw STRING', 'card'), ('good / bad', 'amber'), ('ORC typed', 'green')])) + arrow(118, 75, 130, 75, 'ink3', 1.6) + arrow(230, 75, 242, 75, 'ink3', 1.6) + cap('Quarantine, then CTAS into ORC.', '', 'green', y=150, h=34),
]
see_caps = ['get_json_object reads a nested field.',
            'An index picks one list element; [*] returns all of them as JSON text.',
            'Two json_tuple calls read the top level, then the nested user object.',
            'A full scan of the JsonSerDe table fails on the truncated line.',
            'The cleaned data is stored once as typed ORC and queried with inline.']
behind_caps = ['The path starts at the root ($) and follows keys down the tree.',
               'Array positions start at 0; [*] collects every element.',
               'json_tuple only reads one level, so nested objects need another call.',
               'The SerDe must parse every line into columns; one broken line stops the task.',
               'Raw data is split into good and bad lines, then converted once to ORC.']
two = anim_two('JSON', 'Paths, tuples and SerDes', 'Real Beeline output', 'Which part of the JSON tree is read', see, B1, see_caps, behind_caps)

# ---- scenario 1: broken line
b1 = (t(180, 22, 'Nightly job failed at 2 a.m.', 9.4, 'red', bold=True) + t(180, 56, 'Vertex failed … JsonEOFException', 8.4, 'ink', mono=True) + cap('One partial upload, whole job down.', '', 'amber', y=150, h=34))
b2 = (t(180, 22, 'Find the culprit with the raw table', 9.4, bold=True) + t(180, 56, "WHERE get_json_object(line, '$.event') IS NULL", 8.2, 'ink', mono=True) + t(180, 78, '→ 1 line of 2,000 (real)', 8.6, 'red', bold=True, mono=True) + cap('NULL from get_json_object marks unparsable lines.', '', 'blue', y=150, h=34))
b3 = (t(180, 22, 'Quarantine', 9.6, bold=True) + t(180, 56, "good lines → /data/events_good (1,999)", 8.4, 'green', mono=True) + t(180, 76, "bad lines  → /data/events_bad  (1)", 8.4, 'red', mono=True) + cap('The pipeline continues; bad data is kept for review.', '', 'green', y=150, h=34))
b4 = term([('> SELECT COUNT(*) AS n FROM events_json;', W), ('| 1999 |', G)], label='real output · Hive 4.2.1')
b5 = (t(180, 22, 'Add a data-quality metric', 9.6, 'acc', bold=True) + t(180, 56, 'bad_lines / total_lines per day; alert above 0.1%', 8.4, 'ink2') + cap('Bad data is expected; silent failure is not.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'One truncated line stops the nightly job',
              'A partial upload left one broken JSON line. The counts and errors are real.',
              'Bad records', 'A truncated JSON line failed the SerDe scan; the raw table found it and quarantine let the pipeline continue', [b1, b2, b3, b4, b5],
              ['The typed table failed on a broken line.',
               'The raw STRING table finds lines that do not parse.',
               'Good and bad lines go to separate folders.',
               'The typed table over the good folder reads all 1,999 events.',
               'Track the bad-line rate as a quality metric.'],
              hid='scenario-badline')

# ---- scenario 2: parse once
p1 = (t(180, 22, 'Dashboard on raw JSON is slow', 9.4, bold=True) + t(180, 56, '6 × get_json_object per row, every refresh', 8.4, 'ink', mono=True) + cap('Each call parses the whole line again.', '', 'amber', y=150, h=34))
p2 = (t(180, 22, 'Parse once with CTAS', 9.6, bold=True) + t(180, 56, 'CREATE TABLE events_clean STORED AS ORC AS …', 8.4, 'ink', mono=True) + cap('Typed columns, compression, statistics.', '', 'green', y=150, h=34))
p3 = (t(180, 22, 'Columnar reads', 9.6, bold=True) + t(180, 56, 'a query on city reads only the city column', 8.4, 'ink2') + t(180, 76, '(raw JSON must read and parse every byte)', 8.2, 'ink2') + cap('ORC is covered in Module 6.', '', 'blue', y=150, h=34))
p4 = term([('> SELECT os, COUNT(*), … FROM events_clean GROUP BY os;', W), ('| Android | 1334 | 508 | 38.1 |', G), ('| iOS     | 665  | 271 | 40.8 |', G)], label='real output · Hive 4.2.1')
p5 = (t(180, 22, 'Pattern', 9.6, 'acc', bold=True) + t(180, 56, 'raw (keep forever) → clean ORC (rebuildable) → reports', 8.2, 'ink2') + cap('Bronze → silver → gold, in lakehouse terms.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Parse JSON once, not on every query',
              'Turning a raw JSON table into a typed ORC table. Query results are real; the speed remarks are general guidance.',
              'Parse once', 'Raw JSON parsed by functions on every query is converted once into an ORC table with typed columns', [p1, p2, p3, p4, p5],
              ['Functions re-parse JSON every time a dashboard refreshes.',
               'CTAS writes typed columns into ORC once.',
               'Columnar files let queries read only needed columns.',
               'Reports run on the clean table.',
               'Keep raw data, rebuild clean tables when logic changes.'],
              hid='scenario-parse-once')

# ---- scenario 3: schema drift
d1 = (t(180, 22, 'App 5.4 adds a field', 9.6, bold=True) + t(180, 56, '"payment":{"mode":"UPI","wallet":"none"}', 8.4, 'ink', mono=True) + cap('Old table definitions do not know it.', '', 'blue', y=150, h=34))
d2 = (t(180, 22, 'JsonSerDe ignores unknown keys', 9.6, 'green', bold=True) + t(180, 56, 'queries keep working; payment is just not visible', 8.4, 'ink2') + cap('Add the column with ALTER TABLE … ADD COLUMNS.', '', 'green', y=150, h=34))
d3 = (t(180, 22, 'Missing keys → NULL', 9.6, bold=True) + t(180, 56, 'old events have no payment: NULL, not an error', 8.4, 'ink2') + cap('Like coupon on order events in our data.', '', 'blue', y=150, h=34))
d4 = (t(180, 22, 'Type changes are dangerous', 9.6, 'red', bold=True) + t(180, 56, '"price": 120  →  "price": "120.00"', 8.4, 'ink', mono=True) + cap('Check types in the quarantine step too.', '', 'amber', y=150, h=34))
d5 = (t(180, 22, 'Contract with the app team', 9.6, 'acc', bold=True) + ''.join(t(26, 52 + k * 19, s, 8.4, anchor='start') for k, s in enumerate(['• version field in every event', '• additive changes only', '• schema registry or shared JSON Schema'])) + cap('Agree changes before they ship.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'When the JSON changes shape',
              'Apps evolve and so do their events. A plan for new, missing and changed fields. (Guidance; the NULL behaviour matches our lab.)',
              'Schema drift', 'New JSON keys are ignored until added, missing keys give NULL, and type changes need checks and an agreed contract', [d1, d2, d3, d4, d5],
              ['A new app version adds a nested payment object.',
               'The SerDe ignores keys that are not columns; add them when needed.',
               'Older events without the key show NULL.',
               'Changed types are the real risk; validate them.',
               'Agree an event contract with the producers.'],
              hid='scenario-drift')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Reading the JSON tree</h2>
  <p>Left: real Beeline output. Right: which part of the JSON is read.</p>
''' + two + '''
  <p>Three live scenarios follow: a broken line, parsing once, and changing JSON.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>JSON and semi-structured data at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'events', 10, 'green', bold=True) + t(60, 58, 'clickstream', 7.4, 'ink2'),
    '1. App and web clickstream',
    'Mobile apps and websites send JSON events; Hive tables over the landing folders feed funnels, retention and A/B test reports.',
    ['JSON events', '*Raw → ORC', 'Funnels']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'API', 10, 'blue', bold=True) + t(60, 58, 'payloads', 7.4, 'ink2'),
    '2. API and payment logs',
    'Payment gateways and partner APIs return JSON responses that are stored as-is for audit and parsed into tables for reconciliation.',
    ['API responses', '*get_json_object', 'Reconciliation']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'IoT', 10, 'violet', bold=True) + t(60, 58, 'sensors', 7.4, 'ink2'),
    '3. Device telemetry',
    'Delivery bikes, smart meters and machines send nested JSON readings; SerDe tables with STRUCT columns make them queryable.',
    ['Telemetry', '*JsonSerDe', 'Health dashboards']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'UTM', 10, 'acc', bold=True, mono=True) + t(60, 58, 'campaigns', 7.4, 'ink2'),
    '4. Campaign tracking',
    'parse_url_tuple extracts utm_source and utm_campaign from landing-page URLs to attribute orders to ads.',
    ['Page URLs', '*parse_url_tuple', 'Attribution']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'XML', 10, 'acc', bold=True, mono=True) + t(60, 58, 'legacy feeds', 7.4, 'ink2'),
    '5. Legacy XML feeds',
    'Banks and government systems still exchange XML; xpath functions read fields from XML strings during migration to modern formats.',
    ['XML files', '*xpath_string', 'Tables']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> you need SerDes (<a href="../../02-hiveql/04-row-formats-and-serdes/">2.4</a>) and LATERAL VIEW (<a href="../02-explode-and-lateral-view/">4.2</a>).</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
