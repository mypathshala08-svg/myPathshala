import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()

# ---------------------------------------------------------------- story
sc = (''.join(box(10, 14 + k * 42, 170, 36, 'card') + t(18, 28 + k * 42, a, 7.4, anchor='start', mono=True) + t(18, 41 + k * 42, b, 7.4, 'ink2', anchor='start', mono=True)
              for k, (a, b) in enumerate([('menu.csv', '1,"Dal, Rice combo",120,…'), ('restaurants.json', '{"restaurant_id": 1, "tags": […]}'), ('access.log', '10.165.39.83 - - [01/Oct/2026…] "GET…')])) +
      ''.join(arrow(182, 32 + k * 42, 240, 76, 'ink3', 1.6) for k in range(3)) +
      box(242, 46, 140, 60, 'acc') + t(312, 66, 'SerDe', 10, bold=True) + t(312, 84, 'bytes ⇄ columns', 8, 'ink2') +
      arrow(384, 76, 424, 76, 'ink3', 2.2) + box(426, 30, 204, 92, 'green') + t(528, 48, 'Rows and typed columns', 8.8, bold=True) +
      ''.join(t(436, 66 + j * 14, s, 7.6, anchor='start', mono=True) for j, s in enumerate(['name: Dal, Rice combo', 'tags: ["jain","veg"]', 'status: 500  path: /checkout'])))
scene_svg = scene('A CSV file with quoted fields, a JSON file and a web server log each pass through a SerDe that turns their bytes into rows with typed columns.', sc,
                  'Three file shapes, one idea: a <tspan font-weight="700" class="s-acc">SerDe</tspan> decides how bytes become columns.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Why did ‘Dal, Rice combo’ break my menu table?”</h2>
  <div class="story">
    <p class="narration">The TiffinGo menu team exports a CSV. One dish is called <code>"Dal, Rice combo"</code>, with a comma inside quotes. Kabir’s table shows <code>"Dal</code> as the name, NULL as the price and <code>120</code> as the category. The restaurant data arrives as JSON, and the operations team wants to query the web server’s access log, where nothing is separated by commas at all.</p>

{scene_svg}

K> Sir, a comma is a comma. How is Hive supposed to know which commas are inside quotes?
A> It isn’t, unless you choose a reader that understands quotes. Every Hive table has a <b>SerDe</b>, short for <b>Ser</b>ializer/<b>De</b>serializer: the code that turns bytes into columns when reading and columns into bytes when writing. The default one splits on a character and knows nothing about quotes.
R> So there is a different SerDe for CSV, for JSON and for logs?
A> Exactly. <b>OpenCSVSerde</b> understands quotes, the <b>JsonSerDe</b> maps JSON keys to columns, and <b>RegexSerDe</b> cuts a line with a regular expression. Each has habits you must know: one returns every column as a string, one fails the whole query on a single broken line. We will hit each of them in the lab.
  </div>
</section>
'''

lv = '''
LEVELS> SerDes at three levels
L1> Translators at the door
      <ul>
        <li>Files speak different “languages”: CSV, JSON, log lines.</li>
        <li>A <b>SerDe</b> is the translator Hive puts at the door of a table. Reading: file language → rows and columns. Writing: rows → file language.</li>
        <li>Pick the wrong translator and Hive misunderstands: columns shift, values become NULL.</li>
      </ul>
L2> The SerDes you will use
      <ul>
        <li><b>LazySimpleSerDe</b> (the default for <code>ROW FORMAT DELIMITED</code>): splits on single characters; no quote handling; empty text stays an empty string; <code>\\N</code> means NULL.</li>
        <li><b>OpenCSVSerde</b>: handles quotes and escaped quotes; but it returns <b>every column as STRING</b>, whatever you declare.</li>
        <li><b>JsonSerDe</b> (<code>STORED AS JSONFILE</code>): one JSON object per line; nested objects map to STRUCT and MAP, lists to ARRAY; extra keys ignored, missing keys NULL.</li>
        <li><b>RegexSerDe</b>: one capturing group per column; lines that do not match give a row of NULLs.</li>
        <li>Binary formats (ORC, Parquet, Avro) have their own SerDes chosen by <code>STORED AS</code> (Module 6).</li>
      </ul>
L3> What the lab showed about edge cases (Hive 4.2.1)
      <ul>
        <li>OpenCSVSerde: <code>typeof(price)</code> was <code>string</code> although we declared INT; <code>SUM(price)</code> returned <code>395.0</code> (string → DOUBLE).</li>
        <li>JsonSerDe: one line with a missing <code>}</code> made the whole query fail with <code>JsonEOFException</code>. A string where an INT was expected gave <b>0</b>, not NULL. A key written <code>CITY</code> still matched column <code>city</code>.</li>
        <li>RegexSerDe: in HiveQL string literals a backslash must be doubled: write <code>\\\\S+</code> in the DDL to get the regex <code>\\S+</code>.</li>
        <li>LazySimpleSerDe: <code>serialization.null.format</code> changes the NULL marker (we set it to <code>NA</code>); an empty field is still <code>''</code>, not NULL.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Row formats and SerDes</h2>
