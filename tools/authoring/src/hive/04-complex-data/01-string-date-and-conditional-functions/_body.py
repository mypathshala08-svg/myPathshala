import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()

# ---------------------------------------------------------------- story
raw = ['DELIVERED', '01/Oct/2026:00:00:00 +0530', '+91 98765 43210', 'aRJUN nAIR']
fixed = ['lower(status)', 'unix_timestamp(ts, fmt)', "regexp_replace(…, '[^0-9]', '')", 'initcap(lower(name))']
sc = (box(10, 12, 300, 128, 'card') + t(160, 30, 'Raw values in the tables', 8.8, bold=True) +
      ''.join(t(26, 54 + k * 22, r, 8, 'ink', anchor='start', mono=True) for k, r in enumerate(raw)) +
      arrow(316, 76, 330, 76, 'ink3', 2) +
      box(334, 12, 300, 128, 'green') + t(484, 30, 'One function call each', 8.8, 'green', bold=True) +
      ''.join(t(348, 54 + k * 22, f, 8, 'green', anchor='start', mono=True) for k, f in enumerate(fixed)))
scene_svg = scene('Messy raw values such as upper-case status, log timestamps, phone numbers and badly cased names on the left; the Hive function that cleans each one on the right.', sc,
                  'Hive ships with <tspan font-weight="700" class="s-acc">about 490 built-in functions</tspan>. Knowing ten of them well cleans most data.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Why does my report say zero orders were delivered?”</h2>
  <div class="story">
    <p class="narration">Kabir’s first weekly report for TiffinGo shows <b>0 delivered orders</b>, while the app clearly delivered thousands. The same report puts the first website visit of October at 6:30 pm on 30 September, and the vendor who receives the customer list complains that it contains full phone numbers.</p>

{scene_svg}

K> Sir, I wrote <code>CASE status WHEN 'delivered' THEN 1 END</code>. Hive returned zero.
A> Look at the data: the column says <code>DELIVERED</code>, in capitals. String comparison in Hive is case-sensitive. <code>lower(status)</code> fixes it. The 6:30 pm visit is a time-zone issue: the server runs in UTC, so the log time is converted to UTC. And phone numbers can be masked with <code>mask_show_last_n</code>.
R> How do we even know which functions exist?
A> <code>SHOW FUNCTIONS</code> lists them (493 in our Hive 4.2.1) and <code>DESCRIBE FUNCTION EXTENDED</code> explains one. Today we go through the families you use every day: text, dates, conditions, NULLs, maths and masking. Every output is real, and we will meet three traps, including one in Hive’s own help text.
  </div>
</section>
'''

lv = '''
LEVELS> Built-in functions at three levels
L1> A toolbox for each kind of value
      <ul>
        <li>Text needs cleaning (spaces, capitals, symbols), dates need arithmetic (days between, month start), and many values need a rule (“if more than 500 then big”).</li>
        <li>Hive has a ready function for each job. You call it inside SELECT, WHERE, GROUP BY or ORDER BY, like <code>upper(name)</code>.</li>
        <li>A function works on one row at a time and returns one value. (Aggregates like SUM, from Module 3, combine many rows.)</li>
      </ul>
L2> The families you use most
      <ul>
        <li><b>String:</b> <code>upper/lower/initcap</code>, <code>trim</code>, <code>length</code>, <code>substr</code>, <code>concat/concat_ws</code>, <code>split</code>, <code>lpad/rpad</code>, <code>replace/translate</code>, <code>regexp_extract/regexp_replace</code>, <code>instr/locate</code>, <code>format_number</code>.</li>
        <li><b>Date:</b> <code>current_date</code>, <code>to_date</code>, <code>date_format</code>, <code>datediff</code>, <code>date_add/date_sub</code>, <code>add_months</code>, <code>last_day</code>, <code>next_day</code>, <code>trunc</code>, <code>months_between</code>, <code>year/month/dayofweek/weekofyear/extract</code>, <code>unix_timestamp/from_unixtime</code>, <code>from_utc_timestamp</code>.</li>
        <li><b>Conditional and NULL:</b> <code>IF</code>, <code>CASE</code>, <code>COALESCE</code>, <code>NVL</code>, <code>NULLIF</code>, <code>isnull/isnotnull</code>, <code>assert_true</code>.</li>
        <li><b>Maths, conversion, masking:</b> <code>round/bround/floor/ceil/pmod/power/greatest</code>, <code>CAST</code>, <code>mask*</code>, <code>md5/sha2/hash</code>.</li>
      </ul>
L3> How Hive evaluates them, and where they bite
      <ul>
        <li>Built-ins are Java classes (GenericUDF). <code>DESCRIBE FUNCTION EXTENDED</code> shows the class and whether it is BUILTIN. Most run vectorised on ORC data.</li>
        <li><b>Silent NULLs:</b> a bad CAST, an invalid date, an unknown format or a <code>concat</code> with a NULL argument returns NULL without any error. Count NULLs after every transformation.</li>
        <li><b>Time zones:</b> <code>unix_timestamp</code> gives seconds since 1970 UTC; <code>from_unixtime</code> formats them in <code>hive.local.time.zone</code> (LOCAL = the server JVM’s zone). Set it per session or store UTC deliberately.</li>
        <li>Functions on a <b>partition column</b> or in a join key can stop partition pruning or index use; filter on the raw column when you can (Modules 5 and 8).</li>
        <li>Patterns in <code>date_format</code> and <code>unix_timestamp</code> follow Java’s DateTimeFormatter style: <code>yyyy</code> year, <code>MM</code> month, <code>mm</code> minutes, <code>MMM</code> “Oct”, <code>EEEE</code> weekday, <code>Z</code> zone offset.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Built-in scalar functions</h2>
''' + def_block(
    'A <b>built-in scalar function</b> (a UDF in Hive terms) takes zero or more values from a single row and returns one value. Hive groups them into mathematical, string, date, conditional, type-conversion, collection, data-masking and miscellaneous functions. They can be used wherever an expression is allowed. The list available in a session is shown by <code>SHOW FUNCTIONS</code>, and <code>DESCRIBE FUNCTION [EXTENDED] name</code> documents one function.',
    'A function takes values from one row, like a name or a date, and gives back one new value, like the name in capitals or the number of days between two dates.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('UDF', 'User-defined function: Hive’s name for a one-row-in, one-value-out function, built-in or your own.'),
    ('UDAF', 'Aggregate function (many rows in, one value out), like SUM. Module 3.'),
    ('UDTF', 'Table-generating function (one row in, many rows out), like explode. Lesson 4.2.'),
    ('Epoch / Unix time', 'Seconds since 1 January 1970 UTC. <code>unix_timestamp</code> returns it.'),
    ('Format pattern', 'Letters like <code>dd-MMM-yyyy</code> that describe how a date is written.'),
    ('Masking', 'Hiding part of a value, e.g. showing only the last 4 digits of a phone.'),
    ('Hash', 'A fixed-length fingerprint (md5, sha2). Same input → same hash; useful as a join key without exposing the value.'),
]) + '''

  <h3>Function families with real results (Hive 4.2.1)</h3>
''' + table(['Family', 'Call', 'Real result'], [
    ['String', "<code>initcap(lower('aRJUN nAIR'))</code>", 'Arjun Nair'],
    ['String', "<code>regexp_replace('+91 98765 43210', '[^0-9]', '')</code>", '919876543210'],
    ['String', "<code>format_number(2941120.5, 2)</code>", '2,941,120.50'],
    ['Date', "<code>add_months('2026-01-31', 1)</code>", '2026-02-28'],
    ['Date', "<code>date_format('2026-10-04', 'dd-MMM-yyyy EEEE')</code>", '04-Oct-2026 Sunday'],
    ['Conditional', "<code>coalesce(NULL, NULL, 'Thane')</code>", 'Thane'],
    ['Maths', '<code>round(2.5)</code> · <code>bround(2.5)</code>', '3 · 2'],
    ['Maths', '<code>-7 % 3</code> · <code>pmod(-7, 3)</code>', '-1 · 2'],
    ['Conversion', "<code>CAST('abc' AS INT)</code>", 'NULL (no error)'],
    ['Masking', "<code>mask_show_last_n('9876543210', 4)</code>", 'nnnnnn3210'],
], minw=640) + lv + '''
EXAM> “Name five string and five date functions in Hive.” Give them with one real result each, e.g. <code>datediff('2026-10-31', '2026-10-04') = 27</code>, then mention the two classic traps: string comparison is case-sensitive, and bad casts return NULL silently.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Which function for which job</h2>
''' + table(['Job', 'Function(s)', 'Watch out'], [
    ['Fix case and spaces', '<code>trim</code>, <code>lower</code>, <code>upper</code>, <code>initcap</code>', 'Compare after normalising both sides'],
    ['Cut and join text', '<code>substr(s, start, len)</code> (1-based), <code>split(s, sep)[i]</code> (0-based), <code>concat_ws</code>', '<code>concat</code> with any NULL is NULL; <code>concat_ws</code> skips NULLs'],
    ['Find and extract', '<code>instr</code>, <code>locate</code> (0 = not found), <code>regexp_extract(s, re, group)</code>', 'Backslashes must be doubled in the SQL string'],
    ['Clean and replace', '<code>replace</code>, <code>translate</code>, <code>regexp_replace</code>', 'translate maps characters, not words'],
    ['Pad and format', '<code>lpad/rpad</code>, <code>format_number</code>, <code>printf</code>', 'format_number returns a STRING'],
    ['Date arithmetic', '<code>datediff</code>, <code>date_add/date_sub</code>, <code>add_months</code>, <code>months_between</code>', 'datediff(end, start): order matters'],
    ['Calendar parts', '<code>year</code>, <code>month</code>, <code>dayofweek</code> (Sunday = 1), <code>weekofyear</code>, <code>extract(quarter FROM d)</code>, <code>trunc(d, \'MM\')</code>, <code>last_day</code>', 'Week numbering is ISO-style'],
    ['Parse and print times', '<code>unix_timestamp(s, fmt)</code>, <code>from_unixtime(n, fmt)</code>, <code>date_format</code>, <code>to_date</code>', 'Time zone of the session'],
    ['Rules and NULLs', '<code>IF</code>, <code>CASE</code>, <code>COALESCE</code>, <code>NVL</code>, <code>NULLIF</code>', 'NULL never equals anything'],
    ['Protect personal data', '<code>mask</code>, <code>mask_show_last_n</code>, <code>mask_first_n</code>, <code>md5</code>, <code>sha2</code>', 'md5 is not encryption; prefer sha2 with a secret salt'],
    ['Fuzzy matching', '<code>levenshtein</code>, <code>soundex</code>', 'Good for spotting variants, not for automatic merging'],
], minw=760) + '''
WARN> Hive’s own help can be wrong. <code>DESCRIBE FUNCTION EXTENDED datediff</code> prints the example <code>datediff('2009-07-30', '2009-07-31')</code> with the answer <b>1</b>. Running it in our lab returns <b>-1</b>, which matches the description (“if date1 is earlier than date2, the result is negative”). Always run an example before you trust it.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Cleaning Kabir’s weekly report, one function family at a time</h2>
  <p>All outputs are real, from the Hive 4.2.1 lab.</p>
''' + stepper([
    ('Step 1 · Find and read functions',
     code('sql', 'Beeline', "SHOW FUNCTIONS LIKE '%date%';\nDESCRIBE FUNCTION EXTENDED datediff;\nSELECT datediff('2009-07-30', '2009-07-31') AS d;",
          capf('l41_showfn.txt') + '\n' + capf('l41_descfn.txt') + '\n' + capf('l41_misc.txt').split('\n+--------+')[0]),
     '<code>SHOW FUNCTIONS</code> without LIKE listed 493 functions. The help for datediff shows <b>1</b> as the example answer, but the real result is <b>-1</b>: the first date is earlier, so the result is negative.'),
    ('Step 2 · Clean and build text',
     code('sql', 'Beeline', "SELECT name, upper(name) AS up, length(name) AS len,\n  split(name, ' ')[0] AS first_name, initcap(lower('aRJUN nAIR')) AS fixed,\n  concat_ws(' | ', city, state, plan) AS label,\n  lpad(cast(customer_id AS STRING), 6, '0') AS cust_code\nFROM customers WHERE customer_id <= 3;", capf('l41_str.txt')),
     '<code>split(…)[0]</code> takes the first word (arrays start at 0). <code>lpad</code> builds fixed-width codes. <code>concat_ws</code> joins columns with a separator.'),
    ('Step 3 · Cut, search, extract and format',
     code('sql', 'Beeline', "SELECT trim('  Pune  ') AS t, length(trim('  Pune  ')) AS l,\n  substr('TiffinGo-Thane-0042', 8, 5) AS sub, instr('a,b,c', 'c') AS pos,\n  locate('x', 'Mumbai') AS notfound, replace('Navi-Mumbai', '-', ' ') AS rep,\n  translate('9876-543-210', '-', '') AS tr,\n  regexp_extract('ORD#2026-10-04#PUNE', '#([0-9-]+)#', 1) AS dt,\n  regexp_replace('+91 98765 43210', '[^0-9]', '') AS digits,\n  format_number(2941120.5, 2) AS inr, substring_index('www.tiffingo.in', '.', 2) AS si;", capf('l41_str2.txt')),
     '<code>substr</code> counts from 1: characters 8 to 12 are “o-Tha”. <code>locate</code> returns 0 when the text is not found. <code>regexp_extract</code> returns capture group 1. <code>format_number</code> uses international grouping (2,941,120.50), not lakh-style.'),
    ('Step 4 · Date arithmetic and calendar parts',
     code('sql', 'Beeline', "SELECT date_format('2026-10-04', 'dd-MMM-yyyy EEEE') AS pretty,\n  datediff('2026-10-31', '2026-10-04') AS days_left, date_add('2026-10-04', 30) AS plus30,\n  add_months('2026-01-31', 1) AS am, last_day('2026-02-10') AS ld,\n  next_day('2026-10-04', 'MO') AS nd, trunc('2026-10-04', 'MM') AS month_start,\n  months_between('2026-10-04', '2026-01-04') AS mb, weekofyear('2026-10-04') AS wk,\n  extract(quarter FROM DATE '2026-10-04') AS q, dayofweek('2026-10-04') AS dow;", capf('l41_date.txt')),
     '<code>add_months</code> from 31 January lands on 28 February (the last valid day). <code>next_day</code> gives the next Monday. <code>dayofweek</code> numbers Sunday as 1.'),
    ('Step 5 · Trap: log times shifted by 5½ hours',
     code('sql', 'Beeline', "SELECT ts, unix_timestamp(ts, 'dd/MMM/yyyy:HH:mm:ss Z') AS epoch,\n  from_unixtime(unix_timestamp(ts, 'dd/MMM/yyyy:HH:mm:ss Z'), 'yyyy-MM-dd HH:mm') AS local_time\nFROM access_log LIMIT 3;\n\nSET hive.local.time.zone=Asia/Kolkata;   -- then the same query again",
          capf('l41_unix.txt') + '\n' + capf('l41_tz2.txt')),
     'The epoch number is correct, but <code>from_unixtime</code> prints it in the session zone, which was LOCAL (the server’s UTC). Midnight IST appeared as 18:30 the day before. After setting <code>hive.local.time.zone</code> to Asia/Kolkata the times match the log.'),
    ('Step 6 · Trap: CASE that matches nothing',
     code('sql', 'Beeline', "SELECT status, COUNT(*) AS n,\n  SUM(CASE status WHEN 'delivered' THEN 1 ELSE 0 END) AS exact_match,\n  SUM(CASE lower(status) WHEN 'delivered' THEN 1 ELSE 0 END) AS lower_match\nFROM orders GROUP BY status ORDER BY n DESC;", capf('l41_cond2.txt')),
     'This was the zero in Kabir’s report. The data says DELIVERED, and <code>\'ab\' = \'AB\'</code> is false in Hive (also <code>\'Pune\' LIKE \'pu%\'</code>). Normalise with <code>lower()</code> or <code>upper()</code> on the column before comparing.'),
    ('Step 7 · IF, CASE, NULLIF and NULL handling',
     code('sql', 'Beeline', "SELECT order_id, amount, status, IF(amount >= 500, 'big', 'normal') AS size,\n  CASE WHEN amount < 200 THEN 'low' WHEN amount < 400 THEN 'mid' ELSE 'high' END AS band,\n  CASE status WHEN 'delivered' THEN 1 ELSE 0 END AS ok,\n  nullif(payment, 'COD') AS online_pay\nFROM orders WHERE order_id BETWEEN 100001 AND 100005;\n\nSELECT coalesce(NULL, NULL, 'Thane') AS c, nvl(NULL, 0) AS n, isnull(NULL) AS i,\n  nullif(5, 5) AS nf, NULL + 1 AS plusnull, cast('abc' AS INT) AS badint,\n  cast('12.9' AS INT) AS trunc_int;",
          '\n'.join(l for l in capf('l41_cond.txt').split('\n')) + '\n' + capf('l41_null.txt')),
     'Order 100005 was paid by COD, so <code>nullif</code> turned it into NULL. In the second query, <code>CAST(\'abc\' AS INT)</code> is NULL without any error and <code>CAST(\'12.9\' AS INT)</code> cuts to 12. (The ok column in the first result is 0 for the same case reason as Step 6.)'),
    ('Step 8 · Mask and hash personal data',
     code('sql', 'Beeline', "SELECT name, mask(name) AS m, mask_show_last_n('9876543210', 4) AS phone,\n  mask_first_n('9876543210', 6) AS first6, md5(name) AS md5_hex, sha2(name, 256) AS sha256\nFROM customers WHERE customer_id = 1;", capf('l41_mask.txt')),
     '<code>mask</code> turns capitals into X, small letters into x and digits into n. A hash is the same every time for the same input, so the vendor can still join two files on it without seeing the name.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([("> SELECT upper(name), split(name,' ')[0],", W), ("         lpad(cast(customer_id AS STRING),6,'0')", W), ('| AARAV DESAI | Aarav  | 000001 |', G), ('| ANANYA IYER | Ananya | 000002 |', G), ('| ARJUN NAIR  | Arjun  | 000003 |', G)]),
    term([("> SELECT regexp_extract('ORD#2026-10-04#PUNE',", W), ("         '#([0-9-]+)#', 1);", W), ('| 2026-10-04 |', G)]),
    term([("> SELECT datediff('2026-10-31','2026-10-04'),", W), ("         add_months('2026-01-31', 1);", W), ('| 27 | 2026-02-28 |', G)]),
    term([("> … CASE status WHEN 'delivered' …", W), ('| DELIVERED | 46018 | exact 0 | lower 46018 |', Y)]),
    term([("> SELECT cast('abc' AS INT), concat('Rs ', NULL);", W), ('| NULL | NULL |', RD), ('  no error, no warning', RD)]),
]
def chars(word, hi, y=60, x0=40, w=22, tone='acc'):
    return ''.join(box(x0 + k * w, y, w - 2, 22, tone if k in hi else 'card', rx=3) + t(x0 + k * w + 10, y + 15, ch, 8.4, 'ink', mono=True) for k, ch in enumerate(word))
B1 = [
    t(180, 22, 'split → array, index from 0', 9.4, bold=True) + chars('Aarav Desai', range(0, 5), x0=58) + t(110, 100, '[0] = Aarav', 8.4, 'acc', mono=True) + t(240, 100, '[1] = Desai', 8.4, 'ink2', mono=True) + cap('lpad pads on the left to a fixed width.', "lpad('1', 6, '0') = 000001", 'blue', y=150, h=46),
    t(180, 22, 'regexp_extract: keep capture group 1', 9.4, bold=True) + t(180, 60, 'ORD#2026-10-04#PUNE', 10, 'ink', mono=True) + fill(126, 66, 92, 3, 'green') + t(180, 92, '#( [0-9-]+ )#  → group 1', 8.6, 'green', mono=True) + cap('Group 0 is the whole match, including the # signs.', '', 'green', y=150, h=34),
    t(180, 22, 'Date arithmetic', 9.4, bold=True) + ''.join(fill(20 + k * 10, 60, 8, 20, 'acc' if 3 <= k < 30 else 'grey', rx=1) for k in range(31)) + t(50, 96, '04 Oct', 7.8, 'ink2', mono=True) + t(316, 96, '31 Oct', 7.8, 'ink2', mono=True) + t(180, 118, '27 days between · Jan 31 + 1 month → Feb 28', 8, 'ink', mono=True) + cap('Month ends are clamped to the last valid day.', '', 'blue', y=150, h=34),
    t(180, 22, 'Case-sensitive equality', 9.4, bold=True) + t(110, 62, "'DELIVERED'", 10, 'ink', mono=True) + t(180, 62, '=', 10, 'red', bold=True) + t(250, 62, "'delivered'", 10, 'ink', mono=True) + t(180, 88, 'false', 10, 'red', bold=True, mono=True) + t(180, 116, "lower(status) = 'delivered'  →  true", 8.6, 'green', mono=True) + cap('Normalise case before comparing.', '', 'amber', y=150, h=34),
    t(180, 22, 'Silent NULLs', 9.4, bold=True) + box(30, 48, 300, 70, 'card') + t(180, 68, 'bad CAST · invalid date · NULL in concat', 8.4, 'ink') + t(180, 88, 'unknown pattern · missing JSON key', 8.4, 'ink') + t(180, 108, '→ NULL, query still succeeds', 8.4, 'red', bold=True) + cap('Count NULLs after each transformation.', '', 'amber', y=150, h=34),
]
see_caps = ['String functions clean and build text: upper case, first word, padded code.',
            'regexp_extract pulls a date out of a code string.',
            'Date arithmetic: days between dates and adding a month.',
            'A case-sensitive comparison silently matched nothing.',
            'Bad conversions return NULL without an error.']
behind_caps = ['split makes an array of words; index 0 is the first word.',
               'Brackets in the pattern form capture group 1, which is returned.',
               'datediff counts days; add_months clamps to the last valid day of the month.',
               'Upper-case data never equals a lower-case literal.',
               'Many functions return NULL instead of failing, so check NULL counts.']
two = anim_two('Functions', 'What each function does to the value', 'Real Beeline output', 'How the function transforms the highlighted value', see, B1, see_caps, behind_caps)

# ---- scenario 1: zero delivered
z1 = (t(180, 22, 'Weekly report: delivered orders = 0', 9.4, 'red', bold=True) + t(180, 56, "CASE status WHEN 'delivered' THEN 1 ELSE 0 END", 8.4, 'ink', mono=True) + cap('The dashboard showed 0 delivered orders.', '', 'amber', y=150, h=34))
z2 = term([('> SELECT DISTINCT status FROM orders;', W), ('| DELIVERED |', G), ('| CANCELLED |', G), ('| REFUNDED  |', G)], label='real output · Hive 4.2.1')
z3 = (t(180, 22, 'Fix: normalise the column', 9.6, 'green', bold=True) + t(180, 56, "CASE lower(status) WHEN 'delivered' …", 8.6, 'ink', mono=True) + t(180, 80, 'exact 0  →  lower 46,018', 9, 'green', bold=True, mono=True) + cap('46,018 of 50,000 orders were delivered.', '', 'green', y=150, h=34))
z4 = (t(180, 22, 'Prevent it next time', 9.6, bold=True) + ''.join(t(26, 52 + k * 19, s, 8.4, anchor='start') for k, s in enumerate(['• check DISTINCT values before writing rules', '• standardise case once, in the curated table', '• alert when a metric drops to 0'])) + cap('Look at the data, not at the documentation.', '', 'blue', y=150, h=34))
z5 = (t(180, 22, 'Same trap elsewhere', 9.6, 'acc', bold=True) + t(180, 56, "LIKE 'pu%' misses 'Pune' · 'ab' = 'AB' is false", 8.4, 'ink', mono=True) + t(180, 76, 'joins on city names with mixed case', 8.4, 'ink2') + cap('Hive string comparison is case-sensitive.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'A dashboard showing zero delivered orders',
              'A case mismatch between the data and the query. The numbers are real.',
              'Case mismatch', 'A CASE expression compared upper-case data with a lower-case literal and counted zero; lower() fixed it', [z1, z2, z3, z4, z5],
              ['The rule compared status with a lower-case literal.',
               'The data stores status in capitals.',
               'lower(status) gives the real count: 46,018.',
               'Check distinct values and standardise case early.',
               'The same trap hits LIKE, equality and joins.'],
              hid='scenario-case')

# ---- scenario 2: time zone
c1 = (t(180, 22, 'First visit of October at 18:30 on 30 Sep?', 9.2, bold=True) + t(180, 56, '01/Oct/2026:00:00:00 +0530  →  2026-09-30 18:30', 8.2, 'red', mono=True) + cap('The log says midnight IST.', '', 'amber', y=150, h=34))
c2 = (t(180, 22, 'unix_timestamp is right', 9.6, bold=True) + t(180, 56, '1790793000 seconds since 1970-01-01 UTC', 8.4, 'ink', mono=True) + t(180, 76, '= 2026-09-30 18:30 UTC = 2026-10-01 00:00 IST', 8.2, 'ink2', mono=True) + cap('One instant, two ways to print it.', '', 'blue', y=150, h=34))
c3 = (t(180, 22, 'from_unixtime prints in the session zone', 9.2, bold=True) + t(180, 56, 'hive.local.time.zone=LOCAL → server JVM → UTC', 8.4, 'ink', mono=True) + cap('Cloud servers usually run in UTC.', '', 'blue', y=150, h=34))
c4 = term([('> SET hive.local.time.zone=Asia/Kolkata;', W), ('| 01/Oct/2026:00:00:00 +0530 | 2026-10-01 00:00 |', G), ('| 01/Oct/2026:00:00:37 +0530 | 2026-10-01 00:00 |', G)], label='real output · Hive 4.2.1')
c5 = (t(180, 22, 'Team rule', 9.6, 'acc', bold=True) + ''.join(t(26, 52 + k * 19, s, 8.4, anchor='start') for k, s in enumerate(['• store event time in UTC (or epoch)', '• convert for reports with from_utc_timestamp', '• set the session zone explicitly in jobs'])) + cap('Wrong dates move orders across days and months.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Log times 5½ hours early',
              'A web log in IST, parsed on a UTC server. Outputs are real.',
              'Time zones', 'A timestamp parsed correctly was printed in the server time zone, 5.5 hours earlier; setting hive.local.time.zone fixed it', [c1, c2, c3, c4, c5],
              ['Midnight IST appeared as 18:30 the previous day.',
               'The epoch value itself is correct.',
               'from_unixtime formats in the session time zone, here UTC.',
               'Setting hive.local.time.zone to Asia/Kolkata prints the right time.',
               'Store UTC and convert deliberately for reports.'],
              hid='scenario-timezone')

# ---- scenario 3: masking for a vendor
m1 = (t(180, 22, 'Sharing customers with an SMS vendor', 9.4, bold=True) + t(180, 56, 'they need: city, plan, a stable id', 8.4, 'ink') + t(180, 76, 'they must not see: name, full phone', 8.4, 'red') + cap('Share the minimum.', '', 'blue', y=150, h=34))
m2 = term([("> SELECT mask(name), mask_show_last_n(phone, 4)", W), ('| Xxxxx Xxxxx | nnnnnn3210 |', G)], label='real output · Hive 4.2.1')
m3 = (t(180, 22, 'Stable id without the name', 9.6, bold=True) + t(180, 56, "sha2(concat(customer_id, 'secret-salt'), 256)", 8.4, 'ink', mono=True) + cap('Same customer → same hash in every file.', 'A secret salt stops guessing by brute force.', 'green', y=150, h=46))
m4 = (t(180, 22, 'md5 alone is not enough', 9.6, 'red', bold=True) + t(180, 56, 'only 2,000 customer ids → easy to hash all and match', 8.2, 'ink2') + cap('Hashing is not encryption.', '', 'amber', y=150, h=34))
m5 = (t(180, 22, 'In production', 9.6, 'acc', bold=True) + t(180, 56, 'column masking policies in Apache Ranger (Module 10)', 8.4, 'ink2') + cap('Mask at the source, not in every query.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Masked and hashed data for an outside vendor',
              'Personal data must be minimised before it leaves the company. Masking output is real; the salt pattern is a recommendation.',
              'Data masking', 'Names and phones are masked, and a salted hash gives the vendor a stable id without revealing identity', [m1, m2, m3, m4, m5],
              ['The vendor needs only some columns.',
               'mask and mask_show_last_n hide names and phones.',
               'A salted sha2 hash gives a stable id.',
               'Plain md5 of a small id range can be reversed by guessing.',
               'Ranger policies apply masking centrally.'],
              hid='scenario-masking')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Functions transforming values</h2>
  <p>Left: real Beeline output. Right: what the function did to the value.</p>
''' + two + '''
  <p>Three live scenarios follow: a case mismatch, a time-zone shift and masking data for a vendor.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Built-in functions at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'trim / lower', 8.6, 'green', bold=True, mono=True) + t(60, 58, 'standardise', 7.4, 'ink2'),
    '1. Standardising raw data',
    'Curated tables are built with trim, lower/upper and regexp_replace so that city names, statuses and phone numbers match across sources.',
    ['Raw table', '*Clean functions', 'Curated table']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'date_format', 8.6, 'blue', bold=True, mono=True) + t(60, 58, 'calendar keys', 7.4, 'ink2'),
    '2. Calendar reporting',
    'Week, month and quarter keys (weekofyear, trunc, extract) drive weekly sales reviews and month-on-month comparisons.',
    ['Order date', '*Calendar parts', 'GROUP BY week']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'regexp', 10, 'violet', bold=True, mono=True) + t(60, 58, 'parse logs', 7.4, 'ink2'),
    '3. Parsing logs and codes',
    'regexp_extract and unix_timestamp turn web and app logs into columns: time, page, response code, campaign id.',
    ['Log line', '*regexp + time', 'Columns']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'CASE', 10, 'acc', bold=True, mono=True) + t(60, 58, 'business rules', 7.4, 'ink2'),
    '4. Business rules and bands',
    'Order-size bands, customer tiers and SLA flags are written as CASE expressions in shared views so every report uses the same rule.',
    ['Measures', '*CASE / IF', 'Segments']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'mask / sha2', 8.6, 'acc', bold=True, mono=True) + t(60, 58, 'privacy', 7.4, 'ink2'),
    '5. Privacy-safe data sharing',
    'Banks, telecoms and food apps mask phones and hash ids before sharing data with partners, as data-protection rules such as India’s DPDP Act expect.',
    ['Customer table', '*Mask + hash', 'Partner extract']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> you need SELECT and WHERE (<a href="../../03-querying/01-select-where-and-functions/">3.1</a>) and data types (<a href="../../02-hiveql/03-data-types/">2.3</a>).</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
