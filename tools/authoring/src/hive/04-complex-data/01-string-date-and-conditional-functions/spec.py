import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
BODY = body(HERE)
def capf(n):
    return open(CAP + n).read().rstrip()

META = dict(
    module='04-complex-data', lesson='01-string-date-and-conditional-functions', n='4.1',
    module_label='Module 4 · Functions and complex data',
    title='String, date and conditional functions',
    desc='Hive built-in functions with real Hive 4.2.1 results: SHOW FUNCTIONS and DESCRIBE FUNCTION, string functions (upper, initcap, substr, split, concat_ws, lpad, regexp_extract, regexp_replace, translate, format_number), date functions (datediff, add_months, date_format, trunc, unix_timestamp, time zones), IF, CASE, COALESCE, NVL, NULLIF, maths, CAST, masking and hashing, with the case-sensitivity and time-zone traps.',
    og_desc='Why did the report show zero delivered orders? Hive string, date and conditional functions with real outputs and the traps that cause silent wrong answers.',
    minutes=35, level='Beginner → Advanced',
    lead='Raw data is messy: statuses in capitals, times in log format, phone numbers with spaces. Hive has about 490 built-in functions to clean it. This lesson fixes a real report that showed zero delivered orders, parses web-log times that came out 5½ hours early, masks personal data for a vendor, and catches a wrong example in Hive’s own help. <b>All outputs are real</b>, from Hive 4.2.1.',
    chips=['Real Hive 4.2.1 outputs', 'Case and time-zone traps', 'Masking and hashing', 'Runs in your browser (Python)'],
)

