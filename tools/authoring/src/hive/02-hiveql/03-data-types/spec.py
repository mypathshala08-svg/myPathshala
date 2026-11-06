import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
BODY = body(HERE)
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep

META = dict(
    module='02-hiveql', lesson='03-data-types', n='2.3',
    module_label='Module 2 · Tables and data',
    title='Data types: primitive and complex',
    desc='Hive data types with real Hive 4.2.1 results: TINYINT to BIGINT, overflow wrap-around, FLOAT/DOUBLE vs DECIMAL for money, STRING/VARCHAR/CHAR, DATE and TIMESTAMP parsing, BOOLEAN casts, implicit conversion, typeof(), and the complex types ARRAY, MAP, STRUCT and UNIONTYPE with delimiters, indexing and functions.',
    og_desc='127 + 1 = −128, 0.1 + 0.2 = 0.30000000000000004 and a map that returns NULL: Hive types explained with real outputs.',
    minutes=32, level='Beginner → Advanced',
    lead='A file has no types; Hive gives it types when it reads. Choose well and queries are exact and simple. Choose badly and you get <b>−128</b> instead of 128, totals that are off by a fraction of a paisa, dates that silently turn into NULL and a map lookup that never finds its key. This lesson tests every rule in the lab with <b>real Hive 4.2.1 output</b> and teaches ARRAY, MAP, STRUCT and UNIONTYPE on TiffinGo order data.',
    chips=['Real Hive 4.2.1 outputs', 'Overflow and precision', 'ARRAY · MAP · STRUCT', 'Runs in your browser (Python)'],
)

