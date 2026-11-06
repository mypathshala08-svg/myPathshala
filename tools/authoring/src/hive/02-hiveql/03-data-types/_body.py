import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()

# ---------------------------------------------------------------- story
sc = (box(10, 12, 196, 126, 'card') + t(108, 30, 'One order line in the file', 8.8, bold=True) +
      t(20, 54, '100001|Chole Bhature,Aloo', 7.6, anchor='start', mono=True) + t(20, 67, 'Paratha,Lassi,Rajma Chawal|', 7.6, anchor='start', mono=True) + t(20, 80, 'spice:medium,cutlery:yes', 7.6, anchor='start', mono=True) +
      t(108, 112, 'just text', 8.4, 'ink2') + arrow(210, 76, 250, 76, 'ink3', 2.2) +
      box(256, 12, 374, 126, 'acc') + t(443, 30, 'The same line, typed by Hive', 8.8, bold=True) +
      label_box(268, 44, 70, 52, ['order_id', 'INT', '100001'], 'blue', 7.6) +
      label_box(346, 44, 136, 52, ['dishes', 'ARRAY&lt;STRING&gt;', '4 items'], 'green', 7.6) +
      label_box(490, 44, 128, 52, ['prefs', 'MAP&lt;STRING,STRING&gt;', "['spice'] → medium"], 'violet', 7.6) +
      t(443, 120, 'dishes[0] = Chole Bhature · size(dishes) = 4', 8, 'ink2', mono=True))