''' + def_block(
    'A <b>SerDe</b> (Serializer/Deserializer) is the Hive component that converts between the bytes of a stored record and Hive’s row representation: the <b>deserializer</b> parses records into columns when data is read, and the <b>serializer</b> converts rows into records when data is written. A table’s <b>row format</b> names its SerDe and SerDe properties, either with the shorthand <code>ROW FORMAT DELIMITED …</code> (LazySimpleSerDe) or with <code>ROW FORMAT SERDE \'class\' WITH SERDEPROPERTIES (…)</code>; the <b>file format</b> (<code>STORED AS</code>) names the input and output formats that split files into records.',
    'The file format decides how a file is cut into records (usually lines). The SerDe decides how one record is cut into columns. Choose a SerDe that understands your file: delimited text, CSV with quotes, JSON, or a pattern for logs.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Serialize', 'Turn a row into bytes for writing to a file.'),
    ('Deserialize', 'Turn bytes from a file into a row with columns.'),
    ('InputFormat', 'Splits a file into records (for text: one record per line).'),
    ('SERDEPROPERTIES', 'Settings for a SerDe, such as separator, quote character or regex.'),
    ('LazySimpleSerDe', 'The default text SerDe. “Lazy” because it parses a column only when a query uses it.'),
    ('Quote character', 'Marks text that may contain the separator: <code>"Dal, Rice combo"</code>.'),
    ('Capturing group', 'A part of a regular expression in brackets; RegexSerDe maps group 1 to column 1, and so on.'),
    ('NULL marker', 'Text that means NULL in a file: <code>\\N</code> by default for delimited text.'),
]) + '''

  <h3>Where the SerDe sits in a table definition</h3>
''' + table(['Clause', 'Decides', 'Example'], [
    ['<code>ROW FORMAT DELIMITED FIELDS TERMINATED BY \',\'</code>', 'LazySimpleSerDe with simple separators', 'Plain CSV without quotes'],
    ["<code>ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'</code>", 'A named SerDe class', 'CSV with quotes'],
    ["<code>WITH SERDEPROPERTIES ('separatorChar'=',', 'quoteChar'='\"')</code>", 'Settings for that SerDe', 'Separator, quote, regex'],
    ['<code>STORED AS TEXTFILE | JSONFILE | ORC | PARQUET | AVRO</code>', 'Input/output format (and SerDe for binary formats)', '<code>STORED AS JSONFILE</code> sets the JsonSerDe too'],
    ["<code>TBLPROPERTIES ('serialization.null.format'='NA')</code>", 'How NULL is written in text', 'Exports that write NA for missing values'],
], minw=680) + lv + '''
EXAM> “What is a SerDe in Hive?” Expand the name, say it converts records to rows (deserialize, on read) and rows to records (serialize, on write), name the default <b>LazySimpleSerDe</b> and two others (<b>OpenCSVSerde</b>, <b>JsonSerDe</b>, <b>RegexSerDe</b>, ORC/Parquet/Avro SerDes), and show <code>ROW FORMAT SERDE … WITH SERDEPROPERTIES</code>.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Pick a SerDe for the file in front of you</h2>
''' + table(['File looks like', 'Use', 'Watch out for (seen in the lab)'], [
    ['<code>1,Poha,40,Breakfast</code> (no quotes)', '<code>ROW FORMAT DELIMITED</code> (LazySimpleSerDe)', 'A comma inside a value shifts columns'],
    ['<code>1,"Dal, Rice combo",120,Thali</code>', 'OpenCSVSerde', 'All columns come back as STRING; cast in queries or a curated table'],
    ['<code>{"restaurant_id": 1, "tags": ["veg"]}</code>', '<code>STORED AS JSONFILE</code> (JsonSerDe)', 'One malformed line fails the query; wrong-type values became 0'],
    ['<code>10.1.2.3 - - [01/Oct/2026:…] "GET /cart HTTP/1.1" 200 …</code>', 'RegexSerDe', 'Non-matching lines become all-NULL rows; double the backslashes'],
    ['<code>a|b|c</code> or tab-separated', "<code>DELIMITED FIELDS TERMINATED BY '|'</code> or <code>'\\t'</code>", 'Choose a separator that never appears in the data'],
    ['Multi-character separator <code>a||b</code>', 'MultiDelimitSerDe', 'Less common; check your version supports it'],
    ['Binary columnar files', '<code>STORED AS ORC / PARQUET</code>', 'Not human-readable; fastest for analytics (Module 6)'],
], minw=760) + cards([
    ('Keep raw, publish clean', 'Read awkward files with the SerDe they need in a raw table, then INSERT into an ORC table with proper types. Other queries never touch the awkward SerDe.', 'Best practice'),
    ('Fix at the source', 'Ask the producer for a safer format (JSON, Parquet, or a separator that cannot appear). Cheaper than clever SerDes forever.', 'Long term'),
    ('Custom SerDe', 'For truly unusual formats you can write a Java SerDe and add its JAR. Rarely needed today.', 'Advanced'),
]) + '''
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Four files, four SerDes</h2>
  <p>All outputs are real, from the Hive 4.2.1 lab. The files are in the course dataset.</p>