MAIN = '''# How a delimited text line becomes typed columns (Hive's LazySimpleSerDe, simplified)
line = "100001|Chole Bhature,Aloo Paratha,Lassi|spice:medium,cutlery:yes"

order_id, dishes_txt, prefs_txt = line.split("|")          # FIELDS TERMINATED BY '|'
dishes = dishes_txt.split(",")                              # COLLECTION ITEMS TERMINATED BY ','
prefs = dict(e.split(":", 1) for e in prefs_txt.split(","))  # entries ',', MAP KEYS ':'

print("order_id:", int(order_id))
print("dishes[0]:", dishes[0], "| size:", len(dishes))
print("prefs['cutlery']:", prefs.get("cutlery"))
'''
RUN = dict(
    heading='Run the code: types and delimiters by hand',
    intro='<p>These programs imitate what Hive does when it reads typed columns: split on delimiters, convert text to numbers, wrap integers that overflow and return NULL (here <code>None</code>) for values that do not fit. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('dishes = dishes_txt.split(",")                              # COLLECTION ITEMS TERMINATED BY \',\'', 'Array items are split on the collection delimiter.'),
        ('prefs = dict(e.split(":", 1) for e in prefs_txt.split(","))  # entries \',\', MAP KEYS \':\'', 'Map entries use the <b>same</b> collection delimiter; each entry is split once on the key delimiter.'),
        ('print("prefs[\'cutlery\']:", prefs.get("cutlery"))', 'A missing key gives NULL in Hive (<code>None</code> here), not an error.'),
    ],
    tasks=[
        dict(label='1 · Split a line', hint='Press <b>Run</b>. Then change the map entries to <code>spice:medium;cutlery:yes</code> (the v1 file) and see cutlery become None, exactly like the lab.', code=None),
        dict(label='2 · TINYINT wrap-around', hint='<b>Predict first:</b> what do 127 + 1 and 300 become in an 8-bit signed integer? The function copies Hive’s behaviour.',
             code='''def tinyint(v):
    v &= 0xFF                  # keep the lowest 8 bits
    return v - 256 if v > 127 else v
print("127 + 1 ->", tinyint(127 + 1))
print("300     ->", tinyint(300))
print("-129    ->", tinyint(-129))
'''),
        dict(label='3 · DOUBLE vs DECIMAL', hint='Add up ten payments of Rs 0.10 both ways. Which one equals 1.00?',
             code='''from decimal import Decimal
d = sum([0.1] * 10)
x = sum([Decimal("0.10")] * 10)
print("float  :", repr(d), "equals 1.0?", d == 1.0)
print("decimal:", x, "equals 1.00?", x == Decimal("1.00"))
'''),
        dict(label='4 · Strict date parsing', hint='Only yyyy-MM-dd is a DATE. Add <code>"2026-13-01"</code> and <code>"2026-10-1"</code> to the list and predict the result.',
             code='''from datetime import date
def to_date(s):
    try:
        if len(s) != 10 or s[4] != "-" or s[7] != "-":
            return None
        return date(int(s[:4]), int(s[5:7]), int(s[8:]))
    except ValueError:
        return None
for s in ["2026-10-31", "31/10/2026", "2026-02-30"]:
    print(f"{s:12} -> {to_date(s)}")
'''),
        dict(label='5 · Spot the error', hint='DECIMAL(7,2) allows 5 digits before the point. The check fails for one amount. Fix the precision so all three fit.', expect='error',
             code='''def fits(value, precision, scale):
    whole_digits = len(str(int(abs(value))))
    return whole_digits <= precision - scale
amounts = [12345.67, 999.5, 123456.78]
for a in amounts:
    assert fits(a, 7, 2), f"{a} does not fit DECIMAL(7,2): Hive would return NULL"
print("all fit")
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: more type checks',
    intro='<p>Run these in Beeline on the lab. <b>The outputs are real</b>, recorded from Hive 4.2.1.</p>',
    items=[
        dict(title='1 · Which strings are true?', cmd="SELECT CAST('off' AS BOOLEAN) AS off_, CAST('n' AS BOOLEAN) AS n_, CAST('abc' AS BOOLEAN) AS abc,\n       CAST('on' AS BOOLEAN) AS on_, CAST('1' AS BOOLEAN) AS one, CAST('y' AS BOOLEAN) AS y_, CAST('' AS BOOLEAN) AS empty;", file='Beeline',
             output=open(CAP + 'l23_bool.txt').read().rstrip(),
             note='Together with Step 3: <code>false</code>, <code>no</code>, <code>off</code>, <code>0</code> and empty are false; everything else is true, including <code>n</code> and <code>abc</code>. Never rely on casting free text to BOOLEAN; map values explicitly with CASE (Module 4).'),
        dict(title='2 · More array and map functions', cmd="SELECT COUNT(*) AS paneer_orders FROM order_items\nWHERE array_contains(dishes, 'Paneer Butter Masala');\nSELECT map_keys(prefs) AS k, map_values(prefs) AS v FROM order_items LIMIT 1;", file='Beeline',
             output='+----------------+\n| paneer_orders  |\n+----------------+\n| 319            |\n+----------------+\n' + open(CAP + 'l23_complex.txt').read().rstrip().split('+----------------+\n| 319            |\n+----------------+\n')[1],
             note='<code>array_contains</code> tests membership; <code>map_keys</code> and <code>map_values</code> return arrays.'),
        dict(title='3 · STRUCT, out-of-range index, missing key, UNIONTYPE', cmd="SELECT named_struct('city','Pune','state','MH','pin',410210) AS addr,\n       named_struct('city','Pune','state','MH','pin',410210).city AS city_only,\n       array(1,2,3)[5] AS out_of_range, map('a',1)['zz'] AS missing_key,\n       create_union(0, 'UPI', 99) AS u0, create_union(1, 'UPI', 99) AS u1;", file='Beeline',
             output=open(CAP + 'l23_struct.txt').read().rstrip(),
             note='Out-of-range indexes and missing keys give NULL, not errors. A UNIONTYPE value shows the chosen tag and value (<code>{0:"UPI"}</code>); support for UNIONTYPE in joins, filters and other tools is limited, so it is rarely used.'),
    ],
)

TRACE = dict(
    heading='Converting one text line into typed values',
    intro='<p>Watch each piece of the line become a typed value. A value that cannot be converted becomes <code>None</code>, as Hive returns NULL.</p>',
    code='''line = "150001,Pune,abc,2026-10-31"
parts = line.split(",")
order_id = int(parts[0])
city = parts[1]
amount = int(parts[2]) if parts[2].isdigit() else None
day = parts[3] if parts[3][4] == "-" else None
row = (order_id, city, amount, day)
print(row)
''',
    notes={5: 'NULL :: “abc” is not an INT, so the value becomes NULL. The row is still returned.', 7: 'Row :: One row with one NULL, just like order 150001 in the lab.'},
)

WORKED_INTRO = 'Three type decisions TiffinGo engineers really face: picking types from sample data, measuring how many values a CAST will lose, and modelling an app event with complex types.'
EXAMPLES = [
    dict(level='b', tag='Design · types', title='Pick the smallest safe integer type',
         problem='<p>For each column the largest value expected in five years is given. Choose TINYINT, SMALLINT, INT or BIGINT (the smallest that fits).</p>',
         inp='rating_stars 5 · dishes_per_order 40 · daily_orders 2,500,000 · order_id 4,000,000,000',
         approach=['List the types with their maximum values.', 'For each column take the first type whose maximum is at least the expected value.', 'Print the choice.'],
         code='''limits = [("TINYINT", 127), ("SMALLINT", 32767), ("INT", 2147483647), ("BIGINT", 9223372036854775807)]
cols = {"rating_stars": 5, "dishes_per_order": 40, "daily_orders": 2_500_000, "order_id": 4_000_000_000}
for col, biggest in cols.items():
    for name, mx in limits:
        if biggest <= mx:
            print(f"{col:17} {biggest:>14,} -> {name}")
            break
''', notes={5: 'Fit :: The first type that is big enough wins.'},
         tryit='Many teams simply use INT and BIGINT everywhere: storage formats like ORC compress small values well, and the risk of overflow costs more than a few bytes.'),
    dict(level='i', tag='Data quality · CAST', title='How many values will a CAST turn into NULL?',
         problem='<p>A raw table keeps amount and order date as STRING. Before casting to INT and DATE, count how many sample values would become NULL.</p>',
         inp='amounts: 220, 150, abc, 310, "", 90 · dates: 2026-10-31, 31/10/2026, 2026-02-30, 2026-10-01',
         approach=['Write small converters that return None on failure, like Hive.', 'Apply them to every value.', 'Count the None results.'],
         code='''from datetime import date
def to_int(s):
    return int(s) if s.strip().lstrip("-").isdigit() else None
def to_date(s):
    try:
        return date.fromisoformat(s) if len(s) == 10 else None
    except ValueError:
        return None
amounts = ["220", "150", "abc", "310", "", "90"]
dates = ["2026-10-31", "31/10/2026", "2026-02-30", "2026-10-01"]
bad_a = sum(to_int(a) is None for a in amounts)
bad_d = sum(to_date(d) is None for d in dates)
print(f"amount: {bad_a} of {len(amounts)} would be NULL")
print(f"date  : {bad_d} of {len(dates)} would be NULL")
''', notes={11: 'Count :: These are the rows a curated table would silently lose.'},
         tryit='The same count in Hive: SELECT SUM(CASE WHEN CAST(amount AS INT) IS NULL THEN 1 ELSE 0 END) FROM raw_orders. Teams alert when the share goes above a threshold.'),
    dict(level='a', tag='Modelling · complex types', title='Turn an app event into ARRAY, MAP and STRUCT values',
         problem='<p>The app sends an order event as a Python dictionary (like JSON). Produce the values for columns <code>dishes ARRAY&lt;STRING&gt;</code>, <code>prefs MAP&lt;STRING,STRING&gt;</code> and <code>addr STRUCT&lt;city, pin&gt;</code>, and the delimited text line Hive would read.</p>',
         inp="{'order_id': 100001, 'dishes': ['Chole Bhature', 'Lassi'], 'prefs': {'spice': 'medium', 'cutlery': 'yes'}, 'addr': {'city': 'Pune', 'pin': 411001}}",
         approach=['Keep the list as the ARRAY, the dict as the MAP, the address as the STRUCT.', "Write text with '|' between fields, ',' between items/entries, ':' between key and value.", 'Struct fields also use the collection delimiter, in declared order.'],
         code='''event = {"order_id": 100001, "dishes": ["Chole Bhature", "Lassi"],
         "prefs": {"spice": "medium", "cutlery": "yes"}, "addr": {"city": "Pune", "pin": 411001}}
dishes = ",".join(event["dishes"])
prefs = ",".join(f"{k}:{v}" for k, v in event["prefs"].items())
addr = ",".join(str(event["addr"][f]) for f in ["city", "pin"])
line = "|".join([str(event["order_id"]), dishes, prefs, addr])
print(line)
''', notes={5: 'STRUCT :: Struct fields are written in declared order, separated like collection items.'},
         tryit='Add a dish called “Dal, Rice”. The comma inside the name breaks the array. This is why app data is usually stored as JSON with a JSON SerDe (Lesson 2.4) or in ORC/Parquet, not delimited text.'),
]

QUIZ = mix([
    dict(q='Beginner: Which type should store rupee amounts?', options=['DOUBLE', 'DECIMAL(12,2)', 'STRING', 'FLOAT'], answer=1,
         why='DECIMAL is exact; DOUBLE gave 0.30000000000000004 for 0.1 + 0.2 in the lab.'),
    dict(q='Beginner: What does Hive return for CAST(\'abc\' AS INT)?', options=['0', 'An error', 'NULL', '-1'], answer=2,
         why='Values that cannot be converted become NULL; the query keeps running.'),
    dict(q='Beginner: Which complex type stores key–value pairs?', options=['ARRAY', 'MAP', 'STRUCT', 'UNIONTYPE'], answer=1,
         why="MAP<K,V>, read with prefs['spice']."),
    dict(q='Intermediate: What is CAST(127 AS TINYINT) + CAST(1 AS TINYINT) in Hive 4.2.1?', options=['128', '-128', 'NULL', 'An overflow error'], answer=1,
         why='Integer arithmetic wraps around silently; 128 does not fit in a signed 8-bit integer.'),
    dict(q='Intermediate: What does CAST(\'31/10/2026\' AS DATE) return?', options=['2026-10-31', '2026-31-10', 'NULL', 'An error'], answer=2,
         why='Only yyyy-MM-dd is accepted. Other layouts need a conversion function first.'),
    dict(q='Intermediate: In a delimited text table, which clause separates map entries from each other?', options=['MAP KEYS TERMINATED BY', 'COLLECTION ITEMS TERMINATED BY', 'FIELDS TERMINATED BY', 'LINES TERMINATED BY'], answer=1,
         why="Array items and map entries share the collection delimiter; MAP KEYS TERMINATED BY separates a key from its value. Using ';' in the file gave NULL for prefs['cutlery']."),
    dict(q='Advanced: What type is the literal 1.5 in Hive 4?', options=['DOUBLE', 'FLOAT', 'DECIMAL(2,1)', 'STRING'], answer=2,
         why='typeof(1.5) returned decimal(2,1) in our lab.'),
    dict(q='Advanced: CAST(123456.78 AS DECIMAL(7,2)) returns…', options=['123456.78', '99999.99', 'NULL', '23456.78'], answer=2,
         why='DECIMAL(7,2) has room for 5 digits before the point; values that do not fit become NULL.'),
])

REVISION = [
    'Integers: <b>TINYINT</b> (1 B) · <b>SMALLINT</b> (2 B) · <b>INT</b> (4 B, ±2.1 bn) · <b>BIGINT</b> (8 B). Overflow <b>wraps</b>: 127 + 1 → −128.',
    'Money → <b>DECIMAL(p,s)</b>; measurements → DOUBLE. 0.1 + 0.2 as DOUBLE = 0.30000000000000004.',
    'DECIMAL that does not fit → <b>NULL</b>. Literal <code>1.5</code> is DECIMAL(2,1); <code>1L</code> BIGINT; <code>typeof()</code> to check.',
    '<code>7 / 2</code> = 3.5, <code>7 DIV 2</code> = 3. <code>\'10\' + 5</code> = 15.0 (string → DOUBLE).',
    'DATE only from <code>yyyy-MM-dd</code>; TIMESTAMP from <code>yyyy-MM-dd HH:mm:ss</code>; bad values → NULL. Numbers to TIMESTAMP: use <code>from_unixtime</code>.',
    'STRING for text; VARCHAR(n) cuts, CHAR(n) pads. BOOLEAN cast: false/no/off/0/empty → false, all else true.',
    "Complex: <b>ARRAY</b> <code>a[0]</code>, <code>size(a)</code>, <code>array_contains</code> · <b>MAP</b> <code>m['k']</code>, <code>map_keys</code> · <b>STRUCT</b> <code>s.field</code> · <b>UNIONTYPE</b> <code>create_union</code> (rare).",
    "Delimiters: fields <code>FIELDS TERMINATED BY</code>; array items <b>and</b> map entries <code>COLLECTION ITEMS TERMINATED BY</code>; key/value <code>MAP KEYS TERMINATED BY</code>.",
]
FAQ = [
    ('Why does Hive return NULL instead of an error for bad values?', 'Hive applies the schema when it reads (schema on read). Raw files often contain a few bad values, and failing a 2 TB query because of one line would be impractical, so the SerDe returns NULL for values it cannot convert. The downside is that problems are silent, so good pipelines count NULLs after CASTs and alert on unusual numbers.'),
    ('STRING or VARCHAR in Hive?', 'Use STRING for almost everything: it has no length limit and is the type Hive functions are built around. VARCHAR(n) and CHAR(n) exist mainly for compatibility with other databases and tools; VARCHAR silently cuts longer text (our test cut “Kharghar Navi Mumbai” to “Kharghar”).'),
    ('Does Hive TIMESTAMP store a time zone?', 'No. TIMESTAMP is a “local date-time” without a time zone: Hive stores and shows the value as written. Hive also has TIMESTAMP WITH LOCAL TIME ZONE for instants. In practice teams store event times in UTC, document it, and convert for display with functions such as from_utc_timestamp.'),
    ('What is the difference between ARRAY&lt;STRUCT&gt; and a separate child table?', 'An ARRAY of STRUCTs keeps an order and its items in one row, so no join is needed and the data matches the JSON the app sends. A separate items table with an order_id is easier to aggregate across all items and to update. Hive can convert between them: explode turns the array into rows (Module 4), and collect_list builds arrays from rows.'),
    ('Is UNIONTYPE used in practice?', 'Rarely. It lets one column hold a value of one of several types, but many operations and other engines do not support it well. Most teams use a STRUCT with several nullable fields, or a STRING plus a type column, instead. You should know it exists for exams and for reading old Avro-based tables.'),
]

PRACTICE_INTRO = 'Programs that practise type limits, precision, parsing and complex values.'
PROBLEMS = [
    dict(level='easy', title='Integer ranges', stmt='Print the minimum and maximum of TINYINT, SMALLINT, INT and BIGINT from their bit sizes.', inp='8, 16, 32, 64 bits',
         code='''for name, bits in [("TINYINT", 8), ("SMALLINT", 16), ("INT", 32), ("BIGINT", 64)]:
    print(f"{name:8} {-2**(bits-1):>26,} .. {2**(bits-1)-1:,}")
''', explain='Signed integers use one bit for the sign, so the range is −2^(n−1) to 2^(n−1)−1.'),
    dict(level='easy', title='DIV and /', stmt='For 17 and 5 print what Hive’s / and DIV return.', inp='17, 5',
         code='''a, b = 17, 5
print("17 / 5   =", a / b)
print("17 DIV 5 =", a // b)
''', explain='3.4 and 3. In Hive / always produces a fractional result (DOUBLE or DECIMAL); DIV is integer division.'),
    dict(level='easy', title='Array basics', stmt='For dishes ["Poha", "Chai", "Vada Pav"], print the first item, the size and whether "Chai" is present.', inp='["Poha", "Chai", "Vada Pav"]',
         code='''d = ["Poha", "Chai", "Vada Pav"]
print(d[0], len(d), "Chai" in d)
''', explain='Hive equivalents: dishes[0], size(dishes), array_contains(dishes, \'Chai\'). Index 5 would give NULL in Hive.'),
    dict(level='medium', title='Fits in DECIMAL(p,s)?', stmt='Check which amounts fit DECIMAL(8,2).', inp='999999.99 · 1000000.00 · 12.345',
         code='''def fits(v, p, s):
    return len(str(int(abs(v)))) <= p - s
for v in [999999.99, 1000000.00, 12.345]:
    print(v, fits(v, 8, 2))
''', explain='999999.99 fits (6 whole digits), 1,000,000 does not and would be NULL; 12.345 fits but is rounded to 12.35.'),
    dict(level='medium', title='Parse a map string', stmt="Turn 'spice:hot,cutlery:no,note:ring bell' into a dictionary using ',' for entries and ':' for keys.", inp='spice:hot,cutlery:no,note:ring bell',
         code='''s = "spice:hot,cutlery:no,note:ring bell"
m = dict(e.split(":", 1) for e in s.split(","))
print(m, m.get("tip"))
''', explain='The missing key “tip” gives None, as Hive gives NULL. A value containing a comma would break the split.'),
    dict(level='medium', title='Count NULLs after CAST', stmt='Count how many of these become NULL when cast to INT: "10", "x", "", "-5", "3.7".', inp='"10", "x", "", "-5", "3.7"',
         code='''vals = ["10", "x", "", "-5", "3.7"]
def to_int(s):
    return int(s) if s.lstrip("-").isdigit() else None
print([to_int(v) for v in vals])
''', explain='This simple converter rejects "x", "" and "3.7". Hive itself is more lenient: in our lab CAST(\'3.7\' AS INT) gave 3 and CAST(\' 42\' AS INT) gave 42, so always test real behaviour on your version.'),
    dict(level='business', title='Paise lost to DOUBLE', stmt='Add Rs 0.10 one million times as a float and as a Decimal. How far apart are they?', inp='1,000,000 × 0.10',
         code='''from decimal import Decimal
f = 0.0
for _ in range(1_000_000):
    f += 0.1
d = Decimal("0.10") * 1_000_000
print("float  :", f)
print("decimal:", d, "| difference:", abs(Decimal(repr(f)) - d))
''', explain='The float drifts away from 100000 in the last digits. In a payments table that is a reconciliation failure; DECIMAL avoids it.'),
    dict(level='business', title='Id headroom alert', stmt='The current maximum order_id is 1,610,000,000 and 1.2 million orders arrive per day. How many days until INT overflows?', inp='max 1,610,000,000 · 1,200,000/day',
         code='''limit, current, per_day = 2_147_483_647, 1_610_000_000, 1_200_000
days = (limit - current) // per_day
print("days left:", days, "| about", round(days / 365, 1), "years")
''', explain='447 days, about 1.2 years. Plan the change to BIGINT now, not on the day ids turn negative.'),
]

SCN_INTRO = 'Type questions reveal whether a candidate has handled real data. Expect at least one in any data-engineering interview.'
SCENARIOS = (
    scn('Banking / payments', 'Fresher', 'Totals that do not match the bank',
        'A settlement report built in Hive is off by a few paise against the bank statement.',
        'do you know floating point vs DECIMAL?',
        '''<ul>
          <li>Check the amount column’s type with DESCRIBE; DOUBLE or FLOAT cannot store most decimal fractions exactly.</li>
          <li>Store money as <code>DECIMAL(p,2)</code> with enough precision for the largest value; Hive widens precision for SUM.</li>
          <li>Never compare floating values with <code>=</code>; round or use DECIMAL.</li>
        </ul>''', '“just round at the end”: errors can change the rounded result too.') +
    scn('Data quality', 'Fresher', 'A column suddenly full of NULLs',
        'After a source change, order_date is NULL for all new rows, though the files clearly have dates.',
        'do you know schema on read and strict parsing?',
        '''<ol>
          <li>Look at raw lines: the source probably changed the layout, for example to <code>31/10/2026</code>.</li>
          <li>DATE accepts only <code>yyyy-MM-dd</code>; anything else becomes NULL without an error.</li>
          <li>Fix by reading as STRING and converting with a function (Module 4), and add a NULL-rate check that alerts.</li>
        </ol>''', 'assuming Hive would have thrown an error.') +
    scn('E-commerce · modelling', 'Mid-level', 'Arrays or a child table?',
        'You must store orders with a variable number of items for both order-level and item-level reports.',
        'can you reason about complex types and their trade-offs?',
        '''<ul>
          <li>Store items as <code>ARRAY&lt;STRUCT&lt;name:STRING, qty:INT, price:DECIMAL(10,2)&gt;&gt;</code> to keep one row per order and match the app JSON.</li>
          <li>Use <code>LATERAL VIEW explode</code> for item-level reports, or also publish an exploded items table if many reports need it.</li>
          <li>Avoid delimited text for such data; use ORC/Parquet or JSON so commas in names cannot break parsing.</li>
        </ul>''', 'ten fixed columns item1 … item10.') +
    scn('Platform · growth', 'Mid-level', 'The INT that ran out',
        'An events table uses INT for event_id. Volume has grown 10×. What do you check and change?',
        'do you know overflow behaviour and safe migration?',
        '''<ul>
          <li>Hive integer arithmetic wraps silently; compute headroom with <code>MAX(event_id)</code> vs 2,147,483,647 and the daily growth.</li>
          <li>Widen to BIGINT with <code>ALTER TABLE … CHANGE</code> (metadata only for common formats) and update downstream tables and code.</li>
          <li>Add monitoring for id headroom on all key columns.</li>
        </ul>''', '“Hive will raise an error when it overflows”: it does not.')
)
