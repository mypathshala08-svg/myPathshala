import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
BODY = body(HERE)
def capf(n):
    return open(CAP + n).read().rstrip()

META = dict(
    module='04-complex-data', lesson='03-json-and-semi-structured-data', n='4.3',
    module_label='Module 4 · Functions and complex data',
    title='JSON and semi-structured data',
    desc='Reading JSON in Hive with real Hive 4.2.1 results: raw STRING tables, get_json_object paths and their limits, json_tuple with LATERAL VIEW, the JsonSerDe with STRUCT and ARRAY columns, how one malformed line fails a scan, quarantining bad records, CTAS into ORC, plus parse_url_tuple and xpath for URLs and XML.',
    og_desc='One broken JSON line stopped the whole query. get_json_object, json_tuple and JsonSerDe in Hive with real outputs and a production pattern.',
    minutes=35, level='Beginner → Advanced',
    lead='Apps, APIs and devices send JSON: nested objects, lists and optional fields. Hive can read it with functions at query time or with a SerDe as a typed table. This lesson loads 2,000 real-shaped app events, finds the one truncated line that breaks the SerDe, quarantines it, converts the rest into ORC and answers revenue per city. <b>All outputs are real</b>, from Hive 4.2.1.',
    chips=['Real Hive 4.2.1 outputs', 'get_json_object vs json_tuple vs SerDe', 'Bad-record quarantine', 'Runs in your browser (Python)'],
)

