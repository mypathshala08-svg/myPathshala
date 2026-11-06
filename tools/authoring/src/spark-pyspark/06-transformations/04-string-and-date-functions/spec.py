import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
BODY = body(HERE)

META = dict(
    module='06-transformations', lesson='04-string-and-date-functions', n='6.4',
    module_label='Module 6 · Transformations',
    title='String and date functions',
    desc='Built-in string and datetime functions in PySpark 4.3.0: trimming, case, regexp_replace for phone numbers, regexp_extract, split_part and concat_ws; parsing dates in several formats with try_to_date and coalesce while to_date fails under ANSI; date arithmetic and date_trunc; the YYYY week-based-year pattern rejected by Spark with ISO week 53 spanning two years; and the session time zone changing how the same instant is displayed.',
    og_desc='"YYYY" is not the year: Spark rejects it, and 1 January 2027 is ISO week 53 of 2026. String and date functions in PySpark, tested.',
    minutes=30, level='Beginner → Intermediate',
    lead='Cleaning text and handling dates is daily work in every pipeline. This lesson uses Spark’s built-in functions to normalise names and phone numbers, extract fields with regular expressions, parse messy dates safely, and avoid the week-year and time-zone traps. <b>All outputs are real</b> (PySpark 4.3.0).',
    chips=['PySpark 4.3.0', 'ANSI-safe date parsing', 'YYYY trap shown', 'Runs in your browser (Python)'],
)

