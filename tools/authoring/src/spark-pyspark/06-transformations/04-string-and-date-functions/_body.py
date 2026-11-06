import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
C = 'l64_strdate.txt'
def sec(a, b=None, drop=()):
    s = capsec(C, a, b, drop)
    return '\n'.join(l if len(l) <= 140 else l[:137] + ' …' for l in s.split('\n'))

def chip_row(x, y, items, w=96):
    o = ''
    for k, (a, b, tone) in enumerate(items):
        o += opbox(x, y + k * 30, a, '', 'card', w, 24) + arrow(x + w, y + k * 30 + 12, x + w + 30, y + k * 30 + 12, 'ink3', 1.0) + opbox(x + w + 34, y + k * 30, b, '', tone, w + 20, 24)
    return o

# ---------------------------------------------------------------- story
sc_ = (chip_row(14, 24, [('"  Ravi KUMAR "', 'Ravi Kumar', 'green'), ('"+91 98200-11122"', '9820011122', 'green'), ('"04/11/2026"', '2026-11-04', 'green'), ('"YYYY"', 'error', 'acc')], 110) +
       box(400, 12, 232, 132, 'card') + t(516, 30, 'Measured', 8.6, bold=True) +
       ''.join(t(412, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
           ('to_date("04/11/2026"): error', 'red'), ('try_to_date + coalesce: ok', 'green'),
           ('2026-02-30 -> NULL', 'amber'), ('"YYYY" pattern: rejected', 'red'),
           ('2027-01-01 is ISO week 53', 'amber'), ('same epoch, 15:30 IST / 10:00 UTC', 'ink')])))