MAIN = '''# get_json_object in Python: follow a path through nested JSON, NULL (None) if anything is missing
import json
line = '{"event":"order_placed","user":{"id":1376,"city":"Chennai"},"items":[{"dish":"Rajma Chawal","qty":3,"price":120},{"dish":"Chai","qty":2,"price":20}]}'

def get(line, path):                     # path like ["user", "city"] or ["items", 0, "dish"]
    try:
        node = json.loads(line)
    except ValueError:
        return None                      # broken JSON -> NULL
    for step in path:
        try:
            node = node[step]
        except (KeyError, IndexError, TypeError):
            return None                  # missing key or index -> NULL
    return node

print(get(line, ["user", "city"]))       # $.user.city
print(get(line, ["items", 0, "dish"]))   # $.items[0].dish
print(get(line, ["User", "id"]))         # $.User.id  (keys are case-sensitive)
print(get(line[:-15], ["event"]))        # truncated line
'''
RUN = dict(
    heading='Run the code: paths, tuples and bad lines',
    intro='<p>These programs mimic Hive’s JSON functions with Python’s json module, on the same kind of events used in the lab. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('        node = json.loads(line)', 'Like get_json_object, this parses the whole line on every call. Hive does the same for each call, which is why parsing once into ORC is faster.'),
        ('            return None                  # missing key or index -> NULL', 'Hive also returns NULL here instead of raising an error.'),
    ],
    tasks=[
        dict(label='1 · Follow paths', hint='Press <b>Run</b>: Chennai, Rajma Chawal, None, None, matching Steps 2 and 3.', code=None),
        dict(label='2 · [*] returns all elements', hint='<b>Predict first:</b> what does $.items[*].dish give? In Hive it is JSON text.',
             code='''import json
line = '{"items":[{"dish":"Rajma Chawal"},{"dish":"Chai"},{"dish":"Idli"}]}'
dishes = [it["dish"] for it in json.loads(line)["items"]]
print(json.dumps(dishes, separators=(",", ":")))
'''),
        dict(label='3 · json_tuple: one parse, several keys', hint='The nested user object comes back as text and needs a second parse.',
             code='''import json
line = '{"event":"order_placed","ts":"2026-10-03T10:02:00+05:30","user":{"id":1376,"city":"Chennai"}}'
doc = json.loads(line)                                  # parse once
event, ts, user_json = doc.get("event"), doc.get("ts"), json.dumps(doc.get("user"))
u = json.loads(user_json)                               # second json_tuple
print(event, ts, u["id"], u["city"])
print("dotted key:", doc.get("user.id"))                # json_tuple(line, 'user.id') -> NULL
'''),
        dict(label='4 · Quarantine bad lines', hint='Split lines into good and bad, as in Step 7.',
             code='''import json
lines = ['{"event":"app_open"}', '{"event":"search","query":"dosa"}', '{"event":"order_placed","user":{"id":5']
good, bad = [], []
for l in lines:
    try:
        json.loads(l); good.append(l)
    except ValueError:
        bad.append(l)
print(len(good), "good,", len(bad), "bad:", bad)
'''),
        dict(label='5 · Spot the error', hint='The strict reader stops at the broken line, like the JsonSerDe scan. Make it skip bad lines and count them instead.', expect='error',
             code='''import json
lines = ['{"event":"app_open"}', '{"event":"order_placed","user":{"id":5', '{"event":"search"}']
events = [json.loads(l)["event"] for l in lines]       # strict, like the SerDe
assert len(events) == 2
print(events)
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: unknown keys, JSON functions and coupons',
    intro='<p>Three more checks for Beeline on the events data. <b>Outputs are real</b>, from Hive 4.2.1.</p>',
    items=[
        dict(title='1 · Unknown and missing keys in a SerDe table', cmd="CREATE EXTERNAL TABLE events_min (event STRING, payment STRING)\nROW FORMAT SERDE 'org.apache.hive.hcatalog.data.JsonSerDe' LOCATION '/data/events_good';\nSELECT event, payment, COUNT(*) AS n FROM events_min GROUP BY event, payment ORDER BY n DESC;", file='Beeline',
             output=capf('l43_unknown.txt'),
             note='Keys in the JSON that are not columns (user, items, ts…) are ignored. A column with no matching key (payment) is NULL. This is what makes adding fields to events safe.'),
        dict(title='2 · Which JSON functions does your Hive have?', cmd="SHOW FUNCTIONS LIKE '%json%';\nDESCRIBE FUNCTION json_read;", file='Beeline',
             output=capf('l43_fns.txt') + '\n' + '\n'.join(capf('l43_desc.txt').split('\n')[:5]),
             note='Hive 4 adds json_read (JSON text to a typed value), to_json and parse_json for the VARIANT type, alongside the classic get_json_object and json_tuple. The st_* functions are for geographic data.'),
        dict(title='3 · Coupons, including JSON null', cmd="SELECT coalesce(coupon, '(null)') AS coupon, COUNT(*) AS n\nFROM events_clean WHERE event = 'coupon_applied'\nGROUP BY coupon ORDER BY n DESC;", file='Beeline',
             output=capf('l43_coupon.txt'),
             note='A JSON <code>null</code> and a missing key both arrive as SQL NULL. 142 coupon events had no code: worth asking the app team why.'),
    ],
)

TRACE = dict(
    heading='Walking the path $.items[0].dish',
    intro='<p>The path is followed one step at a time. Watch <code>node</code> get smaller.</p>',
    code='''import json
node = json.loads('{"items":[{"dish":"Idli","qty":2}]}')
for step in ["items", 0, "dish"]:
    node = node[step]
print(node)
''',
    notes={2: 'Parse :: The text becomes nested dicts and lists.', 4: 'Step :: items → list, 0 → first item, dish → its value.'},
)

WORKED_INTRO = 'Three JSON jobs: revenue from item lists, campaign parameters from URLs, and checking a feed before loading.'
EXAMPLES = [
    dict(level='b', tag='Analytics · items array', title='Revenue of one order',
         problem='<p>Order event items: Rajma Chawal 3 × 120, Chai 2 × 20, Idli 3 × 60. In Hive: <code>SUM(it.qty * it.price)</code> after <code>LATERAL VIEW inline(items) it</code>.</p>',
         inp='items of the real event from user 1376',
         approach=['Turn each item into a row (inline).', 'Multiply qty by price.', 'Sum per order.'],
         code='''items = [{"dish": "Rajma Chawal", "qty": 3, "price": 120},
         {"dish": "Chai", "qty": 2, "price": 20},
         {"dish": "Idli", "qty": 3, "price": 60}]
lines = [(it["dish"], it["qty"] * it["price"]) for it in items]
print(lines, "total:", sum(v for _, v in lines))
''', notes={4: 'Line total :: qty × price, as in the real Step 8 output.'},
         tryit='The real query listed 360, 40 and 180 for these three items. Total 580.'),
    dict(level='i', tag='Marketing · parse_url', title='Which campaign brought the visit?',
         problem='<p>From landing URLs, extract the host, path and the <code>src</code> parameter, as <code>parse_url_tuple(url, \'HOST\', \'PATH\', \'QUERY:src\')</code>.</p>',
         inp='https://tiffingo.in/menu/pune?dish=poha&amp;src=ad',
         approach=['Split the URL into parts.', 'Read query parameters by name.', 'Count visits per src.'],
         code='''url = "https://tiffingo.in/menu/pune?dish=poha&src=ad"
rest = url.split("://", 1)[1]
host, _, tail = rest.partition("/")
path, _, query = tail.partition("?")
params = dict(p.split("=", 1) for p in query.split("&") if p)
print(host, "/" + path, params.get("src"), params.get("dish"))
''', notes={5: 'QUERY:key :: Like parse_url(url, \'QUERY\', \'src\').'},
         tryit='Real Hive gave tiffingo.in, /menu/pune and ad. A URL without src gives NULL, which you can report as “direct”.'),
    dict(level='a', tag='Data quality · validation', title='Validate a feed before loading',
         problem='<p>Before pointing a JsonSerDe table at a folder, check each line: valid JSON, has <code>event</code>, and <code>items[].qty</code> is an integer. Route failures to quarantine.</p>',
         inp='four sample lines, two of them bad',
         approach=['Try to parse each line.', 'Check required keys and types.', 'Count good and bad; stop if the bad rate is too high.'],
         code='''import json
lines = ['{"event":"order_placed","items":[{"qty":2}]}', '{"event":"search"}',
         '{"event":"order_placed","items":[{"qty":"two"}]}', '{"event":"app_op']
good = bad = 0
for l in lines:
    try:
        d = json.loads(l)
        ok = "event" in d and all(isinstance(i.get("qty"), int) for i in d.get("items", []))
    except ValueError:
        ok = False
    good, bad = (good + 1, bad) if ok else (good, bad + 1)
print(good, "good,", bad, "bad,", f"{bad / len(lines):.0%} bad")
''', notes={6: 'Type check :: Catches "qty":"two" before it becomes NULL or an error in Hive.'},
         tryit='In Hive, the same checks can be written on the raw table with get_json_object and a regular expression, before the typed table is used.'),
]

QUIZ = mix([
    dict(q='Beginner: Which path reads the city inside the user object?', options=['$user.city', '$.user.city', 'user->city', '$.city.user'], answer=1,
         why='$ is the root, then .user, then .city.'),
    dict(q='Beginner: get_json_object on invalid JSON returns…', options=['An error', 'NULL', 'An empty string', '0'], answer=1,
         why='The truncated line gave NULL; that is how we found it.'),
    dict(q='Beginner: What type does get_json_object return?', options=['The JSON type (int, array…)', 'Always STRING', 'BINARY', 'MAP'], answer=1,
         why='Even lists come back as JSON text, e.g. ["Poha","Idli"].'),
    dict(q='Intermediate: json_tuple(line, \'user.id\') returned NULL. Why?', options=['user is reserved', 'json_tuple takes top-level key names, not paths', 'IDs must be strings', 'Needs GROUP BY'], answer=1,
         why='Read user first, then call json_tuple again on it.'),
    dict(q='Intermediate: A JsonSerDe table: LIMIT 3 worked, COUNT(*) failed. Most likely?', options=['Too much data', 'A malformed line later in the file', 'Wrong LOCATION', 'Metastore down'], answer=1,
         why='LIMIT read only the first lines; the full scan reached line 1,500 (JsonEOFException).'),
    dict(q='Intermediate: Why does `user`.city need back-ticks?', options=['Dots need quotes', 'USER is a reserved word in HiveQL', 'Structs always need them', 'They do not'], answer=1,
         why='Without them: “cannot recognize input near \'user\' \'.\' \'city\'”.'),
    dict(q='Advanced: Best production pattern for a JSON feed queried daily?', options=['get_json_object in every report', 'Raw STRING table → quarantine bad lines → CTAS into ORC → reports', 'Convert to CSV by hand', 'Load into the metastore'], answer=1,
         why='Parse once, keep raw data, isolate bad records.'),
    dict(q='Advanced: A new key appears in the JSON. What happens to an existing JsonSerDe table?', options=['Queries fail', 'The key is ignored until you add a column', 'Hive adds the column automatically', 'All columns become NULL'], answer=1,
         why='Unknown keys are ignored; columns without keys are NULL (tested with events_min).'),
])

REVISION = [
    '<b>Land raw:</b> <code>CREATE EXTERNAL TABLE raw (line STRING) LOCATION …</code>: never fails.',
    '<b>get_json_object(json, \'$.a.b[0].c\')</b>: one value, STRING result, NULL on missing key, wrong case or bad JSON. <code>[*]</code> returns JSON text.',
    'Path limits: no <code>..</code>, no filters <code>?()</code>, no slices or unions.',
    '<b>json_tuple(json, \'k1\', \'k2\')</b> with LATERAL VIEW: one parse, top-level keys only; nest a second json_tuple for objects.',
    '<b>JsonSerDe</b> (<code>org.apache.hive.hcatalog.data.JsonSerDe</code>): typed STRUCT/ARRAY columns; unknown keys ignored, missing keys NULL; <b>a malformed line fails the scan</b>.',
    'Reserved words as JSON keys (<code>user</code>) need back-ticks.',
    '<b>Pattern:</b> raw → quarantine (good/bad folders) → CTAS ORC → reports. Track the bad-line rate.',
    '<b>Others:</b> parse_url / parse_url_tuple (HOST, PATH, QUERY:key), xpath / xpath_string / xpath_int for XML. Hive 4: json_read, to_json, parse_json, variant_get.',
]
FAQ = [
    ('Does Hive need one JSON object per line?', 'Yes. Text-based tables split records at line breaks, so a pretty-printed JSON document spread over many lines cannot be read row by row. Convert such files to JSON Lines (one compact object per line) before loading.'),
    ('get_json_object or json_tuple: which is faster?', 'json_tuple parses the document once for all the keys you ask for, while each get_json_object call parses it again. For many top-level fields json_tuple is cheaper. For a one-off nested field get_json_object is simpler. For repeated queries, parse once into ORC and neither matters.'),
    ('Can the JsonSerDe skip bad lines?', 'The Hive JsonSerDe in our lab failed the whole task on one malformed line. Other SerDes (such as the third-party OpenX JSON SerDe) offer an option to ignore malformed JSON, but the safest pattern does not depend on it: validate and quarantine with a raw STRING table first.'),
    ('What about json_read in Hive 4?', 'json_read(json, \'array&lt;struct&lt;…&gt;&gt;\') converts JSON text straight into a typed value and worked in a small fetch-mode query in our lab. Inside a Tez job on the official Docker image it failed while serialising the plan (a Java 17 module-access error, “Error caching map.xml”). It may work on your cluster; test it before relying on it.'),
    ('How should I handle XML?', 'For a few fields from XML strings, the xpath family is enough. For large XML feeds, convert them to JSON or Avro/Parquet upstream (Spark, NiFi) and load those; XML SerDes exist but are third-party and slower.'),
]

PRACTICE_INTRO = 'Programs that reproduce Hive’s JSON behaviour on real-shaped events, with the HiveQL in each explanation.'
PROBLEMS = [
    dict(level='easy', title='Read a nested field', stmt='Return the city of the user in an event.', inp='{"user":{"id":1279,"city":"Delhi"}}',
         code='''import json
print(json.loads('{"user":{"id":1279,"city":"Delhi"}}')["user"]["city"])
''', explain="get_json_object(line, '$.user.city') = Delhi."),
    dict(level='easy', title='Missing key is NULL', stmt='Read coupon from an order event that has no coupon.', inp='{"event":"order_placed"}',
         code='''import json
print(json.loads('{"event":"order_placed"}').get("coupon"))
''', explain="None, like NULL from get_json_object(line, '$.coupon')."),
    dict(level='easy', title='Count bad lines', stmt='How many of these lines are not valid JSON?', inp='three lines',
         code='''import json
lines = ['{"a":1}', '{"a":', '{"b":2}']
bad = 0
for l in lines:
    try: json.loads(l)
    except ValueError: bad += 1
print(bad)
''', explain="1. In Hive: SUM(IF(get_json_object(line, '$.a') IS NULL, 1, 0)), as in Step 4 (real: 1 of 2,000)."),
    dict(level='medium', title='All dishes as text', stmt='Build the $.items[*].dish result for an order.', inp='items Poha, Idli',
         code='''import json
items = [{"dish": "Poha"}, {"dish": "Idli"}]
print(json.dumps([i["dish"] for i in items], separators=(",", ":")))
''', explain='["Poha","Idli"], exactly the real output. Note it is a string; use the SerDe or json_read for a real array.'),
    dict(level='medium', title='Event mix', stmt='Using the real counts, what share of events are orders?', inp='order_placed 779, coupon_applied 411, search 410, app_open 399',
         code='''c = {"order_placed": 779, "coupon_applied": 411, "search": 410, "app_open": 399}
print(f"{c['order_placed'] / sum(c.values()):.1%} of {sum(c.values())} parsed events")
''', explain='39.0% of 1,999 parsed events (the 2,000th line was broken).'),
    dict(level='medium', title='Query parameter', stmt='Extract dish from a URL query string.', inp='?dish=poha&src=ad',
         code='''params = dict(p.split("=", 1) for p in "dish=poha&src=ad".split("&"))
print(params["dish"])
''', explain="parse_url(url, 'QUERY', 'dish') = poha; parse_url_tuple(url, 'QUERY:dish') too."),
    dict(level='business', title='Revenue leader', stmt='From the real revenue per city, how far ahead is Chennai of Bengaluru, in percent?', inp='Chennai 39,330 · Bengaluru 28,655',
         code='''print(f"{(39330 - 28655) / 28655:.1%} higher")
''', explain='About 37.3% higher in this generated sample. Real conclusions need the full event history.'),
    dict(level='business', title='Bad-line alert', stmt='A day has 1,250,000 events and 1,800 bad lines. Is it above a 0.1% alert threshold?', inp='illustrative daily counts',
         code='''rate = 1800 / 1_250_000
print(f"{rate:.3%}", "ALERT" if rate > 0.001 else "ok")
''', explain='0.144%: above 0.1%, so alert the app team while the good lines still load.'),
]

SCN_INTRO = 'JSON questions test whether you know the functions and the production pattern, not just the syntax.'
SCENARIOS = (
    scn('Any company · HiveQL', 'Fresher', '“Extract fields from a JSON column”',
        'A table has a STRING column payload with JSON like {"user":{"id":7},"amount":250}. Return user id and amount.',
        'do you know get_json_object paths?',
        '''<pre>SELECT CAST(get_json_object(payload, '$.user.id') AS INT) AS user_id,
       CAST(get_json_object(payload, '$.amount') AS DECIMAL(10,2)) AS amount
FROM payments;</pre>
        <p>Cast the results: get_json_object always returns STRING.</p>''', 'Forgetting the $ root or leaving amounts as strings.') +
    scn('Data engineering', 'Mid-level', 'The JSON job failed overnight',
        'A JsonSerDe table query fails with “Hive Runtime Error while processing row … JsonEOFException”.',
        'can you isolate bad records?',
        '''<ol>
          <li>Query the folder through a raw STRING table and find lines where a required key parses to NULL.</li>
          <li>Write good and bad lines to separate folders; point the typed table at the good one.</li>
          <li>Report the bad-line rate and fix the producer (here: a truncated upload).</li>
        </ol>''', 'Deleting files until the error goes away.') +
    scn('Analytics engineering', 'Mid-level', 'Dashboards on raw JSON are slow',
        'Ten reports each call get_json_object six times on a billion-row raw table.',
        'do you know to parse once?',
        '''<ul>
          <li>Build a typed ORC table with CTAS (or INSERT OVERWRITE per date partition) from the SerDe or json_tuple.</li>
          <li>Point the reports at it; keep the raw table for reprocessing.</li>
          <li>Partition by event date (Module 5) so daily reports read one folder.</li>
        </ul>''', 'Adding more nodes while every query keeps re-parsing JSON.') +
    scn('Data platform', 'Senior', 'Design ingestion for evolving app events',
        'Event JSON changes every app release. Design the Hive side.',
        'can you plan for schema drift?',
        '''<ul>
          <li>Raw zone: STRING or JsonSerDe table with only stable fields; unknown keys are ignored, missing ones are NULL.</li>
          <li>Event version field and an agreed JSON Schema; additive changes only.</li>
          <li>Clean zone in ORC or Iceberg (Module 7); ALTER TABLE ADD COLUMNS for new fields; validate types in the quarantine step.</li>
        </ul>''', 'Recreating tables by hand after every release.')
)