MAIN = '''# Cleaning raw values like Hive string functions do
raw = [("  aRJUN nAIR ", "+91 98765 43210", "DELIVERED"),
       ("ananya iyer", "098765-12345", "Delivered"),
       ("KABIR SHAH", "9876500011", "cancelled")]

for name, phone, status in raw:
    clean_name = name.strip().lower().title()          # initcap(lower(trim(name)))
    digits = "".join(ch for ch in phone if ch.isdigit())  # regexp_replace(phone, '[^0-9]', '')
    last10 = digits[-10:]                               # substr(digits, -10)
    masked = "n" * 6 + last10[-4:]                      # mask_show_last_n(last10, 4)
    delivered = 1 if status.lower() == "delivered" else 0   # CASE lower(status) WHEN 'delivered'
    print(f"{clean_name:12} {masked}  delivered={delivered}")
'''
RUN = dict(
    heading='Run the code: clean text, dates and rules',
    intro='<p>These programs do in Python what the Hive functions in this lesson do, so you can test ideas quickly. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('    clean_name = name.strip().lower().title()          # initcap(lower(trim(name)))', 'Functions nest: trim first, then lower, then capitalise each word.'),
        ('    delivered = 1 if status.lower() == "delivered" else 0   # CASE lower(status) WHEN \'delivered\'', 'Normalising case before comparing is the fix for the zero-delivered report.'),
    ],
    tasks=[
        dict(label='1 · Clean names, phones and status', hint='Press <b>Run</b>. Then remove <code>.lower()</code> from the status check and see how many rows still count as delivered.', code=None),
        dict(label='2 · Date arithmetic', hint='<b>Predict first:</b> days from 4 to 31 October, and 31 January plus one month. Real Hive: 27 and 2026-02-28.',
             code='''from datetime import date
import calendar
print((date(2026, 10, 31) - date(2026, 10, 4)).days)          # datediff
d = date(2026, 1, 31)
y, m = (d.year, d.month + 1)
last = calendar.monthrange(y, m)[1]
print(date(y, m, min(d.day, last)))                            # add_months clamps
print(date(2026, 10, 4).strftime("%d-%b-%Y %A"))                # date_format
'''),
        dict(label='3 · Epoch and time zones', hint='The same instant printed in UTC and IST. This is the 5½-hour shift from Step 5.',
             code='''from datetime import datetime, timezone, timedelta
epoch = 1790793000                                     # real unix_timestamp value
utc = datetime.fromtimestamp(epoch, timezone.utc)
ist = utc.astimezone(timezone(timedelta(hours=5, minutes=30)))
print("UTC:", utc.strftime("%Y-%m-%d %H:%M"))
print("IST:", ist.strftime("%Y-%m-%d %H:%M"))
'''),
        dict(label='4 · CASE bands and COALESCE', hint='Change the band limits and the default city.',
             code='''orders = [(100001, 530, None), (100004, 180, "Thane"), (100007, 310, None)]
for oid, amount, city in orders:
    band = "low" if amount < 200 else "mid" if amount < 400 else "high"   # CASE WHEN …
    size = "big" if amount >= 500 else "normal"                          # IF(…)
    print(oid, band, size, city if city is not None else "Unknown")      # COALESCE(city, 'Unknown')
'''),
        dict(label='5 · Spot the error', hint='The report counts delivered orders but gets 0. Fix the comparison so it matches the data.', expect='error',
             code='''statuses = ["DELIVERED", "DELIVERED", "CANCELLED", "DELIVERED"]
delivered = sum(1 for s in statuses if s == "delivered")
assert delivered == 3, f"counted {delivered}: comparison is case-sensitive"
print(delivered)
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: maths, collections and a weekday report',
    intro='<p>Three more groups of functions to try in Beeline. <b>Outputs are real</b>, from Hive 4.2.1 on the TiffinGo data.</p>',
    items=[
        dict(title='1 · Rounding and maths', cmd='SELECT round(123.456, 1) AS r1, round(123.456, -1) AS r2, bround(2.5) AS br, round(2.5) AS r,\n  floor(-2.5) AS f, ceil(-2.5) AS c, abs(-7) AS a, pmod(-7, 3) AS pm, -7 % 3 AS modop,\n  power(2, 10) AS p, sqrt(2) AS s, greatest(3, 9, 4) AS g, least(3, 9, 4) AS l;', file='Beeline',
             output=capf('l41_math.txt'),
             note='<code>round</code> sends .5 up (3); <code>bround</code> uses banker’s rounding to the even number (2). <code>%</code> keeps the sign of the left side (-1), while <code>pmod</code> always returns a positive remainder (2), useful for bucketing.'),
        dict(title='2 · Collection functions on arrays and maps', cmd="SELECT order_id, size(dishes) AS n_dishes, array_contains(dishes, 'Lassi') AS has_lassi,\n  sort_array(dishes) AS sorted, map_keys(prefs) AS k, prefs['spice'] AS spice\nFROM order_items WHERE order_id <= 100003;", file='Beeline',
             output=capf('l41_coll.txt'),
             note='These work on one row’s array or map without splitting it into rows. Lesson 4.2 turns arrays into rows with explode.'),
        dict(title='3 · A weekday report with date functions', cmd="SELECT date_format(order_date, 'EEEE') AS weekday, COUNT(*) AS orders,\n  ROUND(AVG(amount), 2) AS avg_amt\nFROM orders GROUP BY date_format(order_date, 'EEEE'), dayofweek(order_date)\nORDER BY dayofweek(order_date);", file='Beeline',
             output=capf('l41_report.txt'),
             note='<code>dayofweek</code> is grouped too so the result can be sorted Sunday to Saturday instead of alphabetically. Thursday and Friday have the most orders in this data set.'),
    ],
)

TRACE = dict(
    heading='Evaluating a nested function call, inside out',
    intro='<p>Hive evaluates the innermost function first. Watch the value change at each step of <code>initcap(lower(trim(name)))</code>.</p>',
    code='''name = "  aRJUN nAIR "
step1 = name.strip()
step2 = step1.lower()
step3 = step2.title()
code = "C" + str(3).rjust(6, "0")
print(step3, code)
''',
    notes={2: 'trim :: Spaces at both ends removed.', 3: 'lower :: All letters small.', 4: 'initcap :: First letter of each word capital.', 5: 'lpad :: Pads on the left to 6 characters.'},
)

WORKED_INTRO = 'Three cleaning jobs from TiffinGo: tidy phone numbers, order-age buckets, and fuzzy city names.'
EXAMPLES = [
    dict(level='b', tag='Data cleaning · regexp_replace', title='Standardise phone numbers',
         problem='<p>Phones arrive as “+91 98765 43210”, “098765-12345” and “9876500011”. Keep the last 10 digits: <code>substr(regexp_replace(phone, \'[^0-9]\', \'\'), -10)</code>.</p>',
         inp='+91 98765 43210 · 098765-12345 · 9876500011',
         approach=['Remove every non-digit.', 'Keep the last 10 digits (drops 91 or 0 prefixes).', 'Check every result has length 10.'],
         code='''import re
for p in ["+91 98765 43210", "098765-12345", "9876500011"]:
    digits = re.sub(r"[^0-9]", "", p)
    last10 = digits[-10:]
    print(p, "->", last10, len(last10) == 10)
''', notes={3: 'regexp_replace :: Same pattern as in Hive.'},
         tryit='A number with only 9 digits fails the check. In Hive, count such rows with <code>WHERE length(clean) &lt;&gt; 10</code> before loading.'),
    dict(level='i', tag='Reporting · datediff + CASE', title='How old is each order?',
         problem='<p>Bucket orders by age on 31 October 2026: 0–7 days “this week”, 8–30 “this month”, older “old”, using <code>CASE WHEN datediff(\'2026-10-31\', order_date) &lt;= 7 …</code>.</p>',
         inp='order dates 2026-10-30, 2026-10-20, 2026-09-15, 2026-10-24',
         approach=['datediff(end, start) gives the age in days.', 'CASE checks the smallest bucket first.', 'Count orders per bucket.'],
         code='''from datetime import date
end = date(2026, 10, 31)
buckets = {}
for d in [date(2026, 10, 30), date(2026, 10, 20), date(2026, 9, 15), date(2026, 10, 24)]:
    age = (end - d).days
    b = "this week" if age <= 7 else "this month" if age <= 30 else "old"
    buckets[b] = buckets.get(b, 0) + 1
    print(d, age, b)
print(buckets)
''', notes={5: 'datediff :: End date first, otherwise the age is negative.'},
         tryit='Swap the arguments: every age becomes negative and every order lands in “this week”. That is exactly the datediff help-text mistake.'),
    dict(level='a', tag='Data quality · levenshtein', title='Find spelling variants of city names',
         problem='<p>City values include “Bengaluru”, “Bangalore”, “Bengluru” and “Pune”. Flag values within edit distance 3 of the standard name with <code>levenshtein(city, \'Bengaluru\') &lt;= 3</code>.</p>',
         inp='Bengaluru · Bangalore · Bengluru · Pune',
         approach=['Compare each value with the standard name (Hive: levenshtein; Python here: a similarity ratio).', 'Flag close but not identical values for review.', 'Review before merging; never auto-merge blindly.'],
         code='''import difflib
std = "Bengaluru"
for c in ["Bengaluru", "Bangalore", "Bengluru", "Pune"]:
    r = difflib.SequenceMatcher(None, c, std).ratio()
    print(c, round(r, 2), "variant" if 0.6 <= r < 1 else "")
''', notes={4: 'Similarity :: Python stand-in for levenshtein: 1.0 means identical.'},
         tryit='Real Hive returned 3 for Bengaluru vs Bangalore, and the same soundex code B524 for both. Try “Pune” vs “Pone”: distance 1, but they are different words, so keep a human in the loop.'),
]

QUIZ = mix([
    dict(q='Beginner: What does split(\'Aarav Desai\', \' \')[0] return?', options=['Desai', 'Aarav', 'A', 'An error'], answer=1,
         why='split returns an array and arrays start at index 0.'),
    dict(q='Beginner: What does CAST(\'abc\' AS INT) return in Hive?', options=['0', 'An error', 'NULL', '-1'], answer=2,
         why='Hive returns NULL silently. Count NULLs after conversions.'),
    dict(q='Beginner: datediff(\'2026-10-31\', \'2026-10-04\') is…', options=['-27', '27', '28', '26'], answer=1,
         why='End date first gives a positive number of days.'),
    dict(q='Intermediate: CASE status WHEN \'delivered\' … counted 0 on data stored as DELIVERED. Why?', options=['CASE is broken', 'String comparison is case-sensitive', 'Statuses are NULL', 'Need GROUP BY'], answer=1,
         why='Use lower(status) or upper(status) before comparing.'),
    dict(q='Intermediate: concat(\'Rs \', NULL) returns…', options=['Rs ', 'Rs NULL', 'NULL', 'An error'], answer=2,
         why='Any NULL argument makes concat NULL. concat_ws skips NULLs.'),
    dict(q='Intermediate: add_months(\'2026-01-31\', 1) returns…', options=['2026-03-03', '2026-02-31', '2026-02-28', 'NULL'], answer=2,
         why='The day is clamped to the last valid day of February.'),
    dict(q='Advanced: A log time with +0530 printed 5½ hours early via from_unixtime. What fixes it?', options=['CAST to DATE', 'SET hive.local.time.zone=Asia/Kolkata (or convert with from_utc_timestamp)', 'Use upper()', 'Nothing, it is correct'], answer=1,
         why='from_unixtime formats in the session time zone; the server was in UTC.'),
    dict(q='Advanced: Which gives a positive remainder for -7 and 3?', options=['-7 % 3', 'pmod(-7, 3)', 'round(-7/3)', 'abs(-7) % -3'], answer=1,
         why='pmod returned 2; % returned -1.'),
])

REVISION = [
    '<b>Discover:</b> <code>SHOW FUNCTIONS LIKE \'%date%\'</code>, <code>DESCRIBE FUNCTION EXTENDED f</code> (but run the example yourself).',
    '<b>Strings:</b> trim, lower/upper/initcap, length, substr (1-based), split (0-based array), concat (NULL if any NULL), concat_ws (skips NULL), lpad/rpad, replace/translate, regexp_extract/regexp_replace, instr/locate (0 = not found), format_number.',
    '<b>Dates:</b> datediff(end, start), date_add/date_sub, add_months (clamps), last_day, next_day, trunc(d, \'MM\'), months_between, dayofweek (Sunday = 1), weekofyear, extract, date_format.',
    '<b>Times:</b> unix_timestamp(s, fmt) → epoch; from_unixtime prints in <code>hive.local.time.zone</code>; from_utc_timestamp / to_utc_timestamp convert.',
    '<b>Rules:</b> IF, CASE (simple and searched), COALESCE, NVL, NULLIF, isnull; string comparison and LIKE are case-sensitive.',
    '<b>Silent NULLs:</b> bad CAST, invalid date, NULL in concat, NULL + 1.',
    '<b>Maths:</b> round (half up) vs bround (half even), floor/ceil, % vs pmod, greatest/least.',
    '<b>Privacy:</b> mask, mask_show_last_n, mask_first_n; md5/sha2 for stable ids (add a secret salt).',
]
FAQ = [
    ('Are function names case-sensitive?', 'No. UPPER(name), upper(name) and Upper(name) are the same function. The data values are case-sensitive, which is the trap in this lesson.'),
    ('How do I make a comparison case-insensitive?', 'Normalise both sides: <code>lower(city) = lower(\'Pune\')</code>, or for patterns <code>lower(city) LIKE \'pu%\'</code>. RLIKE accepts Java regex flags, so <code>city RLIKE \'(?i)^pu\'</code> also works. Better still, standardise case once in the curated table.'),
    ('Why do date functions accept strings?', 'Many date functions take a string in yyyy-MM-dd (or yyyy-MM-dd HH:mm:ss) form and convert it. An invalid string such as \'2026-13-45\' or \'04/10/2026\' becomes NULL, as our lab showed. Store dates as DATE or TIMESTAMP columns to catch bad values at load time.'),
    ('What is assert_true for?', 'It stops a query when a condition fails: <code>SELECT assert_true(COUNT(*) &gt; 0) FROM staging</code>. In our lab <code>assert_true(1 &gt; 2)</code> failed with “ASSERT_TRUE(): assertion failed.” It is a simple data-quality gate in pipelines.'),
    ('Can I add my own functions?', 'Yes. Write a Java UDF, add the JAR and CREATE FUNCTION; Module 9 shows how. First check SHOW FUNCTIONS: with about 490 built-ins, the function you need often already exists.'),
]

PRACTICE_INTRO = 'Programs that reproduce Hive function results on real lab values, with the HiveQL in each explanation.'
PROBLEMS = [
    dict(level='easy', title='Customer codes', stmt='Turn customer ids 1, 42 and 2000 into 6-digit codes with a C prefix.', inp='ids 1, 42, 2000',
         code='''for cid in [1, 42, 2000]:
    print("C" + str(cid).rjust(6, "0"))
''', explain="concat('C', lpad(cast(customer_id AS STRING), 6, '0')) → C000001, C000042, C002000."),
    dict(level='easy', title='First name', stmt='Take the first word of each name.', inp='Aarav Desai, Ananya Iyer, Arjun Nair',
         code='''for n in ["Aarav Desai", "Ananya Iyer", "Arjun Nair"]:
    print(n.split(" ")[0])
''', explain="split(name, ' ')[0]: Aarav, Ananya, Arjun, as in the real output."),
    dict(level='easy', title='Month start and end', stmt='For 10 February 2026 print the first and last day of the month.', inp='2026-02-10',
         code='''from datetime import date
import calendar
d = date(2026, 2, 10)
print(d.replace(day=1), d.replace(day=calendar.monthrange(d.year, d.month)[1]))
''', explain="trunc(d, 'MM') = 2026-02-01 and last_day(d) = 2026-02-28 (real)."),
    dict(level='medium', title='Extract the date from an order code', stmt='Pull the date out of ORD#2026-10-04#PUNE with a regular expression.', inp='ORD#2026-10-04#PUNE',
         code='''import re
m = re.search(r"#([0-9-]+)#", "ORD#2026-10-04#PUNE")
print(m.group(1))
''', explain="regexp_extract(code, '#([0-9-]+)#', 1) = 2026-10-04 (real). In HiveQL write \\\\d instead of \\d if you use it."),
    dict(level='medium', title='Online vs COD', stmt='Return the payment method, or None for COD (NULLIF).', inp='UPI, COD, Card',
         code='''for p in ["UPI", "COD", "Card"]:
    print(p, "->", None if p == "COD" else p)
''', explain="nullif(payment, 'COD'): order 100005 (COD) became NULL in the real output."),
    dict(level='medium', title='Log time to IST', stmt='Convert the real epoch values to IST times.', inp='1790793000, 1790793037, 1790793074',
         code='''from datetime import datetime, timezone, timedelta
IST = timezone(timedelta(hours=5, minutes=30))
for e in [1790793000, 1790793037, 1790793074]:
    print(e, datetime.fromtimestamp(e, IST).strftime("%Y-%m-%d %H:%M:%S"))
''', explain='00:00:00, 00:00:37 and 00:01:14 on 1 October: the times written in the log.'),
    dict(level='business', title='Delivery rate', stmt='Real counts: DELIVERED 46,018, CANCELLED 3,063, REFUNDED 919. What is the delivery rate, and what did the broken query report?', inp='real status counts',
         code='''counts = {"DELIVERED": 46018, "CANCELLED": 3063, "REFUNDED": 919}
total = sum(counts.values())
print(f"delivery rate {counts['DELIVERED'] / total:.1%} of {total}")
print("broken CASE reported 0.0%")
''', explain='92.0% of 50,000 orders. The case-sensitive CASE reported 0%: a whole dashboard wrong because of one lower().'),
    dict(level='business', title='Weekend vs weekday', stmt='Using the real weekday counts, what share of orders come on Saturday and Sunday?', inp='Sun 6,656 · Mon 6,694 · Tue 6,749 · Wed 6,609 · Thu 8,273 · Fri 8,312 · Sat 6,707',
         code='''w = {"Sun": 6656, "Mon": 6694, "Tue": 6749, "Wed": 6609, "Thu": 8273, "Fri": 8312, "Sat": 6707}
weekend = w["Sat"] + w["Sun"]
print(f"weekend {weekend} = {weekend / sum(w.values()):.1%}")
''', explain='13,363 orders, 26.7%. Thursday and Friday are the busiest days in this data set, which would guide rider staffing.'),
]

SCN_INTRO = 'Function questions in interviews usually come with data: clean this, compute that date, explain this NULL.'
SCENARIOS = (
    scn('Any company · SQL', 'Fresher', '“Count customers who joined in each month”',
        'Customers have a joined_on DATE. Produce month and count, in calendar order.',
        'do you know date functions and grouping keys?',
        '''<pre>SELECT date_format(joined_on, 'yyyy-MM') AS ym, COUNT(*) AS customers
FROM customers
GROUP BY date_format(joined_on, 'yyyy-MM')
ORDER BY ym;</pre>
        <p>The yyyy-MM text sorts correctly; ‘MMM yyyy’ would sort alphabetically.</p>''', 'Grouping by month() alone, which mixes the same month of different years.') +
    scn('Data quality', 'Mid-level', 'A metric dropped to zero overnight',
        'Delivered orders show 0 after a source system started sending upper-case statuses.',
        'do you check the data before blaming the engine?',
        '''<ol>
          <li><code>SELECT status, COUNT(*) … GROUP BY status</code> to see the real values.</li>
          <li>Compare with <code>lower(status)</code>; fix the view to normalise case.</li>
          <li>Add an alert when a core metric drops to zero or moves more than a threshold.</li>
        </ol>''', '“Hive lost the data”.') +
    scn('Data engineering', 'Mid-level', 'Daily totals are off near midnight',
        'Orders placed between 00:00 and 05:30 IST appear on the previous day in reports.',
        'do you understand epoch time and session time zones?',
        '''<ul>
          <li>The data is correct as an instant; it is printed or truncated in UTC.</li>
          <li>Set <code>hive.local.time.zone=Asia/Kolkata</code> in the job, or convert explicitly with <code>from_utc_timestamp(ts, 'Asia/Kolkata')</code> before <code>to_date</code>.</li>
          <li>Document which zone each column is in.</li>
        </ul>''', 'Adding 5.5 hours by hand everywhere.') +
    scn('Privacy', 'Senior', 'Share data with a partner safely',
        'A marketing partner needs customer segments for a campaign, but must not identify customers.',
        'can you minimise and pseudonymise data?',
        '''<ul>
          <li>Send only needed columns; mask phones with <code>mask_show_last_n</code> if they must appear at all.</li>
          <li>Replace ids with <code>sha2(concat(id, secret_salt), 256)</code> so files can be joined without revealing ids.</li>
          <li>Prefer central masking policies (Ranger) over ad-hoc queries; log every export.</li>
        </ul>''', 'Plain md5(id): small id ranges can be reversed by hashing every possible id.')
)