scene_svg = scene('Most cleaning work is text and dates: trimming names, extracting PIN codes, normalising phone numbers, parsing dates in several formats and handling time zones. We cleaned real-looking TiffinGo sign-ups and tested the classic date traps.', sc_,
                  'Prefer <tspan font-weight="700" class="s-acc">built-in functions</tspan>; parse dates with <tspan font-weight="700" class="s-acc">try_</tspan> and explicit formats.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“The new year started on 28 December”</h2>
  <div class="story">
    <p class="narration">A year-end report at TiffinGo grouped orders by <code>date_format(order_date, "YYYY")</code>. In an older system that produced “2027” for orders on 28–31 December 2026, and the yearly totals were wrong. In Spark 4 the same pattern stops the job with an error. Meanwhile the support team found phone numbers like “+91 98200-11122” that matched nothing.</p>

{scene_svg}

K> Sir, YYYY and yyyy look the same to me.
A> They are not. <code>yyyy</code> is the calendar year; <code>YYYY</code> is the <b>week-based year</b>, which can differ in the last days of December. Spark 3+ refuses <code>YYYY</code> in formatting to protect you.
R> And the phone numbers?
A> Text needs normalising before you compare or join on it. Today: trimming and case, regular expressions to extract and clean, parsing dates in several formats with <code>try_to_date</code>, date arithmetic, week-year traps and time zones. All outputs are real (PySpark 4.3.0).
  </div>
</section>
'''

lv = '''
LEVELS> String and date functions at three levels
L1> Filling a form neatly
      <ul>
        <li>Names written in random capitals, phone numbers with spaces and dashes, dates written in different ways: before filing, you rewrite them in one standard form.</li>
        <li>A date written 04/11/2026 could be 4 November or 11 April; you need to know the format.</li>
        <li>3:30 pm in India is 10:00 in London: the same moment, different clock readings.</li>
      </ul>
L2> The API
      <ul>
        <li>Text: <code>trim</code>, <code>lower</code>/<code>upper</code>/<code>initcap</code>, <code>regexp_replace</code>, <code>regexp_extract</code>, <code>split</code>, <code>split_part</code>, <code>substring_index</code>, <code>concat_ws</code>, <code>like</code>/<code>ilike</code>/<code>rlike</code>.</li>
        <li>Dates: <code>to_date</code>/<code>try_to_date(col, fmt)</code>, <code>to_timestamp</code>, <code>date_format</code>, <code>datediff</code>, <code>date_add</code>, <code>add_months</code>, <code>last_day</code>, <code>date_trunc</code>, <code>dayofweek</code>, <code>weekofyear</code>.</li>
        <li>Time zones: <code>spark.sql.session.timeZone</code>, <code>to_utc_timestamp</code>, <code>from_utc_timestamp</code>.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li><code>to_date("04/11/2026")</code> failed under ANSI; <code>coalesce(try_to_date(s), try_to_date(s, "dd/MM/yyyy"))</code> parsed both formats and gave null for 2026-02-30.</li>
        <li><code>"YYYY"</code> raised INCONSISTENT_BEHAVIOR_CROSS_VERSION; 1 January 2027 is ISO week 53 of 2026.</li>
        <li>The session time zone (default from the JVM: Asia/Calcutta) changed how the same instant is displayed: 15:30 vs 10:00.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>String and datetime functions</h2>
''' + def_block(
    '<code>pyspark.sql.functions</code> provides built-in, JVM-executed functions for strings (case, trimming, padding, substring, splitting, concatenation, regular expressions via Java regex syntax) and for datetimes. Dates (<code>DATE</code>) have no time zone; timestamps (<code>TIMESTAMP</code>, i.e. TIMESTAMP_LTZ) store an instant and are displayed in the session time zone <code>spark.sql.session.timeZone</code>, which defaults to the JVM time zone; <code>TIMESTAMP_NTZ</code> stores a wall-clock time without zone. Parsing and formatting use datetime patterns (e.g. <code>yyyy-MM-dd HH:mm:ss</code>); since Spark 3.0 the patterns follow java.time and some ambiguous letters such as week-based year <code>Y</code> are rejected for formatting. Under ANSI mode, <code>to_date</code>/<code>to_timestamp</code> raise errors on invalid input, while <code>try_to_date</code>/<code>try_to_timestamp</code> return null.',
    'Spark has ready-made functions to clean text and work with dates. They run fast inside Spark, unlike your own Python code. Always parse dates with a known format, use try_ versions for messy data, and be clear about time zones.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('regexp_extract', 'Take the part of a string that matches a group.'),
    ('regexp_replace', 'Replace everything that matches a pattern.'),
    ('split_part', 'The n-th piece after splitting (Spark 3.5+).'),
    ('try_to_date', 'Parse a date, null if invalid.'),
    ('date_trunc', 'Round a timestamp down to week, month…'),
    ('Week-based year (Y)', 'The ISO year a week belongs to.'),
    ('Session time zone', 'How timestamps are shown and parsed.'),
    ('Epoch', 'Seconds since 1970-01-01 UTC.'),
]) + '''

  <h3>Datetime pattern letters that bite</h3>
''' + table(['Pattern', 'Means', 'Not to be confused with'], [
    ['<code>yyyy</code>', 'calendar year', '<code>YYYY</code> week-based year (rejected for formatting)'],
    ['<code>MM</code>', 'month', '<code>mm</code> minutes'],
    ['<code>dd</code>', 'day of month', '<code>DD</code> day of year'],
    ['<code>HH</code>', 'hour 0–23', '<code>hh</code> hour 1–12 (needs <code>a</code> for AM/PM)'],
    ['<code>EEE</code> / <code>MMM</code>', 'Thu / Nov', '<code>E</code>, <code>MMMM</code> (full names)'],
], minw=600) + lv + '''
EXAM> “How do you parse dates arriving in several formats?” Read the column as a string and use <code>coalesce(try_to_date(c, fmt1), try_to_date(c, fmt2), …)</code>; values that match no format become null and can be counted and quarantined. Under ANSI mode <code>to_date</code> would fail the whole job on the first unexpected value.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Three time types</h2>
''' + table(['Type', 'Stores', 'Shown as', 'Use for'], [
    ['<code>DATE</code>', 'a calendar day', 'the same everywhere', 'order date, birthday'],
    ['<code>TIMESTAMP</code> (LTZ)', 'an instant (UTC internally)', 'in the session time zone', 'events, logs'],
    ['<code>TIMESTAMP_NTZ</code>', 'a wall-clock time, no zone', 'exactly as stored', 'local opening hours, schedules'],
], minw=620) + '''
WARN> The session time zone defaults to the JVM’s, so the same code can print different timestamps on a laptop in India and a cluster in UTC. Set <code>spark.sql.session.timeZone</code> explicitly (often <code>UTC</code>) in every job, store instants in UTC, and convert for display at the edge.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Cleaning sign-ups and taming dates</h2>
  <p>All outputs are real: PySpark 4.3.0, local mode, ANSI mode on (the default).</p>
''' + stepper([
    ('Step 1 · Cleaning text',
     code('python', 'l64_strdate.py', 'r.select(F.initcap(F.trim("name")).alias("name"), F.lower("email").alias("email"),\n         F.regexp_replace("phone", r"[^0-9]", "").alias("digits"),\n         F.right(F.regexp_replace("phone", r"[^0-9]", ""), F.lit(10)).alias("phone10"))', sec('== 1)', '== 2)')),
     '<code>trim</code> + <code>initcap</code> fixed “  Ravi KUMAR ”; <code>lower</code> made emails comparable. Removing every non-digit left <code>919820011122</code> for the number with a country code, so we keep the last 10 digits: now both phones match the format used elsewhere and can be joined on.'),
    ('Step 2 · Extracting parts',
     code('python', 'l64_strdate.py', 'r.select(F.split("address", ",")[0].alias("city"), F.regexp_extract("address", r"(\\d{6})", 1).alias("pin"),\n         F.split_part("ref", F.lit("-"), F.lit(3)).cast("int").alias("ref_no"),\n         F.substring_index("email", "@", -1).alias("domain"), F.concat_ws(" / ", "name", "ref").alias("label"))', sec('== 2)', '== 3)')),
     '<code>split</code> gave an array (index 0 = city), <code>regexp_extract</code> found the 6-digit PIN anywhere in the address, <code>split_part</code> took the third piece of the reference and <code>cast</code> removed leading zeros. Note the uncleaned name and mixed-case domain: clean first, extract after.'),
    ('Step 3 · Parsing dates safely',
     code('python', 'l64_strdate.py', 'd.select("s", F.try_to_date("s").alias("iso"), F.try_to_date("s", "dd/MM/yyyy").alias("dmy"),\n         F.coalesce(F.try_to_date("s"), F.try_to_date("s", "dd/MM/yyyy")).alias("either"))\nd.select(F.to_date("s")).collect()', sec('== 3)', '== 4)')),
     'Each <code>try_to_date</code> recognised one format and returned null for the others; <code>coalesce</code> combined them. 30 February is not a date in any format and stayed null: count such rows. The strict <code>to_date</code> stopped the job at the first non-ISO value, as ANSI mode should.'),
    ('Step 4 · Date arithmetic',
     code('python', 'l64_strdate.py', 't.select(F.datediff("today", "ts"), F.date_add("today", 30), F.add_months("today", 1), F.last_day("today"),\n         F.date_trunc("week", "ts"), F.dayofweek("ts"), F.date_format("ts", "EEE, d MMM HH:mm"))', sec('== 4)', '== 5)')),
     'Six days since the order; 30 days and one month later happen to give the same date here, but not in general. <code>date_trunc("week")</code> rounded down to Monday 26 October; <code>dayofweek</code> counts Sunday as 1, so Thursday is 5. <code>date_format</code> made a readable label.'),
    ('Step 5 · YYYY vs yyyy, and ISO weeks',
     code('python', 'l64_strdate.py', 'y.select("d", F.date_format("d", "yyyy"))\ny.select(F.date_format("d", "YYYY"))\ny.select("d", F.year("d"), F.weekofyear("d"))', sec('== 5)', '== 6)')),
     '<code>yyyy</code> is the calendar year. <code>YYYY</code> was rejected with INCONSISTENT_BEHAVIOR_CROSS_VERSION, because week-based years silently gave wrong years in older systems. The ISO week column shows why: 28 December 2026 to 1 January 2027 all belong to <b>week 53 of 2026</b>. Weekly reports that use <code>weekofyear</code> must pair it with the ISO week year, not <code>year()</code>.'),
    ('Step 6 · Time zones and patterns',
     code('python', 'l64_strdate.py', 'spark.conf.get("spark.sql.session.timeZone")\nz.select("ts", F.unix_timestamp("ts"), F.to_utc_timestamp("ts", "Asia/Kolkata"), …)\nspark.conf.set("spark.sql.session.timeZone", "UTC"); z.select(F.col("ts").cast("string"))\no.where(F.col("name").startswith("A")); .like("A%"); .rlike("^(Aarav|Ananya) "); .ilike("%iyer")', sec('== 6)')),
     'The session zone came from the JVM: <code>Asia/Calcutta</code> (the old name again, Lesson 5.4). The stored instant (epoch 1793786400) never changed; switching the session to UTC changed only how it is <b>displayed</b>: 15:30 became 10:00. Finally, <code>like</code>, <code>ilike</code> (case-insensitive) and <code>rlike</code> (regex) filter text without any Python.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('"  Ravi KUMAR " -> Ravi Kumar', G), ('"+91 98200-11122" -> 9820011122', G)], size=7.4),
    term([('city Pune, pin 411001', W), ('ref_no 781, domain Mail.in', W)], size=7.6),
    term([('to_date("04/11/2026"): error', RD), ('coalesce(try_to_date…): 2026-11-04', G), ('2026-02-30 -> NULL', Y)], size=7.2),
    term([('"YYYY": INCONSISTENT_BEHAVIOR…', RD), ('2027-01-01: year 2027, week 53', Y)], size=7.4),
    term([('epoch 1793786400 (same)', W), ('IST : 2026-11-04 15:30:00', G), ('UTC : 2026-11-04 10:00:00', G)], size=7.4),
]
B1 = [
    t(180, 14, 'Normalise before comparing', 9.4, bold=True) + chip_row(30, 40, [('"+91 98200-11122"', '919820011122', 'card'), ('919820011122', '9820011122', 'green')], 120) + cap('regexp_replace, then right(…, 10).', '', 'green', y=144, h=30),
    t(180, 14, 'Pull fields out of text', 9.4, bold=True) + chip_row(30, 34, [('"Pune, MH 411001"', 'Pune | 411001', 'green'), ('"TG-2026-000781"', '781', 'green')], 120) + cap('split, regexp_extract, split_part.', '', 'blue', y=144, h=30),
    t(180, 14, 'Try each known format', 9.4, bold=True) + chip_row(30, 30, [('"2026-11-04"', 'ISO ✓', 'green'), ('"04/11/2026"', 'dd/MM/yyyy ✓', 'green'), ('"2026-02-30"', 'NULL', 'acc')], 120) + cap('Unparsed values become countable nulls.', '', 'green', y=144, h=30),
    t(180, 14, 'Calendar year vs week year', 9.4, bold=True) + chip_row(30, 40, [('2026-12-31', 'yyyy 2026', 'green'), ('2027-01-01', 'ISO week 53 of 2026', 'amber')], 120) + cap('Use yyyy; pair weeks with week-year.', '', 'red', y=144, h=30),
    t(180, 14, 'One instant, many clocks', 9.4, bold=True) + opbox(20, 56, 'epoch 1793786400', 'stored instant', 'violet', 130, 30) + ''.join(arrow(150, 71, 210, 50 + k * 40, 'ink3', 1.0) + opbox(214, 36 + k * 40, ['15:30 IST', '10:00 UTC'][k], '', 'green', 110, 26) for k in range(2)) + cap('Set the session time zone.', '', 'blue', y=144, h=30),
]
see_caps = ['Names and phones normalised.', 'City, PIN and number extracted.', 'Two formats parsed, one invalid.', 'YYYY rejected; week 53 crosses years.', 'Same instant, two displays.']
behind_caps = ['Built-in functions run in the JVM.', 'Regex groups and splits.', 'try_ returns null instead of failing.', 'java.time week rules.', 'Timestamps are UTC instants.']
two = anim_two('String and date functions', 'Clean text, correct time', 'Real lab outputs', 'What each function does', see, B1, see_caps, behind_caps)

# ---- scenario 1: phone join
e1 = (t(180, 22, 'Match support tickets to customers', 9.4, bold=True) + t(180, 56, 'join on phone', 8.4, 'ink2') + cap('Half do not match.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Formats differ', 9.4, bold=True) + t(180, 56, '+91 98200-11122 vs 9820011122', 8.4, 'ink', mono=True) + cap('Same person.', '', 'amber', y=150, h=34))
e3 = (t(180, 22, 'Normalise both sides', 9.4, bold=True) + t(180, 56, 'right(regexp_replace(p, "[^0-9]", ""), 10)', 7.8, 'ink', mono=True) + cap('Our Step 1.', '', 'green', y=150, h=34))
e4 = (t(180, 22, 'Store the clean key', 9.4, bold=True) + t(180, 56, 'phone10 column in the table', 8.4, 'ink2') + cap('Compute once.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Same for emails', 9.4, 'acc', bold=True) + t(180, 56, 'lower(trim(email))', 8.4, 'ink', mono=True) + cap('Case and spaces.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Same customer, no match',
              'Normalising join keys. (Typical; functions from our lab.)',
              'Key normalisation', 'Text keys must be normalised the same way on both sides before joining', [e1, e2, e3, e4, e5],
              ['Join fails.', 'Formats.', 'Normalise.', 'Store.', 'Emails too.'],
              hid='scenario-phone')

# ---- scenario 2: year-end report
b1 = (t(180, 22, 'Yearly totals with YYYY', 9.4, bold=True) + t(180, 56, 'date_format(d, "YYYY") in an old job', 8.2, 'ink', mono=True) + cap('Worked all year.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, '28–31 December', 9.4, bold=True) + t(180, 56, 'counted in next year', 8.4, 'ink2') + cap('Week-based year.', '', 'red', y=150, h=34))
b3 = (t(180, 22, 'Spark 3+ rejects it', 9.4, bold=True) + t(180, 56, 'INCONSISTENT_BEHAVIOR_CROSS_VERSION', 7.8, 'ink', mono=True) + cap('Our Step 5.', '', 'amber', y=150, h=34))
b4 = (t(180, 22, 'Use year() or yyyy', 9.4, bold=True) + t(180, 56, 'F.year("order_date")', 8.4, 'ink', mono=True) + cap('Calendar year.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Weekly reports', 9.4, 'acc', bold=True) + t(180, 56, 'ISO week + ISO week-year together', 8.4, 'ink2') + cap('Never week + calendar year.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'A year that began in December',
              'Datetime patterns. (Behaviour from our lab.)',
              'YYYY vs yyyy', 'YYYY is the week-based year; Spark rejects it for formatting, use yyyy or year()', [b1, b2, b3, b4, b5],
              ['YYYY.', 'Wrong year.', 'Rejected.', 'yyyy.', 'ISO weeks.'],
              hid='scenario-yyyy')

# ---- scenario 3: time zone drift
u1 = (t(180, 22, 'Hourly orders report', 9.4, bold=True) + t(180, 56, 'hour(order_ts)', 8.4, 'ink', mono=True) + cap('Runs on laptops and cluster.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'Peak hour differs', 9.4, bold=True) + t(180, 56, 'laptop: 20:00, cluster: 14:30', 8.4, 'ink2') + cap('Session zones differ.', '', 'amber', y=150, h=34))
u3 = (t(180, 22, 'Default = JVM time zone', 9.4, bold=True) + t(180, 56, 'Asia/Calcutta vs UTC', 8.4, 'ink', mono=True) + cap('Our Step 6.', '', 'red', y=150, h=34))
u4 = (t(180, 22, 'Set it in every job', 9.4, bold=True) + t(180, 56, 'spark.sql.session.timeZone=Asia/Kolkata', 7.8, 'ink', mono=True) + cap('Or UTC, consistently.', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'Store UTC, show local', 9.4, 'acc', bold=True) + t(180, 56, 'convert in the report layer', 8.4, 'ink2') + cap('Same answer everywhere.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'The peak hour moved',
              'Session time zones. (Behaviour from our lab.)',
              'Session time zone', 'Timestamps are displayed and extracted in the session time zone; set it explicitly in every job', [u1, u2, u3, u4, u5],
              ['Report.', 'Different hour.', 'JVM default.', 'Set it.', 'UTC storage.'],
              hid='scenario-tz')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Clean text, correct time</h2>
  <p>Left: real outputs. Right: what each function does.</p>
''' + two + '''
  <p>Three live scenarios follow: phone numbers that did not match, a year that began in December, and a peak hour that moved.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Text and dates at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'KYC', 12, 'blue', bold=True) + t(60, 58, 'cleaning', 7.4, 'ink2'),
    '1. Customer data cleaning',
    'Names, emails, phones and PIN codes are normalised before deduplication and matching.',
    ['Raw sign-ups', '*trim / regex', 'Clean keys']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'logs', 12, 'green', bold=True) + t(60, 58, 'parsing', 7.4, 'ink2'),
    '2. Log parsing',
    'regexp_extract pulls status codes, paths and latencies out of web server logs.',
    ['Log lines', '*regexp_extract', 'Columns']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'calendar', 10, 'violet', bold=True) + t(60, 58, 'reports', 7.4, 'ink2'),
    '3. Calendar reporting',
    'Week, month and fiscal-year buckets with date_trunc, last_day and add_months.',
    ['Timestamps', '*date_trunc', 'Periods']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'SLA', 12, 'acc', bold=True) + t(60, 58, 'durations', 7.4, 'ink2'),
    '4. Delivery SLAs',
    'Minutes between order and delivery from unix_timestamp differences.',
    ['Two timestamps', '*difference', 'SLA breaches']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'global', 11, 'acc', bold=True) + t(60, 58, 'time zones', 7.4, 'ink2'),
    '5. Multi-country data',
    'Events stored in UTC are converted to each country’s local time for local reports.',
    ['UTC events', '*from_utc_timestamp', 'Local hours']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> columns and try_cast in <a href="../../04-dataframes/03-working-with-columns/">4.3</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