''' + stepper([
    ('Step 1 · The default SerDe meets quoted commas',
     code('sql', 'Beeline', "-- menu.csv:  1,\"Dal, Rice combo\",120,Thali\nCREATE EXTERNAL TABLE menu_naive (item_id INT, name STRING, price INT, category STRING)\nROW FORMAT DELIMITED FIELDS TERMINATED BY ','\nLOCATION 'file:///data/tiffingo/menu_csv'\nTBLPROPERTIES ('skip.header.line.count'='1');\nSELECT * FROM menu_naive;", capf('l24_csv.txt').split('+-------------------+')[0].rstrip()),
     'Row 1 is split at every comma: <code>"Dal</code> becomes the name, <code> Rice combo"</code> lands in price (NULL, not a number) and 120 lands in category. Row 3’s doubled quotes are kept literally.'),
    ('Step 2 · OpenCSVSerde understands quotes',
     code('sql', 'Beeline', "CREATE EXTERNAL TABLE menu_csv (item_id INT, name STRING, price INT, category STRING)\nROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'\nWITH SERDEPROPERTIES ('separatorChar'=',', 'quoteChar'='\"', 'escapeChar'='\\\\')\nLOCATION 'file:///data/tiffingo/menu_csv'\nTBLPROPERTIES ('skip.header.line.count'='1');\nSELECT * FROM menu_csv;", '+-------------------+-------------------------+-----------------+--------------------+\n| menu_csv.item_id  |      menu_csv.name      | menu_csv.price  | menu_csv.category  |\n+-------------------+-------------------------+-----------------+--------------------+\n| 1                 | Dal, Rice combo         | 120             | Thali              |\n| 2                 | Poha                    | 40              | Breakfast          |\n| 3                 | Paneer "Special" Thali  | 220             | Thali              |\n| 4                 | Masala Chai             | 15              | Beverage           |\n+-------------------+-------------------------+-----------------+--------------------+'),
     'The quoted comma stays inside the name, and <code>""Special""</code> becomes <code>"Special"</code>. Correct rows at last, but read on.'),
    ('Step 3 · The OpenCSVSerde surprise: everything is a string',
     code('sql', 'Beeline', 'SELECT SUM(price) AS total FROM menu_csv;\nSELECT typeof(price) AS t, price + 1 AS p1 FROM menu_csv LIMIT 1;',
          '+--------+\n| total  |\n+--------+\n| 395.0  |\n+--------+\n+---------+--------+\n|    t    |   p1   |\n+---------+--------+\n| string  | 121.0  |\n+---------+--------+'),
     'We declared <code>price INT</code>, yet the values arrive as strings, so arithmetic converts them to DOUBLE (395.0, 121.0). Cast explicitly (<code>CAST(price AS INT)</code>) or copy the data into a typed ORC table.'),
    ('Step 4 · JSON with nested fields',
     code('sql', 'Beeline', "CREATE EXTERNAL TABLE restaurants (restaurant_id INT, name STRING, city STRING,\n  cuisine STRING, rating DECIMAL(2,1), tags ARRAY<STRING>,\n  contact STRUCT<phone:STRING, email:STRING>)\nSTORED AS JSONFILE\nLOCATION 'file:///data/tiffingo/restaurants';\nSELECT restaurant_id, name, city, rating, tags, contact.email FROM restaurants LIMIT 3;",
          capf('l24_json.txt').split('+---------------+')[0].rstrip()),
     'JSON keys map to columns by name; the JSON list becomes an ARRAY and the nested object a STRUCT, read with <code>contact.email</code>. <code>SHOW CREATE TABLE</code> shows the SerDe chosen: <code>org.apache.hadoop.hive.serde2.JsonSerDe</code>.'),
    ('Step 5 · JSON edge cases',
     code('sql', 'Beeline', '-- r.json:\n-- {"restaurant_id": 900, "name": "Good Line", "city": "Pune"}\n-- {"restaurant_id": "nine-o-two", "name": "Bad Type", "city": "Pune", "extra_field": 1}\n-- {"name": "No Id", "CITY": "Thane"}\nSELECT * FROM rest_bad;',
          capf('l24_json_types.txt') + '\n\n-- with a line missing its closing }:\n' + capf('l24_json_bad.txt').split(' (`StreamReadFeature')[0] + ' …'),
     'Extra keys are ignored, missing keys give NULL, key case does not matter (<code>CITY</code> matched <code>city</code>), and a text value in an INT field became <b>0</b>, a silent wrong value. One truncated line failed the <b>whole query</b>. Validate JSON before it lands.'),
    ('Step 6 · RegexSerDe for web server logs',
     code('sql', 'Beeline', "CREATE EXTERNAL TABLE access_log (\n  ip STRING, ts STRING, method STRING, path STRING, status INT, bytes INT)\nROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.RegexSerDe'\nWITH SERDEPROPERTIES (\n  'input.regex' = '^(\\\\S+) \\\\S+ \\\\S+ \\\\[([^\\\\]]+)\\\\] \"(\\\\S+) (\\\\S+) \\\\S+\" (\\\\d{3}) (\\\\d+)$')\nLOCATION 'file:///data/tiffingo/access_log';\nSELECT status, COUNT(*) AS hits FROM access_log GROUP BY status ORDER BY status;",
          '+---------+-------+\n| status  | hits  |\n+---------+-------+\n| 200     | 2531  |\n| 304     | 257   |\n| 404     | 143   |\n| 500     | 69    |\n+---------+-------+'),
     'Six capturing groups → six columns. Backslashes are doubled because the regex is inside a HiveQL string literal. 2,531 + 257 + 143 + 69 = 3,000 lines: every line matched.'),
    ('Step 7 · Lines that do not match, and NULL markers',
     code('sql', 'Beeline', "-- access_bad has two log lines and 'health-check ping from load balancer'\nSELECT ip, status, path FROM access_bad;", capf('l24_regex_bad.txt')),
     'A line that does not match the pattern gives a row of NULLs (no error). Filter them with <code>WHERE ip IS NOT NULL</code> and count them as a quality metric. For delimited text, <code>\\N</code> means NULL and an empty field is an empty string; <code>serialization.null.format</code> changes the marker (PCRUN 3).'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
def cells(x, y, vals, tones, w=82, h=24, size=7.6):
    o = ''
    for k, (v, tone) in enumerate(zip(vals, tones)):
        o += box(x + k * (w + 4), y, w, h, tone) + t(x + k * (w + 4) + w / 2, y + 16, v, size, 'ink', mono=True)
    return o
LINE = '1,"Dal, Rice combo",120,Thali'
see = [
    term([('$ head -2 menu.csv', W), ('item_id,name,price,category', W), ('1,"Dal, Rice combo",120,Thali', G)]),
    term([('> SELECT * FROM menu_naive LIMIT 1;', W), ('| 1 | "Dal | NULL | 120 |', RD)]),
    term([('> SELECT * FROM menu_csv LIMIT 1;', W), ('| 1 | Dal, Rice combo | 120 | Thali |', G), ('> SELECT typeof(price) FROM menu_csv', W), ('  LIMIT 1;', W), ('| string |', Y)]),
    term([('> SELECT name, tags, contact.email', W), ('  FROM restaurants LIMIT 1;', W), ('| Desai Mess | ["late-night"] |', G), ('|   kitchen1@tiffingo.in |', G)]),
    term([('> SELECT * FROM rest_bad;', W), ('Error: … SerDeException: …', RD), ('  JsonEOFException: Unexpected', RD), ('  end-of-input: expected close', RD), ('  marker for Object', RD)]),
    term([('> SELECT ip, status, path FROM access_bad;', W), ('| 10.165.39.83  | 200  | /api/orders |', G), ('| 10.114.24.225 | 304  | /cart       |', G), ('| NULL          | NULL | NULL        |', RD)], size=7.6),
]
B1 = [
    t(180, 22, 'One record, as bytes', 9.4, bold=True) + box(20, 50, 320, 34, 'card') + t(180, 72, LINE, 9, 'ink', mono=True) + t(180, 110, 'The InputFormat has cut the file into lines.', 8.4, 'ink2') + t(180, 126, 'Now the SerDe must cut the line into columns.', 8.4, 'ink2') +
    cap('File format → records. SerDe → columns.', '', 'blue', y=190, h=34),
    t(180, 22, 'LazySimpleSerDe: split at every comma', 9.4, 'red', bold=True) + t(180, 52, '1 | "Dal | Rice combo" | 120 | Thali', 8.8, 'red', mono=True) + t(180, 72, '5 pieces for 4 columns: the 5th is dropped', 8.4, 'ink2') +
    cells(10, 92, ['1', '"Dal', 'NULL', '120'], ['card', 'red', 'red', 'red']) + t(180, 140, 'price: " Rice combo"" is not an INT → NULL', 8, 'ink2', mono=True) + cap('No quote awareness: columns shift.', '', 'red', y=190, h=34),
    t(180, 22, 'OpenCSVSerde: quotes respected', 9.4, 'green', bold=True) + cells(10, 52, ['1', 'Dal, Rice…', '120', 'Thali'], ['green'] * 4) + t(180, 104, 'but each value is handed back as a STRING', 8.4, 'amber', bold=True) +
    t(180, 122, "'120' + 1 → 121.0 (string → DOUBLE)", 8.2, 'ink2', mono=True) + cap('Correct values, wrong types: CAST them.', '', 'amber', y=190, h=34),
    t(180, 22, 'JsonSerDe: keys → columns', 9.4, bold=True) + box(10, 40, 160, 104, 'card') + ''.join(t(18, 56 + k * 14, s, 7.2, anchor='start', mono=True) for k, s in enumerate(['{"restaurant_id": 1,', ' "name": "Desai Mess",', ' "tags": ["late-night"],', ' "contact": {', '   "email": "kitchen1@…"}}'])) +
    arrow(172, 90, 190, 90) + ''.join(label_box(192, 40 + k * 36, 156, 30, [a, b], tone, 7.4) for k, (a, b, tone) in enumerate([('restaurant_id INT', '1', 'blue'), ('tags ARRAY<STRING>'.replace('<', '&lt;').replace('>', '&gt;'), '["late-night"]', 'green'), ('contact STRUCT', '.email = kitchen1@…', 'violet')])) +
    cap('Matched by key name (case-insensitive).', '', 'blue', y=190, h=34),
    t(180, 22, 'One broken line stops the reader', 9.4, 'red', bold=True) + box(20, 44, 320, 66, 'red') + t(30, 62, '{"restaurant_id": 900, …}', 8, 'ink', anchor='start', mono=True) + t(30, 78, '{"restaurant_id": 901, … "city": "Pune"', 8, 'red', anchor='start', mono=True, bold=True) + t(30, 94, '{"restaurant_id": …}', 8, 'ink', anchor='start', mono=True) +
    t(180, 136, 'the parser reaches the end of input inside an object', 8.4, 'ink2') + cap('The whole query fails, not just one row.', 'Validate JSON at ingestion.', 'red', y=176, h=46),
    t(180, 22, 'RegexSerDe: groups → columns', 9.4, bold=True) + t(180, 48, '^(\\S+) \\S+ \\S+ \\[([^\\]]+)\\] "(\\S+) (\\S+) …" (\\d{3}) (\\d+)$', 7.4, 'ink', mono=True) +
    cells(10, 62, ['ip', 'ts', 'method', 'path'], ['blue', 'blue', 'blue', 'blue'], w=82, size=7.4) + t(180, 114, '“health-check ping…” does not match', 8.4, 'red', bold=True) + t(180, 130, '→ every column NULL', 8.4, 'red') +
    cap('Count the NULL rows: they are lines you did not parse.', '', 'amber', y=190, h=34),
]
see_caps = ['The menu file has a dish name with a comma inside quotes.',
            'The default table splits that line wrongly: the name is cut and the price is NULL.',
            'With OpenCSVSerde the row is right, but typeof(price) says string.',
            'JSON keys become columns, including an array and a nested object.',
            'One unfinished JSON line makes the whole query fail.',
            'A log line that does not match the regex becomes a row of NULLs.']
behind_caps = ['The text InputFormat has already split the file into lines. Now the SerDe must split one line into columns.',
               'LazySimpleSerDe splits on every comma: five pieces for four columns. Values land in the wrong columns.',
               'OpenCSVSerde respects quotes but returns all values as strings, so arithmetic converts them to DOUBLE.',
               'The JsonSerDe matches keys to column names, ignoring case; nested values map to complex types.',
               'The JSON parser reaches the end of the input inside an object and throws an exception for the whole read.',
               'RegexSerDe maps capturing group 1 to column 1, and so on. If the line does not match, nothing is captured.']
two = anim_two('SerDes at work', 'Bytes to columns, six frames', 'Real Beeline output', 'What the SerDe does with the line', see, B1, see_caps, behind_caps)

# ---- scenario 1: raw → curated pattern
p1 = (t(180, 22, 'Daily partner CSV, quoted and messy', 9.6, bold=True) + node(20, 50, 140, 50, 'partner_menu.csv', 'quotes, commas', 'card') + arrow(162, 75, 196, 75) + node(198, 50, 140, 50, 'raw.menu (OpenCSV)', 'all STRING', 'amber') +
      cap('Read it with the SerDe it needs.', '', 'blue', y=150, h=34))
p2 = (t(180, 22, 'Publish a clean, typed copy', 9.6, bold=True) + t(180, 52, 'INSERT OVERWRITE TABLE tiffingo.menu', 8.2, 'ink', mono=True) + t(180, 68, 'SELECT CAST(item_id AS INT), name,', 8.2, 'ink', mono=True) + t(180, 84, 'CAST(price AS DECIMAL(8,2)), category FROM raw.menu;', 8.2, 'ink', mono=True) +
      cap('ORC table with real types.', 'Everyone else queries this one.', 'green', y=150, h=46))
p3 = (t(180, 22, 'Count what the CAST lost', 9.6, bold=True) + t(180, 56, 'SUM(CASE WHEN CAST(price AS DECIMAL(8,2)) IS NULL', 7.8, 'ink', mono=True) + t(180, 72, 'AND price &lt;&gt; \'\' THEN 1 ELSE 0 END) AS bad_prices', 7.8, 'ink', mono=True) +
      cap('Alert when bad_prices > 0.', 'Bad rows are reported, not hidden.', 'amber', y=150, h=46))
p4 = (t(180, 22, 'Why not query raw directly?', 9.6, bold=True) + ''.join(t(26, 52 + k * 19, s, 8.4, anchor='start') for k, s in enumerate(['• every query must remember to CAST', '• text parsing on every read: slow', '• one producer change breaks every report', '• ORC/Parquet: typed, compressed, fast'])) +
      cap('Pay the parsing cost once.', '', 'green', y=150, h=34))
p5 = (t(180, 22, 'The pattern', 9.6, 'acc', bold=True) + label_box(10, 60, 100, 50, ['file', 'any shape'], 'card', 8.4) + arrow(112, 85, 128, 85) + label_box(130, 60, 100, 50, ['raw table', 'right SerDe'], 'amber', 8.4) + arrow(232, 85, 248, 85) + label_box(250, 60, 100, 50, ['curated', 'ORC, typed'], 'green', 8.4) +
      cap('Raw → curated is the standard pipeline shape.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Raw table with the right SerDe, curated table with real types',
              'The professional answer to awkward files: parse once, publish clean.',
              'Raw to curated', 'A messy CSV read with OpenCSVSerde into a raw table, cast into a typed ORC table, with a count of rejected values', [p1, p2, p3, p4, p5],
              ['A partner sends a quoted CSV every day. A raw table reads it with OpenCSVSerde; all columns are strings.',
               'A daily INSERT casts each column to its real type into an ORC table.',
               'The same job counts values the CAST turned into NULL and alerts if any appear.',
               'Querying the raw table directly would repeat casts and parsing in every report.',
               'File → raw table with the right SerDe → curated typed table: the standard shape.'],
              hid='scenario-rawcurated')

# ---- scenario 2: log analytics
g1 = (t(180, 22, '“Checkout is failing!”', 9.6, 'red', bold=True) + t(180, 52, 'Support gets complaints at 9 p.m.', 8.6, 'ink2') + box(40, 66, 280, 60, 'card') + t(180, 86, 'access.log on the web servers', 8.4, bold=True, mono=True) + t(180, 104, '3,000 lines in our sample day', 8, 'ink2') +
      cap('Logs are text with a fixed pattern.', '', 'blue', y=150, h=34))
g2 = (t(180, 22, 'RegexSerDe table over the log folder', 9.6, bold=True) + cells(10, 52, ['ip', 'ts', 'path', 'status'], ['blue'] * 4) + t(180, 104, 'no copying: an external table on the folder', 8.4, 'ink2') + cap('SQL on raw logs in minutes.', '', 'green', y=150, h=34))
g3 = (t(180, 22, 'Errors by status (real)', 9.6, bold=True) + bars([('200', 84, 'green', '2,531'), ('304', 9, 'blue', '257'), ('404', 5, 'amber', '143'), ('500', 2.3, 'red', '69')], y=40) +
      cap('69 server errors in the day.', '', 'red', y=150, h=34))
g4 = (t(180, 22, 'Which pages fail? (real)', 9.6, bold=True) + bars([('/api/orders', 100, 'red', '15'), ('/checkout', 100, 'red', '15'), ('/menu', 93, 'red', '14')], y=46, x=150, w=160) +
      cap('Spread across pages: not one broken screen.', 'Look at a shared backend instead.', 'amber', y=150, h=46))
g5 = (t(180, 22, 'Make it robust', 9.6, 'green', bold=True) + ''.join(t(26, 52 + k * 19, s, 8.4, anchor='start') for k, s in enumerate(['• WHERE ip IS NOT NULL drops unmatched lines', '• count unmatched lines as a metric', '• parse ts with a date function (Module 4)', '• keep a daily ORC copy for fast history'])) +
      cap('Regex tables are great for exploring.', '', 'green', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Investigating errors in a web server log',
              'Operations needs answers from raw logs tonight. The numbers come from the lab’s sample log.',
              'Log analytics', 'A RegexSerDe table over web server logs used to count errors by status and by page', [g1, g2, g3, g4, g5],
              ['Users report checkout failures. The evidence is in the web server access logs.',
               'An external RegexSerDe table turns each log line into columns without copying files.',
               'GROUP BY status shows 69 server errors (status 500) in the sample day.',
               'Errors are spread over several pages, which points to a shared backend rather than one page.',
               'Filter unmatched lines, track them as a metric, and keep a typed daily copy for history.'],
              hid='scenario-logs')

# ---- scenario 3: silent JSON problems
j1 = (t(180, 22, 'A new app version ships', 9.6, bold=True) + t(180, 56, '"restaurant_id": 902   →   "restaurant_id": "R-902"', 8.4, 'ink', mono=True) + cap('A developer changed the id to a string.', '', 'amber', y=150, h=34))
j2 = (t(180, 22, 'Hive keeps running…', 9.6, bold=True) + term([('| restaurant_id | name     |', W), ('| 900           | Good Line|', G), ('| 0             | Bad Type |', Y)], label='real behaviour in our lab', size=8, y0=64).replace('y="14" width="332" height="196"', 'y="36" width="332" height="100"').replace('y="30" font-size="9"', 'y="50" font-size="9"') +
      cap('Wrong-type values became 0, not NULL.', 'Joins on restaurant_id quietly match nothing.', 'red', y=150, h=46))
j3 = (t(180, 22, '…or stops completely', 9.6, 'red', bold=True) + t(180, 60, 'one line cut off during upload:', 8.6, 'ink2') + t(180, 80, 'JsonEOFException: Unexpected end-of-input', 8.4, 'red', mono=True, bold=True) +
      cap('The whole nightly job fails.', '', 'red', y=150, h=34))
j4 = (t(180, 22, 'Defences', 9.6, 'green', bold=True) + ''.join(t(26, 52 + k * 19, s, 8.4, anchor='start') for k, s in enumerate(['• validate JSON and schema at ingestion', '• read raw ids as STRING, cast in curated', '• quarantine bad lines instead of loading them', '• data contract with the app team'])) +
      cap('Problems caught at the door are cheap.', '', 'green', y=150, h=34))
j5 = (t(180, 22, 'Check after every load', 9.6, 'acc', bold=True) + t(180, 60, "SELECT COUNT(*) FROM restaurants WHERE restaurant_id = 0", 7.8, 'ink', mono=True) + t(180, 76, "   OR restaurant_id IS NULL;", 7.8, 'ink', mono=True) +
      cap('A non-zero count raises an alert.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'JSON that changes shape',
              'JSON is flexible, which is exactly why it breaks quietly. Both behaviours shown were reproduced in the lab.',
              'JSON schema drift', 'A JSON field changing type produces zeros silently, and a truncated line fails the query; defences at ingestion', [j1, j2, j3, j4, j5],
              ['An app release changes restaurant_id from a number to a string.',
               'The JsonSerDe returned 0 for the text value in our lab: no error, wrong data.',
               'A truncated line fails the entire query with JsonEOFException.',
               'Validate at ingestion, keep raw ids as STRING, quarantine bad lines and agree a data contract.',
               'Run a simple check after each load and alert on suspicious values.'],
              hid='scenario-json')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>One line, many readers</h2>
  <p>Left: Beeline’s real output. Right: what the SerDe does with the bytes.</p>
''' + two + '''
  <p>Three live scenarios follow: raw-to-curated pipelines, log analytics and JSON schema drift.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>SerDes in real pipelines</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:#E0A100"/>' + t(60, 42, '"a, b",c', 9, 'acc', bold=True, mono=True) + t(60, 58, 'OpenCSV', 7.4, 'ink2'),
    '1. Partner and government CSV exports',
    'Bank statements, GST reports and partner catalogues often quote fields with commas. A raw OpenCSVSerde table reads them correctly before a typed copy is made.',
    ['Export', '*OpenCSVSerde', 'Typed ORC']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, '{ }', 11, 'blue', bold=True, mono=True) + t(60, 58, 'JSONFILE', 7.4, 'ink2'),
    '2. App and API events',
    'Mobile apps and APIs emit JSON. Landing tables use <code>STORED AS JSONFILE</code> with ARRAY, MAP and STRUCT columns that mirror the payload.',
    ['App events', '*JsonSerDe', 'Event tables']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-board"/><text x="22" y="42" font-size="7" class="mono" style="fill:#9FD3B8">10.1.2.3 - - [..]</text><text x="22" y="56" font-size="7" class="mono" style="fill:#FF8A80">"GET /x" 500</text>',
    '3. Server and security logs',
    'Web, firewall and application logs follow fixed patterns. RegexSerDe tables let operations and security teams query them with SQL during an incident.',
    ['Log files', '*RegexSerDe', 'Incident queries']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'TSV / |', 9, 'acc', bold=True, mono=True) + t(60, 58, 'DELIMITED', 7.4, 'ink2'),
    '4. Exports between systems',
    'Data moved between databases is often exported as tab- or pipe-separated text with <code>\\N</code> for NULL, which LazySimpleSerDe reads quickly with no extra settings.',
    ['DB export', '*Delimited text', 'Hive']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'ORC', 10, 'green', bold=True, mono=True) + t(60, 58, 'built-in SerDe', 7.4, 'ink2'),
    '5. Curated warehouse tables',
    'Once data is clean it is stored as ORC or Parquet, whose SerDes keep types, compress well and let Hive skip data. Text SerDes stay at the edges of the pipeline.',
    ['Raw text', '*INSERT … SELECT', 'ORC tables']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> know column types and delimiters from <a href="../03-data-types/">Lesson 2.3</a>. A little regular-expression knowledge helps for Step 6 (each <code>(…)</code> captures one column).</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