scene_svg = scene('A text line from the order items file becomes an integer, an array of dishes and a map of preferences when read through a typed Hive table.', sc,
                  'The file holds text; the <tspan font-weight="700" class="s-acc">column types</tspan> decide what Hive can do with it.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Why is the cutlery column NULL for every order?”</h2>
  <div class="story">
    <p class="narration">TiffinGo’s app writes one line per order: the order id, the dishes and the customer’s preferences (spice level, cutlery yes or no). Kabir defines a table with an <code>ARRAY</code> and a <code>MAP</code> column and asks for <code>prefs['cutlery']</code>. Every row says <code>NULL</code>. Meanwhile Riya’s revenue total is off by a few paise, and a TINYINT column shows <code>-128</code> where it should say 128.</p>

{scene_svg}

K> The file clearly says <code>cutlery:yes</code>. Why can’t Hive see it?
A> Because Hive reads text through the <b>types and delimiters</b> you declare. A file has no types; it is just characters. If you tell Hive the wrong separator for map entries, the whole rest of the line becomes one value. We will reproduce your bug exactly.
R> And my paise? And the -128?
A> Those are type choices too. <code>DOUBLE</code> cannot store 0.1 exactly, so money belongs in <code>DECIMAL</code>. <code>TINYINT</code> holds only −128 to 127, and in Hive arithmetic that goes past the limit <b>wraps around</b> silently. Today you will see every type Hive has, what happens when a value does not fit, and how to work with arrays, maps and structs.
  </div>
</section>
'''

lv = '''
LEVELS> Data types at three levels
L1> Containers of the right size
      <ul>
        <li>A type is a <b>container</b>: a small cup (TINYINT) holds small numbers, a bucket (BIGINT) holds huge ones. Pour too much in and it spills.</li>
        <li><b>STRING</b> holds any text; <b>DATE</b> and <b>TIMESTAMP</b> hold calendar values; <b>BOOLEAN</b> holds true or false.</li>
        <li>Complex types hold <b>many values in one column</b>: a list (ARRAY), a lookup table (MAP) or a mini-record (STRUCT).</li>
        <li>If Hive cannot read a value as the declared type, it shows <b>NULL</b> instead of failing.</li>
      </ul>
L2> Choosing types
      <ul>
        <li>Counts and ids: <b>INT</b> (up to about 2.1 billion) or <b>BIGINT</b> (up to about 9.2 × 10<sup>18</sup>).</li>
        <li>Money: <b>DECIMAL(p,s)</b>, for example DECIMAL(12,2). Never DOUBLE for rupees.</li>
        <li>Text: <b>STRING</b> almost always; VARCHAR(n) cuts longer text; CHAR(n) pads.</li>
        <li>Dates: <b>DATE</b> needs <code>yyyy-MM-dd</code>; <b>TIMESTAMP</b> needs <code>yyyy-MM-dd HH:mm:ss[.fff]</code>. Other layouts become NULL; convert them with functions (Module 4).</li>
        <li>Nested data: <b>ARRAY&lt;T&gt;</b>, <b>MAP&lt;K,V&gt;</b>, <b>STRUCT&lt;a:T, b:U&gt;</b>; rarely <b>UNIONTYPE</b>.</li>
      </ul>
L3> Exact behaviour in Hive 4.2.1 (all checked in the lab)
      <ul>
        <li><b>Overflow wraps</b>: <code>CAST(127 AS TINYINT) + CAST(1 AS TINYINT)</code> = −128; <code>INT 2147483647 + 1</code> = −2147483648; <code>CAST(300 AS TINYINT)</code> = 44 (low 8 bits kept).</li>
        <li><b>Literals</b>: <code>1</code> is INT, <code>1L</code> BIGINT, <code>1.5</code> is <b>DECIMAL(2,1)</b>, <code>'a'</code> STRING (checked with <code>typeof()</code>).</li>
        <li><b>Division</b>: <code>7 / 2</code> = 3.5 (always a fractional result); <code>7 DIV 2</code> = 3.</li>
        <li><b>Implicit conversion</b>: <code>'10' + 5</code> = 15.0 (the string becomes DOUBLE). Invalid text in CAST gives NULL; <code>CAST('2026-02-30' AS DATE)</code> is NULL.</li>
        <li><b>DECIMAL overflow</b> gives NULL: <code>CAST(123456.78 AS DECIMAL(7,2))</code> is NULL because only 5 digits fit before the point.</li>
        <li><b>Strict timestamps</b>: <code>CAST(1793010170 AS TIMESTAMP)</code> is refused (<code>hive.strict.timestamp.conversion</code>); use <code>from_unixtime()</code>.</li>
        <li><b>Delimiters</b>: in a delimited text table, array items <b>and</b> map entries both use <code>COLLECTION ITEMS TERMINATED BY</code>; map keys use <code>MAP KEYS TERMINATED BY</code>.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Hive data types</h2>
''' + def_block(
    'Hive supports <b>primitive types</b>: integers (<code>TINYINT</code>, <code>SMALLINT</code>, <code>INT</code>, <code>BIGINT</code>), floating point (<code>FLOAT</code>, <code>DOUBLE</code>), exact <code>DECIMAL(p,s)</code>, text (<code>STRING</code>, <code>VARCHAR(n)</code>, <code>CHAR(n)</code>), <code>BOOLEAN</code>, <code>BINARY</code> and date/time types (<code>DATE</code>, <code>TIMESTAMP</code>, <code>INTERVAL</code>); and <b>complex types</b>: <code>ARRAY&lt;T&gt;</code>, <code>MAP&lt;K,V&gt;</code>, <code>STRUCT&lt;name:T, …&gt;</code> and <code>UNIONTYPE&lt;T1, T2, …&gt;</code>. Because Hive applies the schema when data is read, a value that cannot be interpreted as the declared type is returned as <code>NULL</code>.',
    'Every column has a type that tells Hive how to read and compute with the text in the files. Simple types hold one value; complex types hold a list, a key–value lookup or a small record inside one column. Values that do not fit the type turn into NULL.') + '''

  <h3>Primitive types</h3>
''' + table(['Type', 'Size / range', 'Example literal', 'Use for'], [
    ['<code>TINYINT</code>', '1 byte, −128 to 127', '<code>100Y</code>', 'Tiny codes, flags'],
    ['<code>SMALLINT</code>', '2 bytes, −32,768 to 32,767', '<code>100S</code>', 'Small counts'],
    ['<code>INT</code>', '4 bytes, about ±2.1 billion', '<code>100</code>', 'Ids, counts'],
    ['<code>BIGINT</code>', '8 bytes, about ±9.2 × 10<sup>18</sup>', '<code>100L</code>', 'Large ids, epoch milliseconds, sums'],
    ['<code>FLOAT</code> / <code>DOUBLE</code>', '4 / 8 bytes, approximate', '<code>CAST(1.5 AS DOUBLE)</code>', 'Measurements, ratios, ML features'],
    ['<code>DECIMAL(p,s)</code>', 'Exact; up to 38 digits, s after the point', '<code>1.5BD</code>, <code>1.5</code>', 'Money, rates'],
    ['<code>STRING</code>', 'Any length', "<code>'Pune'</code>", 'Almost all text'],
    ['<code>VARCHAR(n)</code> / <code>CHAR(n)</code>', 'Max n (cut) / exactly n (padded)', "<code>CAST('x' AS VARCHAR(8))</code>", 'Compatibility with other databases'],
    ['<code>BOOLEAN</code>', 'true / false', '<code>TRUE</code>', 'Flags'],
    ['<code>DATE</code>', '<code>yyyy-MM-dd</code>', "<code>DATE '2026-10-31'</code>", 'Calendar days, partitions'],
    ['<code>TIMESTAMP</code>', '<code>yyyy-MM-dd HH:mm:ss[.fffffffff]</code>, no time zone', "<code>TIMESTAMP '2026-10-31 21:15:00'</code>", 'Event times'],
    ['<code>BINARY</code>', 'Bytes', '<code>unhex(\'4869\')</code>', 'Images, hashes (rare)'],
], minw=660) + '''

  <h3>Complex types</h3>
''' + table(['Type', 'Holds', 'Build it', 'Read it'], [
    ['<code>ARRAY&lt;STRING&gt;</code>', 'An ordered list of one type', "<code>array('Poha','Chai')</code>", '<code>dishes[0]</code>, <code>size(dishes)</code>, <code>array_contains(dishes,\'Poha\')</code>'],
    ['<code>MAP&lt;STRING,STRING&gt;</code>', 'Key → value pairs, keys unique', "<code>map('spice','mild')</code>", "<code>prefs['spice']</code>, <code>map_keys(prefs)</code>"],
    ['<code>STRUCT&lt;city:STRING, pin:INT&gt;</code>', 'Named fields of different types', "<code>named_struct('city','Pune','pin',410210)</code>", '<code>addr.city</code>'],
    ['<code>UNIONTYPE&lt;STRING, INT&gt;</code>', 'One value that can be one of several types', "<code>create_union(0,'UPI',99)</code>", 'Shown as <code>{0:"UPI"}</code>; limited support'],
], minw=680) + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Primitive type', 'Holds one value: a number, text, date, flag.'),
    ('Complex type', 'Holds a collection or record inside one column: ARRAY, MAP, STRUCT, UNIONTYPE.'),
    ('Overflow', 'A result too big for its type. Integer arithmetic in Hive wraps around; DECIMAL becomes NULL.'),
    ('Implicit conversion', 'Hive changes a type automatically, for example a string to DOUBLE in <code>\'10\' + 5</code>.'),
    ('CAST', 'Explicit conversion: <code>CAST(x AS INT)</code>. Invalid input gives NULL.'),
    ('Precision, scale', 'In DECIMAL(7,2): 7 digits in total, 2 after the point, so at most 99,999.99.'),
    ('Collection delimiter', 'The character between array items and between map entries in a text file.'),
    ('typeof()', 'A function that tells you the type of an expression: <code>typeof(1.5)</code> → <code>decimal(2,1)</code>.'),
]) + lv + '''
EXAM> “List Hive data types.” Write two groups. Primitive: numeric (TINYINT, SMALLINT, INT, BIGINT, FLOAT, DOUBLE, DECIMAL), string (STRING, VARCHAR, CHAR), date/time (DATE, TIMESTAMP, INTERVAL), misc (BOOLEAN, BINARY). Complex: ARRAY, MAP, STRUCT, UNIONTYPE, each with a one-line example such as <code>ARRAY&lt;STRING&gt;</code> → <code>dishes[0]</code>.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Choosing types for TiffinGo tables</h2>
''' + table(['Column', 'Good type', 'Why', 'Bad choice and what happens'], [
    ['<code>order_id</code>', '<code>BIGINT</code>', 'Ids grow for years', '<code>INT</code>: wraps to negative after 2,147,483,647'],
    ['<code>amount</code> (rupees)', '<code>DECIMAL(12,2)</code>', 'Exact paise', '<code>DOUBLE</code>: 0.1 + 0.2 = 0.30000000000000004'],
    ['<code>order_ts</code>', '<code>TIMESTAMP</code>', 'Date arithmetic, ordering', '<code>STRING</code>: sorts “9:05” after “21:15”'],
    ['<code>order_date</code>', '<code>DATE</code>', 'Partitions, date filters', 'Source <code>31/10/2026</code> into DATE: NULL'],
    ['<code>rating</code> (4.3)', '<code>DECIMAL(2,1)</code> or <code>DOUBLE</code>', 'Small, approximate is fine', '<code>INT</code>: 4.3 becomes 4'],
    ['<code>dishes</code>', '<code>ARRAY&lt;STRING&gt;</code>', 'Variable number of items', 'One STRING: need string splitting in every query'],
    ['<code>prefs</code>', '<code>MAP&lt;STRING,STRING&gt;</code>', 'Optional key–value settings', 'Many sparse columns'],
    ['<code>address</code>', '<code>STRUCT&lt;city, state, pin&gt;</code>', 'Fields that belong together', 'Flat columns are also fine; structs keep JSON shape'],
], minw=760) + '''
TIP> When you load raw files you do not trust, a common pattern is to declare everything as <code>STRING</code> in the raw table, then <code>CAST</code> into proper types in the curated table and count the NULLs that the CAST produced. That way bad values are measured instead of silently hidden.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Test every type rule in the lab</h2>
  <p>All outputs are real, from Hive 4.2.1.</p>
''' + stepper([
    ('Step 1 · Integers wrap, decimals are exact',
     code('sql', 'Beeline', "SELECT CAST(127 AS TINYINT) + CAST(1 AS TINYINT) AS tiny_overflow,\n       CAST(300 AS TINYINT) AS cast_300,\n       7 / 2 AS int_div, 7 DIV 2 AS div_op,\n       CAST('abc' AS INT) AS bad_int, '10' + 5 AS str_plus_int,\n       CAST(0.1 AS DOUBLE) + CAST(0.2 AS DOUBLE) AS dbl_sum,\n       CAST(0.1 AS DECIMAL(10,2)) + CAST(0.2 AS DECIMAL(10,2)) AS dec_sum;", capf('l23_num.txt')),
     'Five lessons in one row: overflow wraps (−128), a narrowing CAST keeps only the low bits (300 → 44), <code>/</code> gives a fraction while <code>DIV</code> gives a whole number, bad text becomes NULL, and DOUBLE cannot hold 0.3 exactly while DECIMAL can.'),
    ('Step 2 · Bigger limits',
     code('sql', 'Beeline', "SELECT CAST(2147483647 AS INT) + 1 AS int_over,\n       CAST(2147483647 AS BIGINT) + 1 AS big_ok,\n       CAST(12345.678 AS DECIMAL(7,2)) AS d72,\n       CAST(123456.78 AS DECIMAL(7,2)) AS d72_over,\n       from_unixtime(1793010170) AS fu;", capf('l23_num2.txt')),
     'INT wraps too; BIGINT has room. DECIMAL(7,2) rounds 12345.678 to 12345.68 but cannot hold 123456.78 at all, so it returns NULL. <code>from_unixtime</code> converts epoch seconds (output in the server time zone, UTC in our lab).'),
    ('Step 3 · Dates, text and booleans',
     code('sql', 'Beeline', "SELECT CAST('2026-10-31' AS DATE) AS d, CAST('31/10/2026' AS DATE) AS bad_d,\n       CAST('2026-02-30' AS DATE) AS feb30,\n       CAST('2026-10-31 21:15:00' AS TIMESTAMP) AS ts,\n       CAST('Kharghar Navi Mumbai' AS VARCHAR(8)) AS vc,\n       CAST('yes' AS BOOLEAN) AS b2;", capf('l23_dates.txt')),
     'Only <code>yyyy-MM-dd</code> becomes a DATE; an Indian-style date and an impossible date are NULL. VARCHAR(8) silently cuts the text. For BOOLEAN, our tests showed <code>\'false\'</code>, <code>\'no\'</code>, <code>\'off\'</code>, <code>\'0\'</code> and the empty string become false, and anything else, even <code>\'n\'</code> or <code>\'abc\'</code>, becomes true.'),
    ('Step 4 · Ask Hive for the type',
     code('sql', 'Beeline', "SELECT typeof(1), typeof(1L), typeof(1.5), typeof(1.5BD), typeof('a');", '+------+---------+---------------+---------------+---------+\n| _c0  |   _c1   |      _c2      |      _c3      |   _c4   |\n+------+---------+---------------+---------------+---------+\n| int  | bigint  | decimal(2,1)  | decimal(2,1)  | string  |\n+------+---------+---------------+---------------+---------+'),
     '<code>1.5</code> is a DECIMAL literal in Hive 4, not a DOUBLE. <code>typeof()</code> is the quickest way to check what an expression really is.'),
    ('Step 5 · The delimiter bug, reproduced',
     code('sql', 'Beeline', "CREATE EXTERNAL TABLE order_items_bad (order_id INT,\n  dishes ARRAY<STRING>, prefs MAP<STRING,STRING>)\nROW FORMAT DELIMITED FIELDS TERMINATED BY '|'\n  COLLECTION ITEMS TERMINATED BY ','\n  MAP KEYS TERMINATED BY ':'\nLOCATION 'file:///data/tiffingo/order_items_bad';\n-- file line: 100001|Chole Bhature,…|spice:medium;cutlery:yes\nSELECT order_id, prefs, prefs['cutlery'] AS cutlery FROM order_items_bad LIMIT 2;",
          '+-----------+---------------------------------+----------+\n| order_id  |              prefs              | cutlery  |\n+-----------+---------------------------------+----------+\n| 100001    | {"spice":"medium;cutlery:yes"}  | NULL     |\n| 100002    | {"spice":"mild;cutlery:yes"}    | NULL     |\n+-----------+---------------------------------+----------+'),
     'Map entries are split by the <b>collection</b> delimiter (a comma). The file used a semicolon, so Hive saw one entry whose value was <code>medium;cutlery:yes</code>, and the key <code>cutlery</code> does not exist: NULL. Kabir’s bug, explained.'),
    ('Step 6 · The fixed file: arrays and maps at work',
     code('sql', 'Beeline', "-- file line: 100001|Chole Bhature,Aloo Paratha,Lassi,Rajma Chawal|spice:medium,cutlery:yes\nSELECT order_id, dishes[0] AS first_dish, size(dishes) AS n_dishes,\n       prefs['spice'] AS spice, prefs['cutlery'] AS cutlery\nFROM order_items LIMIT 3;\nSELECT prefs['spice'] AS spice, COUNT(*) AS orders,\n       ROUND(AVG(size(dishes)),2) AS avg_dishes\nFROM order_items GROUP BY prefs['spice'] ORDER BY orders DESC;", capf('l23_complex.txt').split('+----------------+\n| paneer_orders')[0].rstrip()),
     'Indexing (<code>[0]</code>), <code>size()</code> and map lookup work like ordinary columns, even inside GROUP BY. 5,000 orders: hot 1,695, medium 1,689, mild 1,616.'),
    ('Step 7 · A STRUCT column in a table',
     code('sql', 'Beeline', "CREATE TABLE cust_addr (customer_id INT,\n  addr STRUCT<city:STRING, state:STRING, pin:INT>, tags ARRAY<STRING>);\nINSERT INTO cust_addr\nSELECT customer_id, named_struct('city', city, 'state', state, 'pin', 400000 + customer_id),\n       array(plan, state)\nFROM customers WHERE customer_id <= 3;\nSELECT customer_id, addr, addr.city, tags FROM cust_addr;", capf('l23_struct_table.txt').split('+--------------+-------------------------------------------+')[0].rstrip()),
     'A STRUCT keeps related fields together and is read with a dot: <code>addr.city</code>. (The pin numbers here are made up from the id, only to fill the field.)'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
def dial(x, y, val, label, col):
    return label_box(x, y, 100, 44, [label, val], col, 8.6)
see = [
    term([('> SELECT CAST(127 AS TINYINT)', W), ('         + CAST(1 AS TINYINT);', W), ('| -128 |', RD), ('', W), ('> SELECT CAST(300 AS TINYINT);', W), ('| 44   |', RD)]),
    term([('> SELECT CAST(0.1 AS DOUBLE)', W), ('         + CAST(0.2 AS DOUBLE);', W), ('| 0.30000000000000004 |', Y), ('> SELECT CAST(0.1 AS DECIMAL(10,2))', W), ('         + CAST(0.2 AS DECIMAL(10,2));', W), ('| 0.30 |', G)]),
    term([("> SELECT CAST('2026-10-31' AS DATE),", W), ("         CAST('31/10/2026' AS DATE),", W), ("         CAST('2026-02-30' AS DATE);", W), ('| 2026-10-31 | NULL | NULL |', G)]),
    term([('> SELECT prefs, prefs[\'cutlery\']', W), ('  FROM order_items_bad LIMIT 1;', W), ('| {"spice":"medium;cutlery:yes"} | NULL |', RD)], size=7.6),
    term([("> SELECT dishes[0], size(dishes),", W), ("         prefs['spice'], prefs['cutlery']", W), ('  FROM order_items LIMIT 1;', W), ('| Chole Bhature | 4 | medium | yes |', G)]),
    term([('> SELECT addr, addr.city FROM cust_addr;', W), ('| {"city":"Bengaluru","state":"KA",', G), ('|  "pin":400001}  | Bengaluru |', G), ('> DESCRIBE cust_addr;', W), ('| addr | struct<city:string,state:string,', G), ('|        pin:int> |', G)], size=7.6),
]
def bits(x, y, v, n=8, col='blue'):
    s = format(v & ((1 << n) - 1), f'0{n}b')
    o = ''
    for k, ch in enumerate(s):
        o += box(x + k * 22, y, 20, 22, 'acc' if (k == 0 and col == 'red') else 'card') + t(x + k * 22 + 10, y + 15, ch, 9, 'ink', mono=True, bold=True)
    return o
B1 = [
    t(180, 22, 'TINYINT has 8 bits', 9.4, bold=True) + t(20, 52, '127 =', 8.6, anchor='start', mono=True) + bits(80, 38, 127) + t(20, 86, '+1  =', 8.6, anchor='start', mono=True) + bits(80, 72, 128, col='red') +
    t(180, 122, 'the top bit is the sign bit → read as −128', 8.4, 'red', bold=True) + t(20, 156, '300 =', 8.6, anchor='start', mono=True) + t(80, 156, '1 0010 1100 → keep 8 bits → 0010 1100 = 44', 8, 'ink2', anchor='start', mono=True) + cap('Integer overflow wraps silently. Pick a type with room.', '', 'red', y=190, h=34),
    t(180, 22, 'DOUBLE stores binary fractions', 9.4, bold=True) + dial(20, 44, '0.1000000000000000055…', 'DOUBLE 0.1', 'amber') + dial(130, 44, '0.2000000000000000111…', 'DOUBLE 0.2', 'amber') + dial(240, 44, '0.30000000000000004', 'sum', 'red') +
    dial(20, 112, '10 hundredths', 'DECIMAL 0.10', 'green') + dial(130, 112, '20 hundredths', 'DECIMAL 0.20', 'green') + dial(240, 112, '0.30 exactly', 'sum', 'green') + cap('Money = DECIMAL. Measurements = DOUBLE.', '', 'green', y=190, h=34),
    t(180, 22, 'DATE accepts one layout: yyyy-MM-dd', 9.4, bold=True) + ''.join(label_box(20, 44 + k * 44, 320, 36, [a, b], tone, 8.4) for k, (a, b, tone) in enumerate([("'2026-10-31'", '→ 2026-10-31', 'green'), ("'31/10/2026'", '→ NULL (wrong layout: convert with a function)', 'red'), ("'2026-02-30'", '→ NULL (no such day)', 'red')])) +
    cap('No error is raised: just NULL. Count NULLs after loading.', '', 'blue', y=190, h=34),
    t(180, 22, 'How the bad line was split', 9.4, bold=True) + t(180, 46, "100001|Chole…|spice:medium;cutlery:yes", 8.2, 'ink', mono=True) + t(180, 66, "fields on '|'   → 3 fields", 8.2, 'ink2', mono=True) + t(180, 84, "entries on ','  → 1 entry (no comma!)", 8.2, 'red', mono=True) + t(180, 102, "key on ':'      → spice : medium;cutlery:yes", 8.2, 'red', mono=True) +
    box(70, 116, 220, 40, 'red') + t(180, 140, "prefs['cutlery'] → no such key → NULL", 8.4, 'red', bold=True, mono=True) + cap('Same delimiter for array items and map entries.', '', 'red', y=190, h=34),
    t(180, 22, 'Fixed file: three levels of delimiters', 9.4, bold=True) + label_box(10, 44, 70, 56, ['order_id', '100001'], 'blue', 8) + label_box(88, 44, 140, 56, ['dishes (split on ,)', '[Chole Bhature, Aloo…]'], 'green', 7.6) + label_box(236, 44, 116, 56, ['prefs (, then :)', 'spice→medium', 'cutlery→yes'], 'violet', 7.6) +
    t(180, 128, "'|' fields · ',' items/entries · ':' key→value", 8.6, 'ink2', mono=True) + cap('dishes[0] · size(dishes) · prefs[\'spice\']', '', 'green', y=190, h=34),
    t(180, 22, 'STRUCT = a small record in one column', 9.4, bold=True) + box(40, 44, 280, 80, 'acc') + t(180, 62, 'addr', 9, bold=True, mono=True) + ''.join(label_box(52 + k * 88, 72, 80, 40, [f, v], 'card', 8) for k, (f, v) in enumerate([('city', 'Bengaluru'), ('state', 'KA'), ('pin', '400001')])) +
    t(180, 146, 'read a field with a dot: addr.city', 8.6, 'ink2', mono=True) + cap('Fields keep their own types (pin is INT).', '', 'blue', y=190, h=34),
]
see_caps = ['TINYINT arithmetic past 127 wraps to −128; casting 300 into a TINYINT gives 44.',
            'DOUBLE gives 0.30000000000000004; DECIMAL gives exactly 0.30.',
            'Only yyyy-MM-dd text becomes a DATE. The other two values are NULL.',
            'With the wrong map-entry delimiter, prefs has one strange entry and cutlery is NULL.',
            'With the fixed file, array and map functions return the expected values.',
            'A STRUCT column shows as JSON-like text, and addr.city reads one field.']
behind_caps = ['128 needs the 8th bit, which TINYINT uses for the sign, so the value is read as −128. 300 keeps only its lowest 8 bits: 44.',
               'Binary floating point cannot represent 0.1 exactly; DECIMAL stores digits, so money adds up.',
               'DATE parsing is strict: wrong layouts and impossible days quietly become NULL.',
               'Fields split on |, entries on the collection delimiter (a comma), keys on a colon. The semicolon was never a delimiter.',
               'Three delimiter levels map the text to INT, ARRAY and MAP. Indexing and lookups work in SELECT and GROUP BY.',
               'A STRUCT stores named fields with their own types inside one column.']
two = anim_two('Types in action', 'Six rules, six frames', 'Real Beeline results for each rule', 'What happens to the value inside Hive', see, B1, see_caps, behind_caps)

# ---- scenario 1: money in DOUBLE
m1 = (t(180, 22, 'Daily payout report: DOUBLE amounts', 9.6, bold=True) + t(180, 52, 'SUM(amount) over 18 lakh orders', 8.6, 'ink2', mono=True) + dial(70, 70, 'Rs 5,41,23,456.7299999', 'DOUBLE total', 'amber') + dial(190, 70, 'Rs 5,41,23,456.73', 'bank says', 'green') +
      cap('Tiny errors appear in the last digits.', 'Finance refuses to sign off.', 'amber', y=150, h=46))
m2 = (t(180, 22, 'Why: binary fractions', 9.6, bold=True) + ''.join(t(26, 52 + k * 18, s, 8.4, anchor='start', mono=True) for k, s in enumerate(['0.1 (DOUBLE) = 0.1000000000000000055…', '0.2 (DOUBLE) = 0.2000000000000000111…', 'many additions → errors add up', 'order of addition changes the last digits'])) +
      cap('Results can even differ between runs.', 'Parallel sums add in a different order.', 'red', y=150, h=46))
m3 = (t(180, 22, 'Fix: DECIMAL(12,2)', 9.6, 'green', bold=True) + t(180, 56, 'ALTER TABLE … CHANGE amount amount DECIMAL(12,2)', 7.8, 'ink', mono=True) + t(180, 74, 'or CAST(amount AS DECIMAL(12,2)) in the curated table', 7.8, 'ink', mono=True) +
      cap('Exact paise, same total every run.', 'Rs 5,41,23,456.73', 'green', y=150, h=46))
m4 = (t(180, 22, 'Choosing precision', 9.6, bold=True) + ''.join(t(26, 52 + k * 18, s, 8.4, anchor='start') for k, s in enumerate(['DECIMAL(12,2): up to Rs 99,99,99,999.99', 'single order amounts: DECIMAL(10,2) is plenty', 'sums: Hive widens precision for SUM results', 'too small → NULL (we saw DECIMAL(7,2) overflow)'])) +
      cap('Size for the largest value you will ever store.', '', 'blue', y=150, h=34))
m5 = (t(180, 22, 'Rule of thumb', 9.6, 'acc', bold=True) + ''.join(t(26, 52 + k * 20, s, 8.6, anchor='start') for k, s in enumerate(['Rupees, GST, commissions → DECIMAL', 'Distance, temperature, scores → DOUBLE', 'Counts, ids → INT / BIGINT', 'Never compare DOUBLEs with = '])) +
      cap('Pick types for meaning, not convenience.', '', 'green', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Money in DOUBLE: the payout that did not match',
              'A finance report sums order amounts stored as DOUBLE. The bank’s total differs in the last digits. (Amounts illustrative.)',
              'DOUBLE vs DECIMAL', 'A payout total in DOUBLE differs slightly from the bank; switching to DECIMAL gives an exact total', [m1, m2, m3, m4, m5],
              ['The DOUBLE total is off by a fraction of a paisa; the bank statement is exact.',
               'Binary floating point cannot store 0.1 exactly; errors accumulate and depend on the order of addition.',
               'Using DECIMAL(12,2) stores exact paise and gives the same total every time.',
               'Choose precision to fit the largest value; values that do not fit become NULL.',
               'DECIMAL for money, DOUBLE for measurements, INT/BIGINT for counts and ids.'],
              hid='scenario-money')

# ---- scenario 2: id overflow
i1 = (t(180, 22, 'order_id INT, launched 2019', 9.6, bold=True) + bars([('2019', 2, 'green', '0.04 bn'), ('2022', 30, 'green', '0.6 bn'), ('2025', 75, 'amber', '1.6 bn'), ('2027', 100, 'red', '2.1 bn')], y=44) +
      cap('INT max: 2,147,483,647.', 'Fast growth reaches it sooner than anyone planned.', 'amber', y=150, h=46))
i2 = term([('> SELECT CAST(2147483647 AS INT) + 1;', W), ('| -2147483648 |', RD), ('', W), ('next order id becomes negative', Y), ('joins on order_id start failing silently', Y)])
i3 = (t(180, 22, 'Fix: BIGINT', 9.6, 'green', bold=True) + t(180, 56, 'max 9,223,372,036,854,775,807', 9, 'ink', mono=True) + t(180, 80, '(we saw 2147483647 + 1 = 2147483648 as BIGINT)', 8, 'ink2') +
      cap('Ids, epoch milliseconds, sums of counts → BIGINT.', '', 'green', y=150, h=34))
i4 = (t(180, 22, 'Changing a type later', 9.6, bold=True) + t(180, 56, 'ALTER TABLE orders CHANGE order_id order_id BIGINT;', 7.8, 'ink', mono=True) + ''.join(t(26, 86 + k * 18, s, 8.4, anchor='start') for k, s in enumerate(['metadata change only: files are not rewritten', 'widening INT → BIGINT is usually safe', 'narrowing or STRING → INT may give NULLs'])) +
      cap('Widening is easy; narrowing is risky.', '', 'blue', y=150, h=34))
i5 = (t(180, 22, 'Check headroom regularly', 9.6, 'acc', bold=True) + t(180, 56, 'SELECT MAX(order_id) / 2147483647.0 FROM orders;', 8, 'ink', mono=True) + t(180, 82, 'alert above 0.5', 8.6, 'red', bold=True) +
      cap('Monitoring beats a 3 a.m. surprise.', '', 'green', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'The day order_id went negative',
              'INT is fine for years, until it is not. Watch an id column hit the limit and how teams fix and prevent it. (Growth numbers illustrative.)',
              'INT overflow', 'Order ids growing towards the INT limit, wrapping negative, and the fix with BIGINT', [i1, i2, i3, i4, i5],
              ['Order ids grow every year and approach the INT maximum of 2,147,483,647.',
               'In Hive the next value wraps to −2,147,483,648, a real result from our lab.',
               'BIGINT has room for about 9.2 quintillion values.',
               'Widening a column type is a metadata change; narrowing can create NULLs.',
               'Monitor how close ids are to their limit and alert early.'],
              hid='scenario-overflow')

# ---- scenario 3: nested app data
n1 = (t(180, 22, 'App event, as the developers send it', 9.6, bold=True) + box(20, 40, 320, 92, 'card') + ''.join(t(30, 58 + k * 14, s, 7.8, anchor='start', mono=True) for k, s in enumerate(['{"order_id": 100001,', ' "dishes": ["Chole Bhature", "Lassi"],', ' "prefs": {"spice": "medium"},', ' "addr": {"city": "Pune", "pin": 411001}}'])) +
      cap('Lists and nested objects are normal in app data.', '', 'blue', y=150, h=34))
n2 = (t(180, 22, 'Option A: flatten everything', 9.6, bold=True) + t(180, 52, 'dish1, dish2, dish3, … dish10, spice, cutlery, city, pin', 7.8, 'ink', mono=True) +
      cap('Fixed columns for a variable list: waste and limits.', 'Order 11 dishes and the 11th is lost.', 'red', y=150, h=46))
n3 = (t(180, 22, 'Option B: complex types', 9.6, 'green', bold=True) + t(180, 56, 'dishes ARRAY&lt;STRING&gt;, prefs MAP&lt;STRING,STRING&gt;,', 8, 'ink', mono=True) + t(180, 72, 'addr STRUCT&lt;city:STRING, pin:INT&gt;', 8, 'ink', mono=True) +
      cap('Keeps the shape of the data.', 'Any number of dishes, optional preferences.', 'green', y=150, h=46))
n4 = (t(180, 22, 'Query them directly', 9.6, bold=True) + ''.join(t(26, 52 + k * 18, s, 8.2, anchor='start', mono=True) for k, s in enumerate(["size(dishes) > 3", "array_contains(dishes, 'Paneer Butter Masala')", "prefs['spice'] = 'hot'", 'addr.city = \'Pune\''])) +
      cap('319 of 5,000 orders contained Paneer Butter Masala.', '(real result)', 'blue', y=150, h=46))
n5 = (t(180, 22, 'One row per dish? Module 4', 9.6, 'acc', bold=True) + t(180, 60, 'LATERAL VIEW explode(dishes) d AS dish', 8.6, 'ink', mono=True) + t(180, 84, 'turns 1 order with 4 dishes into 4 rows', 8.4, 'ink2') +
      cap('Complex types + explode = flexible analysis.', '', 'green', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Modelling nested app data',
              'Mobile apps send lists and nested objects. Compare flattening with complex types.',
              'Nested data', 'An app event with a list of dishes, a preferences map and an address object stored with complex types', [n1, n2, n3, n4, n5],
              ['An order event contains a list of dishes, optional preferences and an address.',
               'Flattening into fixed columns wastes space and breaks when lists grow.',
               'ARRAY, MAP and STRUCT keep the original shape in three columns.',
               'Functions such as size, array_contains, map lookup and dot access work in WHERE and GROUP BY.',
               'To analyse each dish separately, explode the array into rows (Module 4).'],
              hid='scenario-nested')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Six type rules, two views</h2>
  <p>Left: the real result in Beeline. Right: what happens to the value inside Hive.</p>
''' + two + '''
  <p>Three live scenarios follow: money in DOUBLE, an id column that overflows, and nested app data.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Types in real data work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'DECIMAL', 9, 'green', bold=True, mono=True) + t(60, 58, 'paise exact', 7.4, 'ink2'),
    '1. Payments and settlements',
    'UPI and card settlement tables use DECIMAL for amounts, fees and GST so totals match bank statements to the paisa.',
    ['Transactions', '*DECIMAL(12,2)', 'Reconciled totals']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'MAP', 9, 'violet', bold=True, mono=True) + t(60, 58, 'event properties', 7.4, 'ink2'),
    '2. App analytics events',
    'Click events carry different properties per screen. A <code>MAP&lt;STRING,STRING&gt;</code> column holds them without a schema change for every new property.',
    ['App event', '*MAP column', 'props[\'screen\']']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'STRING → CAST', 8.4, 'acc', bold=True) + t(60, 58, 'count NULLs', 7.4, 'ink2'),
    '3. Raw-to-curated typing',
    'Raw tables keep every column as STRING. The curated job CASTs to proper types and reports how many values became NULL, which catches broken files early.',
    ['Raw STRING', '*CAST + NULL count', 'Curated types']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'ARRAY', 9, 'blue', bold=True, mono=True) + t(60, 58, 'cart items', 7.4, 'ink2'),
    '4. Shopping carts and orders',
    'E-commerce and food-delivery orders store items as an ARRAY (or an ARRAY of STRUCTs with name, quantity and price) and explode it when item-level analysis is needed.',
    ['Order', '*ARRAY&lt;STRUCT&gt;', 'Item analysis']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:#D64545"/>' + t(60, 42, 'BIGINT', 9, 'red', bold=True, mono=True) + t(60, 58, 'ids & epochs', 7.4, 'ink2'),
    '5. Event ids and timestamps',
    'Event ids and epoch milliseconds exceed INT range, so logs and clickstreams use BIGINT and convert epochs with functions such as <code>from_unixtime</code>.',
    ['Raw epoch', '*BIGINT', 'TIMESTAMP']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> you should be able to create a table (<a href="../01-databases-and-tables/">Lesson 2.1</a>). The order items file is in the course dataset (<code>order_items.txt</code> and the faulty <code>order_items_v1.txt</code>).</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
