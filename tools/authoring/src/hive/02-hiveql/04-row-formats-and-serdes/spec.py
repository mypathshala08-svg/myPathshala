import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
BODY = body(HERE)
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep

META = dict(
    module='02-hiveql', lesson='04-row-formats-and-serdes', n='2.4',
    module_label='Module 2 · Tables and data',
    title='Row formats and SerDes: CSV, JSON and logs',
    desc='How Hive turns bytes into columns: row formats, SerDes and SERDEPROPERTIES. LazySimpleSerDe and quoted commas, OpenCSVSerde (all columns as STRING), JsonSerDe with STORED AS JSONFILE (nested fields, malformed lines, wrong types), RegexSerDe for web server logs, NULL markers and the raw-to-curated pattern. Real outputs from Hive 4.2.1.',
    og_desc='A quoted comma, a broken JSON line and a web server log: three files, three SerDes, real Hive 4 behaviour.',
    minutes=32, level='Beginner → Advanced',
    lead='Every Hive table has a translator between the file and the columns: its <b>SerDe</b>. Pick the default one for a CSV with quoted commas and the columns shift. Pick OpenCSVSerde and the columns are right but every value is a string. JSON maps neatly to nested types, until one broken line stops the whole query. This lesson reads a menu CSV, restaurant JSON and a web server log with the right SerDe each, with <b>real Hive 4.2.1 output</b>.',
    chips=['Real Hive 4.2.1 outputs', 'CSV · JSON · Regex', 'Log analytics scenario', 'Runs in your browser (Python)'],
)