MAIN = '''# Normalising Indian phone numbers before a join
import re
raw = ["+91 98200-11122", "9820011133", "098200 11144", "+91-98200-11155"]

def phone10(p):
    digits = re.sub(r"[^0-9]", "", p)     # like F.regexp_replace(c, "[^0-9]", "")
    return digits[-10:]                   # like F.right(c, F.lit(10))

for p in raw:
    print(f"{p:18} -> {phone10(p)}")
'''
RUN = dict(
    heading='Run the code: normalising phone numbers',
    intro='<p>The same logic as Step 1 in plain Python. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('    digits = re.sub(r"[^0-9]", "", p)     # like F.regexp_replace(c, "[^0-9]", "")', 'Remove spaces, dashes and the plus sign.'),
        ('    return digits[-10:]                   # like F.right(c, F.lit(10))', 'Drop country code or leading zero.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Add a number with too few digits: how would you flag it?', code=None),
        dict(label='2 · Predict first: dates', hint='<b>Predict first:</b> which strings parse with either format?',
             code='''from datetime import datetime
def try_date(s, f):
    try:
        return datetime.strptime(s, f).date()
    except ValueError:
        return None
for s in ("2026-11-04", "04/11/2026", "2026-02-30"):
    print(s, try_date(s, "%Y-%m-%d") or try_date(s, "%d/%m/%Y"))
'''),
        dict(label='3 · ISO week year', hint='Calendar year vs ISO week year.',
             code='''from datetime import date
for d in (date(2026, 12, 28), date(2027, 1, 1)):
    y, w, _ = d.isocalendar()
    print(d, "year", d.year, "| ISO", y, "week", w)
'''),
        dict(label='4 · Extract a PIN', hint='First 6-digit number in an address.',
             code='''import re
print(re.search(r"(\\d{6})", "Navi Mumbai, MH 400703").group(1))
'''),
        dict(label='5 · Spot the error', hint='This report formats years with YYYY.', expect='error',
             code='''pattern = "YYYY"
assert pattern != "YYYY", "YYYY is the week-based year: use yyyy or year()"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: text and dates',
    intro='<p>In the <code>pyspark</code> shell. <b>Outputs are real</b> (PySpark 4.3.0).</p>',
    items=[
        dict(title='1 · Session time zone', cmd='spark.conf.get("spark.sql.session.timeZone")', file='pyspark',
             output="'Asia/Calcutta'", note='From the JVM; set it explicitly.'),
        dict(title='2 · try_to_date', cmd='spark.sql("SELECT try_to_date(\'2026-02-30\') AS d").first()', file='pyspark',
             output='Row(d=None)', note='to_date would raise an error.'),
        dict(title='3 · ISO week', cmd='spark.sql("SELECT weekofyear(DATE\'2027-01-01\') AS w").first()', file='pyspark',
             output='Row(w=53)', note='Week 53 of 2026.'),
    ],
)

TRACE = dict(
    heading='coalesce over several formats',
    intro='<p>Follow which format parses each value.</p>',
    code='''from datetime import datetime
formats = ["%Y-%m-%d", "%d/%m/%Y"]
for s in ["2026-11-04", "04/11/2026", "2026-02-30"]:
    result = None
    for f in formats:
        try:
            result = datetime.strptime(s, f).date(); break
        except ValueError:
            pass
    print(s, "->", result)
''',
    notes={5: 'Order :: The first format that works wins, like coalesce.', 10: 'Null :: Values matching no format stay null and can be counted.'},
)

WORKED_INTRO = 'Three cleaning tasks with built-in functions.'
EXAMPLES = [
    dict(level='b', tag='Text · basics', title='Clean names and emails',
         problem='<p>Make names and emails consistent.</p>',
         inp='name, email',
         approach=['trim + initcap for names.', 'trim + lower for emails.', 'Keep the raw columns too.'],
         code='''print("""df.withColumns({"name_clean": F.initcap(F.trim("name")),
                "email_clean": F.lower(F.trim("email"))})""")
''', notes={1: 'Keep raw :: Useful for audits.'},
         tryit='Step 1.'),
    dict(level='i', tag='Dates · parsing', title='Mixed date formats',
         problem='<p>Parse order dates that arrive as ISO or dd/MM/yyyy.</p>',
         inp='string column',
         approach=['try_to_date per format.', 'coalesce.', 'Count nulls.'],
         code='''print("""parsed = F.coalesce(F.try_to_date("s"), F.try_to_date("s", "dd/MM/yyyy"))
df.withColumn("order_date", parsed).where("order_date IS NULL").count()""")
''', notes={1: 'Order :: Put the most common format first.'},
         tryit='Step 3.'),
    dict(level='a', tag='Dates · time zones', title='Hourly report in IST from UTC data',
         problem='<p>Orders are stored in UTC; managers want IST hours.</p>',
         inp='order_ts (UTC instants)',
         approach=['Session zone UTC for processing.', 'from_utc_timestamp(ts, "Asia/Kolkata") for display.', 'hour() on the converted value.'],
         code='''from datetime import datetime, timedelta
utc = datetime(2026, 11, 4, 10, 0)
print("IST hour:", (utc + timedelta(hours=5, minutes=30)).hour)
''', notes={3: 'Offset :: IST is UTC+5:30 all year (no daylight saving).'},
         tryit='Step 6.'),
]

QUIZ = mix([
    dict(q='Beginner: Which removes leading and trailing spaces?', options=['strip()', 'F.trim', 'F.lower', 'F.split'], answer=1,
         why='trim, ltrim, rtrim.'),
    dict(q='Beginner: Pattern for calendar year?', options=['YYYY', 'yyyy', 'YY', 'y-M'], answer=1,
         why='YYYY is week-based.'),
    dict(q='Beginner: Which extracts a regex group?', options=['regexp_replace', 'regexp_extract', 'like', 'split'], answer=1,
         why='Group index argument.'),
    dict(q='Intermediate: to_date("04/11/2026") under ANSI…', options=['Returns null', 'Fails', 'Guesses', 'Returns the string'], answer=1,
         why='Use try_to_date or a format.'),
    dict(q='Intermediate: What does try_to_date return for 2026-02-30?', options=['2026-03-02', 'NULL', 'Error', '2026-02-28'], answer=1,
         why='Invalid date.'),
    dict(q='Intermediate: Where does the default session time zone come from?', options=['UTC always', 'The JVM', 'The data', 'The OS clock only'], answer=1,
         why='Asia/Calcutta in our lab.'),
    dict(q='Advanced: ISO week of 2027-01-01?', options=['1', '52', '53', '0'], answer=2,
         why='Week 53 of 2026.'),
    dict(q='Advanced: Changing the session time zone changes…', options=['The stored instant', 'How timestamps are displayed and parsed', 'Dates only', 'Nothing'], answer=1,
         why='Same epoch, different clock time.'),
])

REVISION = [
    'Text: <code>trim</code>, <code>initcap</code>/<code>lower</code>, <code>regexp_replace</code>, <code>regexp_extract</code>, <code>split</code>/<code>split_part</code>, <code>concat_ws</code>.',
    'Normalise keys (phones, emails) the same way before joining.',
    'Dates: <code>coalesce(try_to_date(s, f1), try_to_date(s, f2))</code>; <code>to_date</code> fails under ANSI.',
    'Arithmetic: <code>datediff</code>, <code>date_add</code>, <code>add_months</code>, <code>last_day</code>, <code>date_trunc</code>.',
    '<code>yyyy</code> not <code>YYYY</code>; ISO weeks can cross years (2027-01-01 = week 53).',
    'Timestamps are instants shown in <code>spark.sql.session.timeZone</code> (default = JVM). Set it.',
    'Prefer built-in functions over UDFs (Lesson 6.6).',
]
FAQ = [
    ('Which regex syntax does Spark use?', 'Java regular expressions. Escape backslashes in Python strings or use raw strings r"…".'),
    ('How do I parse timestamps with milliseconds?', 'to_timestamp(c, "yyyy-MM-dd HH:mm:ss.SSS"), or try_to_timestamp for messy input.'),
    ('What is TIMESTAMP_NTZ?', 'A timestamp without time zone (wall-clock time), useful for local schedules. Default timestamps are LTZ instants.'),
    ('Why did my dates shift by a day?', 'Converting timestamps to dates in a different session time zone can move them across midnight. Fix the session zone.'),
    ('Are there functions for Indian formats?', 'Use format_number for grouping digits and date_format with patterns like dd-MM-yyyy; lakh/crore grouping needs a custom expression.'),
]

PRACTICE_INTRO = 'Programs about text cleaning and dates.'
PROBLEMS = [
    dict(level='easy', title='initcap', stmt='Title-case a name.', inp='"  Ravi KUMAR "',
         code='''print("  Ravi KUMAR ".strip().title())
''', explain='F.initcap(F.trim()).'),
    dict(level='easy', title='Domain', stmt='Email domain.', inp='ravi.k@Mail.in',
         code='''print("ravi.k@Mail.in".split("@")[-1].lower())
''', explain='substring_index + lower.'),
    dict(level='easy', title='Days between', stmt='Days between two dates.', inp='2026-10-29 → 2026-11-04',
         code='''from datetime import date
print((date(2026, 11, 4) - date(2026, 10, 29)).days)
''', explain='datediff: 6.'),
    dict(level='medium', title='Reference number', stmt='Third part of a reference as an int.', inp='TG-2026-000781',
         code='''print(int("TG-2026-000781".split("-")[2]))
''', explain='split_part + cast.'),
    dict(level='medium', title='Week start', stmt='Monday of the week of a date.', inp='2026-10-29',
         code='''from datetime import date, timedelta
d = date(2026, 10, 29)
print(d - timedelta(days=d.weekday()))
''', explain='date_trunc("week").'),
    dict(level='medium', title='Month end', stmt='Last day of a month.', inp='2026-11',
         code='''import calendar
print(calendar.monthrange(2026, 11)[1])
''', explain='last_day.'),
    dict(level='business', title='Delivery minutes', stmt='Minutes from order to delivery.', inp='20:49 → 21:27',
         code='''print((21 * 60 + 27) - (20 * 60 + 49))
''', explain='unix_timestamp difference / 60.'),
    dict(level='business', title='Matched customers', stmt='Matches after normalising phones.', inp='4 raw formats of 2 numbers',
         code='''import re
ps = ["+91 98200-11122", "9820011122", "098200 11133", "9820011133"]
print(len({re.sub(r"\\D", "", p)[-10:] for p in ps}), "distinct customers")
''', explain='Before: 4 different strings.'),
]

SCN_INTRO = 'Text and date questions check practical data cleaning.'
SCENARIOS = (
    scn('Any company · PySpark', 'Fresher', '“Convert a string to a date”',
        'Convert "04/11/2026" to a date column.',
        'formats?',
        '<p><code>F.to_date("s", "dd/MM/yyyy")</code>, or <code>try_to_date</code> if some values may be invalid. Without the format, Spark expects ISO yyyy-MM-dd; under ANSI mode a mismatch fails the job.</p>', 'Using a Python UDF with strptime.') +
    scn('Data engineering', 'Mid-level', 'Messy phone numbers',
        'Customer phones come in many formats. How do you join on them?',
        'normalisation?',
        '''<ul>
          <li>regexp_replace non-digits, keep the last 10 digits.</li>
          <li>Validate length; flag bad values.</li>
          <li>Store the normalised key; apply the same rule on both sides.</li>
        </ul>''', 'Joining raw strings.') +
    scn('Analytics', 'Mid-level', 'Wrong year at year end',
        'A report shows late-December orders in the next year.',
        'week-year awareness?',
        '''<ol>
          <li>Check for YYYY (week-based year) or ISO week logic.</li>
          <li>Use yyyy/year() for calendar years.</li>
          <li>For weekly reports use ISO week with ISO week-year.</li>
        </ol>''', 'Hard-coding a fix for one date.') +
    scn('Data engineering', 'Senior', 'Time zones across teams',
        'Different teams get different hourly numbers from the same table.',
        'time-zone handling?',
        '''<ul>
          <li>Session time zone defaults to the JVM; set it in every job.</li>
          <li>Store instants in UTC; convert at presentation.</li>
          <li>Document which zone each report uses.</li>
        </ul>''', 'Storing local times as strings.')
)