MAIN = '''# Two readers for the same CSV line
import csv, io
line = '1,"Dal, Rice combo",120,Thali'

naive = line.split(",")                      # like LazySimpleSerDe: split at every comma
proper = next(csv.reader(io.StringIO(line)))  # like OpenCSVSerde: respects quotes

print("naive :", naive, "->", len(naive), "pieces")
print("proper:", proper, "->", len(proper), "pieces")
print("price (proper) is a", type(proper[2]).__name__)   # OpenCSVSerde also returns strings
'''
RUN = dict(
    heading='Run the code: write tiny SerDes in Python',
    intro='<p>A SerDe is just a function from a line to columns. These programs build the four you met (delimited, CSV, JSON, regex) and show the same edge cases as the lab. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('naive = line.split(",")                      # like LazySimpleSerDe: split at every comma', 'Five pieces for four columns: the quoted comma was treated as a separator.'),
        ('proper = next(csv.reader(io.StringIO(line)))  # like OpenCSVSerde: respects quotes', 'A real CSV parser keeps <code>Dal, Rice combo</code> together.'),
        ('print("price (proper) is a", type(proper[2]).__name__)   # OpenCSVSerde also returns strings', 'Just like OpenCSVSerde, the CSV parser gives text; converting to a number is your job.'),
    ],
    tasks=[
        dict(label='1 · Two CSV readers', hint='Press <b>Run</b>. Then try the line <code>3,"Paneer ""Special"" Thali",220,Thali</code>.', code=None),
        dict(label='2 · A JSON reader', hint='<b>Predict first:</b> what does the reader return for the missing key and the extra key? Then break the JSON by deleting the final <code>}</code>.',
             code='''import json
columns = ["restaurant_id", "name", "city"]
line = '{"restaurant_id": 900, "name": "Good Line", "extra_field": 1}'
obj = {k.lower(): v for k, v in json.loads(line).items()}   # keys matched ignoring case
row = [obj.get(c) for c in columns]                          # missing key -> None (NULL)
print(row)
'''),
        dict(label='3 · A regex reader for logs', hint='Each <code>(…)</code> group becomes a column. The health-check line does not match, so all columns are None, as in Hive.',
             code='''import re
pattern = re.compile(r'^(\\S+) \\S+ \\S+ \\[([^\\]]+)\\] "(\\S+) (\\S+) \\S+" (\\d{3}) (\\d+)$')
lines = ['10.165.39.83 - - [01/Oct/2026:00:00:00 +0530] "GET /api/orders HTTP/1.1" 200 7484',
         'health-check ping from load balancer']
for ln in lines:
    m = pattern.match(ln)
    print(m.groups() if m else (None,) * 6)
'''),
        dict(label='4 · NULL markers', hint='Delimited text uses <code>\\N</code> for NULL; an empty field stays an empty string. Change <code>null_marker</code> to <code>"NA"</code>.',
             code='''null_marker = "\\\\N"
rows = ["1,Pune,\\\\N", "2,,150", "3,NA,90"]
for r in rows:
    print([None if v == null_marker else v for v in r.split(",")])
'''),
        dict(label='5 · Spot the error', hint='This “SerDe” assumes every line has 4 fields. A line with a quoted comma has 5 and the check fails. Fix it by using <code>csv.reader</code>.', expect='error',
             code='''lines = ['2,Poha,40,Breakfast', '1,"Dal, Rice combo",120,Thali']
for ln in lines:
    parts = ln.split(",")
    assert len(parts) == 4, f"{len(parts)} fields in: {ln}"
    print(parts)
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: inspect and tune SerDes',
    intro='<p>Run these in Beeline on the lab after creating the tables from the steps. <b>The outputs are real</b>, from Hive 4.2.1.</p>',
    items=[
        dict(title='1 · Which SerDe did STORED AS JSONFILE choose?', cmd='SHOW CREATE TABLE restaurants;', file='Beeline',
             output='''CREATE EXTERNAL TABLE `restaurants`(
  `restaurant_id` int COMMENT 'from deserializer',
  …
  `tags` array<string> COMMENT 'from deserializer',
  `contact` struct<`phone`:string, `email`:string> COMMENT 'from deserializer')
ROW FORMAT SERDE
  'org.apache.hadoop.hive.serde2.JsonSerDe'
STORED AS INPUTFORMAT
  'org.apache.hadoop.mapred.TextInputFormat'
OUTPUTFORMAT
  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION
  'file:/data/tiffingo/restaurants'
(trimmed)''',
             note='<code>STORED AS JSONFILE</code> is shorthand for the JsonSerDe plus text input/output formats. “from deserializer” means the SerDe supplies the column information.'),
        dict(title='2 · Group restaurants by cuisine from JSON', cmd='SELECT cuisine, COUNT(*) AS kitchens, ROUND(AVG(rating),2) AS avg_rating\nFROM restaurants GROUP BY cuisine ORDER BY kitchens DESC LIMIT 4;', file='Beeline',
             output='''+---------------+-----------+-------------+
|    cuisine    | kitchens  | avg_rating  |
+---------------+-----------+-------------+
| South Indian  | 20        | 4.03        |
| Punjabi       | 17        | 4.16        |
| Bengali       | 15        | 4.07        |
| Chinese       | 15        | 3.93        |
+---------------+-----------+-------------+''',
             note='Once the SerDe has done its work, JSON data is queried like any other table.'),
        dict(title='3 · Change the NULL marker', cmd="-- n.csv:  1,Pune,\\N / 2,,150 / 3,NA,90\nSELECT id, city, city IS NULL AS city_null, amount FROM nulls_demo;\nALTER TABLE nulls_demo SET TBLPROPERTIES ('serialization.null.format'='NA');\nSELECT id, city, city IS NULL AS city_null, amount FROM nulls_demo;", file='Beeline',
             output=open(CAP + 'l24_nulls.txt').read().rstrip(),
             note='Before the change <code>NA</code> is just text; after it, <code>NA</code> is NULL. The empty city in row 2 is an empty string, not NULL, in both cases. (Row 1’s amount is NULL because <code>\\N</code> or text is not an INT.)'),
    ],
)

TRACE = dict(
    heading='A regex SerDe reading one log line',
    intro='<p>Watch the pattern match the line and each group become a column value, then a type conversion for status and bytes.</p>',
    code='''import re
line = '10.114.24.225 - - [01/Oct/2026:00:00:37 +0530] "GET /cart HTTP/1.1" 304 7687'
m = re.match(r'^(\\S+) \\S+ \\S+ \\[([^\\]]+)\\] "(\\S+) (\\S+) \\S+" (\\d{3}) (\\d+)$', line)
ip, ts, method, path, status, size = m.groups()
row = {"ip": ip, "path": path, "status": int(status), "bytes": int(size)}
print(row)
''',
    notes={3: 'Match :: The whole line must match; otherwise every column would be NULL.', 5: 'Types :: Groups are text; INT columns convert them.'},
)

WORKED_INTRO = 'Three file problems from TiffinGo’s data team: checking a CSV before choosing a SerDe, building a log report, and validating JSON before it reaches Hive.'
EXAMPLES = [
    dict(level='b', tag='Ingestion · checks', title='Does this CSV need OpenCSVSerde?',
         problem='<p>Before creating a table, check a sample file: count lines whose number of comma-separated pieces differs from the header, and lines that contain a double quote.</p>',
         inp='item_id,name,price,category / 1,"Dal, Rice combo",120,Thali / 2,Poha,40,Breakfast / 3,"Paneer ""Special"" Thali",220,Thali / 4,Masala Chai,15,Beverage',
         approach=['Split the header to get the expected count.', 'For each data line, compare the naive split count.', 'Count quoted lines too; any hit means a quote-aware SerDe is needed.'],
         code='''sample = """item_id,name,price,category
1,"Dal, Rice combo",120,Thali
2,Poha,40,Breakfast
3,"Paneer ""Special"" Thali",220,Thali
4,Masala Chai,15,Beverage"""
lines = sample.splitlines()
expected = len(lines[0].split(","))
bad = [l for l in lines[1:] if len(l.split(",")) != expected]
quoted = [l for l in lines[1:] if '"' in l]
print("lines with wrong field count:", len(bad))
print("lines with quotes           :", len(quoted))
print("use OpenCSVSerde" if bad or quoted else "ROW FORMAT DELIMITED is enough")
''', notes={8: 'Check :: A naive split that gives too many fields means quoted separators.'},
         tryit='Line 3 has quotes but still 4 pieces, so only the quote check catches it; with the default SerDe its name would keep the doubled quotes. Check both.'),
    dict(level='i', tag='Logs · report', title='Error rate per page from log lines',
         problem='<p>From sample access-log lines, compute requests and the share of 5xx errors per path, using a regex like the RegexSerDe table.</p>',
         inp='5 log lines in the lab format',
         approach=['Match each line and pull path and status.', 'Count totals and errors per path in dictionaries.', 'Print the error rate.'],
         code='''import re
pat = re.compile(r'"\\S+ (\\S+) \\S+" (\\d{3}) ')
lines = ['10.1.1.1 - - [x] "GET /checkout HTTP/1.1" 500 10',
         '10.1.1.2 - - [x] "GET /checkout HTTP/1.1" 200 10',
         '10.1.1.3 - - [x] "GET /menu HTTP/1.1" 200 10',
         '10.1.1.4 - - [x] "GET /checkout HTTP/1.1" 502 10',
         '10.1.1.5 - - [x] "GET /menu HTTP/1.1" 404 10']
total, errors = {}, {}
for ln in lines:
    path, status = pat.search(ln).groups()
    total[path] = total.get(path, 0) + 1
    if status.startswith("5"):
        errors[path] = errors.get(path, 0) + 1
for p in total:
    print(f"{p:10} {total[p]} requests, {errors.get(p, 0) / total[p]:.0%} 5xx")
''', notes={10: 'Count :: The same GROUP BY path you would write in Hive.'},
         tryit='The Hive version: SELECT path, COUNT(*), AVG(CASE WHEN status >= 500 THEN 1 ELSE 0 END) FROM access_log GROUP BY path. 404 is a client error, not counted as 5xx.'),
    dict(level='a', tag='Quality · JSON gate', title='Validate JSON lines before loading',
         problem='<p>Build a gate that sorts incoming JSON lines into “good” and “quarantine”: a line must parse, and <code>restaurant_id</code> must be an integer. This prevents both failures seen in the lab (a whole-query error and a silent 0).</p>',
         inp='4 lines: valid; missing }; restaurant_id "nine-o-two"; valid without city',
         approach=['Try json.loads; on error, quarantine.', 'Check the type of restaurant_id.', 'Only good lines go to the Hive folder.'],
         code='''import json
lines = ['{"restaurant_id": 900, "name": "Good Line", "city": "Pune"}',
         '{"restaurant_id": 901, "name": "Broken Line", "city": "Pune"',
         '{"restaurant_id": "nine-o-two", "name": "Bad Type"}',
         '{"restaurant_id": 903, "name": "No City"}']
good, quarantine = [], []
for ln in lines:
    try:
        obj = json.loads(ln)
    except json.JSONDecodeError as e:
        quarantine.append(("parse error", ln[:30])); continue
    if not isinstance(obj.get("restaurant_id"), int):
        quarantine.append(("bad id type", ln[:30])); continue
    good.append(obj["restaurant_id"])
print("good:", good)
for reason, text in quarantine:
    print("quarantine:", reason, "|", text)
''', notes={10: 'Gate :: A broken line is set aside instead of failing tonight’s query.'},
         tryit='The missing city is allowed (it becomes NULL). Decide with the business which fields are mandatory and add checks for them.'),
]

QUIZ = mix([
    dict(q='Beginner: What does SerDe stand for?', options=['Server/Desktop', 'Serializer/Deserializer', 'Sequential Decoder', 'Service Definition'], answer=1,
         why='It converts rows to bytes (serialize, on write) and bytes to rows (deserialize, on read).'),
    dict(q='Beginner: Which SerDe does ROW FORMAT DELIMITED use?', options=['OpenCSVSerde', 'LazySimpleSerDe', 'JsonSerDe', 'RegexSerDe'], answer=1,
         why='LazySimpleSerDe is the default for delimited text.'),
    dict(q='Beginner: A CSV has "Dal, Rice combo" in quotes. Which SerDe keeps it as one value?', options=['LazySimpleSerDe', 'OpenCSVSerde', 'RegexSerDe with no groups', 'None can'], answer=1,
         why='OpenCSVSerde handles quote characters; the default split at the inner comma.'),
    dict(q='Intermediate: With OpenCSVSerde and price declared INT, what did typeof(price) return?', options=['int', 'bigint', 'string', 'decimal'], answer=2,
         why='OpenCSVSerde returns every column as a string; SUM(price) gave 395.0.'),
    dict(q='Intermediate: What happens to a log line that does not match a RegexSerDe pattern?', options=['The query fails', 'The line is skipped silently and not counted', 'It becomes a row where every column is NULL', 'It is put in the first column'], answer=2,
         why='Our health-check line produced NULL, NULL, NULL.'),
    dict(q='Intermediate: In delimited text, what is the default marker for NULL?', options=['NULL', 'NA', '\\N', 'An empty field'], answer=2,
         why="\\N, changeable with serialization.null.format. An empty field is an empty string."),
    dict(q='Advanced: One JSON line is missing its closing brace. What did Hive 4.2.1 do?', options=['Returned NULLs for that row', 'Skipped the row', 'Failed the whole query with JsonEOFException', 'Repaired the JSON'], answer=2,
         why='The JsonSerDe threw an exception and the query failed; validate JSON at ingestion.'),
    dict(q='Advanced: Why are backslashes doubled in the input.regex of a RegexSerDe DDL?', options=['Regex needs two backslashes', 'HiveQL string literals treat backslash as an escape, so \\\\S in DDL becomes \\S in the regex', 'It makes matching faster', 'It is a Windows path rule'], answer=1,
         why='The string literal removes one level of escaping before the SerDe sees the pattern.'),
])

REVISION = [
    '<b>File format</b> (InputFormat) cuts a file into records; <b>SerDe</b> cuts a record into columns (and back on write).',
    '<b>LazySimpleSerDe</b>: default for <code>ROW FORMAT DELIMITED</code>; no quote handling; <code>\\N</code> = NULL; empty = \'\'.',
    "<b>OpenCSVSerde</b>: <code>ROW FORMAT SERDE '…OpenCSVSerde' WITH SERDEPROPERTIES ('separatorChar', 'quoteChar', 'escapeChar')</code>; returns all columns as STRING.",
    '<b>JsonSerDe</b>: <code>STORED AS JSONFILE</code>; keys → columns (case-insensitive); nested → STRUCT/MAP/ARRAY; extra keys ignored; missing → NULL; malformed line fails the query; wrong type gave 0.',
    "<b>RegexSerDe</b>: <code>'input.regex'</code>, one group per column; non-matching lines → all NULL; double backslashes in DDL.",
    "<code>serialization.null.format</code> changes the NULL marker; <code>skip.header.line.count</code> skips headers.",
    'Pattern: raw table with the right SerDe → curated ORC/Parquet table with real types; count rejected values.',
    'Binary formats (ORC, Parquet, Avro) bring their own SerDes via <code>STORED AS</code> (Module 6).',
]
FAQ = [
    ('What is the difference between a SerDe and a file format?', 'The file format (input and output format classes) decides how a file is split into records and how records are written into files; for text that means lines. The SerDe decides how one record is turned into columns and back. For text tables you can combine the text format with different SerDes (LazySimple, OpenCSV, JSON, Regex); binary formats such as ORC and Parquet come with matching SerDes.'),
    ('Why does OpenCSVSerde return everything as a string?', 'Its parser produces text values and the SerDe exposes them as strings, regardless of the declared types; Hive then converts implicitly when you compute (string to DOUBLE), which is why SUM(price) gave 395.0. Cast explicitly in queries or, better, copy the data once into a typed ORC table.'),
    ('Can Hive skip bad JSON lines instead of failing?', 'Some JSON SerDes and settings can ignore malformed records, depending on version and SerDe. In our Hive 4.2.1 test the built-in JsonSerDe failed the query. The robust approach is to validate and quarantine bad lines at ingestion so the table only ever sees valid JSON.'),
    ('Is RegexSerDe fast enough for big logs?', 'Regular expressions cost CPU on every read, and logs are large text. RegexSerDe tables are excellent for exploring and incident work; for repeated analysis, convert the parsed logs daily into a partitioned ORC table, so the regex runs once per line instead of once per query.'),
    ('Can I write data with RegexSerDe or OpenCSVSerde?', 'RegexSerDe is meant for reading; writing through it is not supported in general. OpenCSVSerde can write, quoting values as needed, but all values are strings. For tables you write to, prefer ORC or Parquet, or delimited text with a separator that never appears in the data.'),
]

PRACTICE_INTRO = 'Programs that act like SerDes: splitting, quoting, parsing JSON and matching patterns.'
PROBLEMS = [
    dict(level='easy', title='Split with a custom delimiter', stmt="Split '5|Misal Pav|80|Breakfast' on '|' and convert the price to an integer.", inp='5|Misal Pav|80|Breakfast',
         code='''parts = "5|Misal Pav|80|Breakfast".split("|")
parts[2] = int(parts[2])
print(parts)
''', explain="Hive: ROW FORMAT DELIMITED FIELDS TERMINATED BY '|'. A pipe rarely appears in names, so it is a safer separator than a comma."),
    dict(level='easy', title='Count fields', stmt='Count fields in the line 1,"Dal, Rice combo",120,Thali with a naive split and with a CSV reader.', inp='1,"Dal, Rice combo",120,Thali',
         code='''import csv, io
line = '1,"Dal, Rice combo",120,Thali'
print(len(line.split(",")), len(next(csv.reader(io.StringIO(line)))))
''', explain='5 and 4. The difference is exactly the quoted comma.'),
    dict(level='easy', title='Missing JSON key', stmt='Read {"name": "No Id", "city": "Thane"} into columns restaurant_id, name, city.', inp='{"name": "No Id", "city": "Thane"}',
         code='''import json
obj = json.loads('{"name": "No Id", "city": "Thane"}')
print([obj.get(c) for c in ["restaurant_id", "name", "city"]])
''', explain='[None, \'No Id\', \'Thane\']: a missing key becomes NULL, as in the lab.'),
    dict(level='medium', title='Unmatched log lines', stmt='Count how many of these lines match a pattern that needs an IP at the start and a 3-digit status after the quoted request.', inp='3 lines, one health check',
         code='''import re
pat = re.compile(r'^\\d+\\.\\d+\\.\\d+\\.\\d+ .*" (\\d{3}) ')
lines = ['10.0.0.1 - - [t] "GET / HTTP/1.1" 200 5', 'health-check ping', '10.0.0.2 - - [t] "GET /x HTTP/1.1" 500 9']
matched = sum(1 for l in lines if pat.match(l))
print("matched", matched, "| would be all-NULL rows:", len(lines) - matched)
''', explain='2 matched, 1 all-NULL row. Track this number: a sudden jump means the log format changed.'),
    dict(level='medium', title='Flatten nested JSON', stmt='From {"restaurant_id": 1, "contact": {"email": "kitchen1@tiffingo.in"}, "tags": ["veg", "jain"]} print the id, email and number of tags.', inp='one JSON object',
         code='''import json
o = json.loads('{"restaurant_id": 1, "contact": {"email": "kitchen1@tiffingo.in"}, "tags": ["veg", "jain"]}')
print(o["restaurant_id"], o["contact"]["email"], len(o["tags"]))
''', explain='Hive: SELECT restaurant_id, contact.email, size(tags) FROM restaurants.'),
    dict(level='medium', title='Write CSV safely', stmt='Write the row [1, "Dal, Rice combo", 120] as one CSV line so that a CSV reader gets 3 fields back.', inp='[1, "Dal, Rice combo", 120]',
         code='''import csv, io
buf = io.StringIO()
csv.writer(buf).writerow([1, "Dal, Rice combo", 120])
print(buf.getvalue().strip())
''', explain='1,"Dal, Rice combo",120. Serialising is the other half of a SerDe: values with separators must be quoted.'),
    dict(level='business', title='Cost of parsing every query', stmt='A 200 GB text log table is queried 40 times a day with a RegexSerDe at 2 minutes of cluster time per 10 GB. A daily ORC copy reads 25 GB per query at 0.5 minutes per 10 GB, plus 40 minutes once to build. Compare daily cluster minutes.', inp='200 GB · 40 queries · rates above',
         code='''raw = 40 * (200 / 10) * 2
orc = 40 * (25 / 10) * 0.5 + 40
print("regex on raw text:", raw, "min/day")
print("daily ORC copy   :", orc, "min/day")
''', explain='1,600 vs 90 minutes a day. Parse once, read many times. (Rates are illustrative.)'),
    dict(level='business', title='Quarantine rate alert', stmt='A day had 1,20,000 JSON lines; 36 were quarantined. Alert if the rate is above 0.02%.', inp='120,000 lines · 36 quarantined',
         code='''total, bad = 120_000, 36
rate = bad / total
print(f"rate {rate:.3%} | alert: {rate > 0.0002}")
''', explain='0.030% is above the 0.02% threshold, so the app team is alerted with sample lines, before the problem grows.'),
]

SCN_INTRO = 'SerDe questions show whether you have loaded real-world files. Interviewers love the quoted-comma and JSON cases.'
SCENARIOS = (
    scn('Retail / partner data', 'Fresher', 'Columns are shifted in a CSV table',
        'Some rows of a product table show the price in the category column.',
        'can you diagnose quoted separators?',
        '''<ol>
          <li>Look at the raw lines: the shifted rows contain a comma inside a quoted field.</li>
          <li>The default LazySimpleSerDe has no quote handling. Use <code>OpenCSVSerde</code> with <code>quoteChar</code>, or ask the producer for a different separator.</li>
          <li>Remember OpenCSVSerde returns strings; cast into a typed curated table.</li>
        </ol>''', '“clean the commas with a script first” without asking why they are there.') +
    scn('App analytics', 'Mid-level', 'Nightly JSON job fails',
        'The nightly job over app events fails with a SerDeException mentioning JsonEOFException.',
        'do you know JSON SerDe failure modes and fixes?',
        '''<ul>
          <li>A malformed line (often a truncated upload) makes the JsonSerDe fail the whole read.</li>
          <li>Find it: search the new files for lines that do not parse; move them to a quarantine folder and re-run.</li>
          <li>Prevent: validate at ingestion, write atomically (temp file then rename), monitor quarantine counts.</li>
        </ul>''', 'turning off all validation so bad data flows silently.') +
    scn('Operations / SRE', 'Fresher', 'Query web logs during an incident',
        'You have 30 minutes to find which endpoint returns most 500 errors from raw access logs on HDFS.',
        'can you use RegexSerDe pragmatically?',
        '''<ol>
          <li>Create an external RegexSerDe table on the log folder with groups for ip, time, method, path, status, bytes.</li>
          <li><code>SELECT path, COUNT(*) FROM access_log WHERE status &gt;= 500 GROUP BY path ORDER BY 2 DESC</code>.</li>
          <li>Check for all-NULL rows (unmatched lines) so you know the pattern covers the data.</li>
        </ol>''', 'copying logs into a database first; an external table needs no copy.') +
    scn('Data platform · design', 'Mid-level', 'Raw vs curated tables',
        'Analysts query a raw OpenCSVSerde table directly and complain it is slow and full of CASTs.',
        'do you know the raw-to-curated pattern?',
        '''<ul>
          <li>Keep the raw table only for ingestion. A daily job casts and cleans into a partitioned ORC table.</li>
          <li>Record rejected values in a quality table and alert on spikes.</li>
          <li>Point analysts and BI at the curated table: typed, compressed and fast.</li>
        </ul>''', '“add more memory to the cluster”.')
)
